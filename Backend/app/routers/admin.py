import os
import pyodbc
import re
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..audit import write_audit_log
from ..config import BACKUP_DIR, DB_NAME, DB_SERVER, ODBC_DRIVER
from ..database import engine, get_db
from ..deps import require_roles
from ..models import AIConfig, AuditLog, LibraryConfig
from ..schemas import (
    AIConfigOut,
    AIConfigUpdate,
    AuditLogOut,
    BackupOut,
    LibraryConfigOut,
    LibraryConfigUpdate,
    RestoreRequest,
)
router = APIRouter(prefix="/api/admin", tags=["admin"])


def _mask_api_key(key: str) -> str:
    if not key:
        return ""
    if len(key) <= 8:
        return "*" * len(key)
    return key[:4] + "*" * (len(key) - 8) + key[-4:]


def _ai_config_out(cfg: AIConfig) -> AIConfigOut:
    return AIConfigOut(
        provider=cfg.provider,
        model=cfg.model,
        api_key_masked=_mask_api_key(cfg.api_key),
        has_api_key=bool(cfg.api_key),
        prompt_template=cfg.prompt_template,
    )


@router.get("/config/library", response_model=LibraryConfigOut)
def get_library_config(
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "librarian")),
) -> LibraryConfigOut:
    cfg = db.get(LibraryConfig, 1)
    if cfg is None:
        raise HTTPException(status_code=404, detail="Chưa có cấu hình thư viện.")
    return cfg


@router.put("/config/library", response_model=LibraryConfigOut)
def update_library_config(
    body: LibraryConfigUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> LibraryConfigOut:
    cfg = db.get(LibraryConfig, 1)
    if cfg is None:
        raise HTTPException(status_code=404, detail="Chưa có cấu hình thư viện.")
    cfg.max_borrow_days = body.max_borrow_days
    cfg.overdue_fine_per_day = body.overdue_fine_per_day
    cfg.max_books_at_once = body.max_books_at_once
    write_audit_log(
        db,
        user,
        "UPDATE_LIBRARY_CONFIG",
        "CONFIG",
        entity_id="1",
        details=body.model_dump_json(),
    )
    db.commit()
    db.refresh(cfg)
    return cfg


@router.get("/config/ai", response_model=AIConfigOut)
def get_ai_config(
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> AIConfigOut:
    cfg = db.get(AIConfig, 1)
    if cfg is None:
        raise HTTPException(status_code=404, detail="Chưa có cấu hình AI.")
    return _ai_config_out(cfg)


@router.put("/config/ai", response_model=AIConfigOut)
def update_ai_config(
    body: AIConfigUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> AIConfigOut:
    cfg = db.get(AIConfig, 1)
    if cfg is None:
        raise HTTPException(status_code=404, detail="Chưa có cấu hình AI.")
    data = body.model_dump(exclude_unset=True)
    if "api_key" in data:
        cfg.api_key = data["api_key"]
    for field in ("provider", "model", "prompt_template"):
        if field in data:
            setattr(cfg, field, data[field])
    write_audit_log(
        db,
        user,
        "UPDATE_AI_CONFIG",
        "CONFIG",
        entity_id="1",
        details=",".join(data.keys()),
    )
    db.commit()
    db.refresh(cfg)
    return _ai_config_out(cfg)


@router.get("/audit-logs", response_model=list[AuditLogOut])
def list_audit_logs(
    limit: int = Query(100, ge=1, le=500),
    action: str | None = Query(None, max_length=50),
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> list[AuditLogOut]:
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    return query.order_by(AuditLog.id.desc()).limit(limit).all()


@router.post("/backup", response_model=BackupOut)
def backup_database(
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> BackupOut:
    if not re.fullmatch(r"[A-Za-z0-9_]+", DB_NAME):
        raise HTTPException(status_code=500, detail="Tên database cấu hình không hợp lệ.")
    backup_dir = BACKUP_DIR
    if not backup_dir:
        with engine.connect() as conn:
            backup_dir = conn.execute(
                text("SELECT CAST(SERVERPROPERTY('InstanceDefaultBackupPath') AS NVARCHAR(500))")
            ).scalar()
    if not backup_dir:
        raise HTTPException(status_code=500, detail="Không xác định được thư mục backup.")
    os.makedirs(backup_dir, exist_ok=True)
    filename = f"{DB_NAME}_{datetime.now():%Y%m%d_%H%M%S}.bak"
    path = os.path.join(backup_dir, filename)
    path_sql = path.replace("'", "''")
    conn = None
    try:
        conn = pyodbc.connect(
            f"DRIVER={{{ODBC_DRIVER}}};SERVER={DB_SERVER};DATABASE={DB_NAME};"
            "Trusted_Connection=Yes;TrustServerCertificate=Yes",
            autocommit=True,
        )
        cursor = conn.cursor()
        cursor.execute(f"BACKUP DATABASE [{DB_NAME}] TO DISK = N'{path_sql}'")
        while cursor.nextset():
            pass
        cursor.close()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Sao lưu CSDL thất bại: {exc}",
        )
    finally:
        if conn is not None:
            conn.close()
    write_audit_log(
        db,
        user,
        "BACKUP_DATABASE",
        "DATABASE",
        entity_id=filename,
        details=path,
    )
    db.commit()
    return BackupOut(message="Đã sao lưu cơ sở dữ liệu.", path=path)


@router.post("/restore")
def restore_database(
    body: RestoreRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
):
    path = body.file_path
    if not os.path.isfile(path) or not path.lower().endswith(".bak"):
        raise HTTPException(
            status_code=404,
            detail="File backup không tồn tại hoặc không phải .bak.",
        )
    if not re.fullmatch(r"[A-Za-z0-9_]+", DB_NAME):
        raise HTTPException(status_code=500, detail="Tên database cấu hình không hợp lệ.")

    path_sql = path.replace("'", "''")
    write_audit_log(
        db,
        user,
        "RESTORE_DATABASE",
        "DATABASE",
        entity_id=os.path.basename(path),
        details=path,
    )
    db.commit()

    conn = None
    try:
        conn = pyodbc.connect(
            f"DRIVER={{{ODBC_DRIVER}}};SERVER={DB_SERVER};DATABASE=master;"
            "Trusted_Connection=Yes;TrustServerCertificate=Yes",
            autocommit=True,
        )
        cursor = conn.cursor()
        cursor.execute(f"ALTER DATABASE [{DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
        while cursor.nextset():
            pass
        cursor.execute(f"RESTORE DATABASE [{DB_NAME}] FROM DISK = N'{path_sql}' WITH REPLACE")
        while cursor.nextset():
            pass
        cursor.execute(f"ALTER DATABASE [{DB_NAME}] SET MULTI_USER")
        while cursor.nextset():
            pass
        cursor.close()
    except Exception as exc:
        try:
            if conn is not None:
                cursor = conn.cursor()
                cursor.execute(f"ALTER DATABASE [{DB_NAME}] SET MULTI_USER")
                while cursor.nextset():
                    pass
                cursor.close()
        except Exception:
            pass
        raise HTTPException(
            status_code=500,
            detail=f"Phục hồi CSDL thất bại: {exc}",
        )
    finally:
        if conn is not None:
            conn.close()
    return {"message": "Đã phục hồi CSDL từ file backup.", "path": path}
