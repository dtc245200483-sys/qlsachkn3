from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..audit import write_audit_log
from ..database import get_db
from ..deps import require_roles
from ..models import Reader, User
from ..schemas import LockReaderRequest, ReaderCreate, ReaderOut, ReaderUpdate

router = APIRouter(prefix="/api/readers", tags=["readers"])


@router.get("", response_model=list[ReaderOut])
def list_readers(
    q: str | None = Query(None, max_length=255),
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "librarian")),
) -> list[ReaderOut]:
    query = db.query(Reader)
    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(
                Reader.ma.like(pattern),
                Reader.hoTen.like(pattern),
            )
        )
    return query.order_by(Reader.ma.asc()).all()


@router.post("", response_model=ReaderOut)
def create_reader(
    body: ReaderCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> ReaderOut:
    if db.get(Reader, body.ma) is not None:
        raise HTTPException(status_code=409, detail="Mã độc giả đã tồn tại.")
    if db.query(Reader).filter(Reader.email == body.email).first() is not None:
        raise HTTPException(status_code=409, detail="Email đã được sử dụng.")
    reader = Reader(**body.model_dump())
    db.add(reader)
    write_audit_log(
        db,
        user,
        "CREATE_READER",
        "READER",
        entity_id=body.ma,
        details=f"hoTen={body.hoTen}",
    )
    db.commit()
    db.refresh(reader)
    return reader


@router.put("/{ma}", response_model=ReaderOut)
def update_reader(
    ma: str,
    body: ReaderUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> ReaderOut:
    reader = db.get(Reader, ma)
    if reader is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy độc giả.")
    data = body.model_dump(exclude_unset=True)
    if "email" in data:
        duplicate_email = (
            db.query(Reader)
            .filter(Reader.email == data["email"], Reader.ma != ma)
            .first()
        )
        if duplicate_email is not None:
            raise HTTPException(status_code=409, detail="Email đã được sử dụng.")
    for field, value in data.items():
        setattr(reader, field, value)
    if "trangThaiThe" in data:
        linked = db.query(User).filter(User.reader_id == ma).first()
        if linked is not None:
            linked.is_active = data["trangThaiThe"] == "hoat_dong"
    write_audit_log(
        db,
        user,
        "UPDATE_READER",
        "READER",
        entity_id=ma,
        details=f"changed={','.join(data.keys())}",
    )
    db.commit()
    db.refresh(reader)
    return reader


@router.put("/{ma}/lock", response_model=ReaderOut)
def lock_reader(
    ma: str,
    body: LockReaderRequest,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "librarian")),
) -> ReaderOut:
    reader = db.get(Reader, ma)
    if reader is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy độc giả.")
    reader.trangThaiThe = body.trangThaiThe
    linked = db.query(User).filter(User.reader_id == ma).first()
    if linked is not None:
        linked.is_active = body.trangThaiThe == "hoat_dong"
    write_audit_log(
        db,
        user,
        "UPDATE_READER_STATUS",
        "READER",
        entity_id=ma,
        details=(
            f"trangThaiThe={body.trangThaiThe}; "
            f"account_locked={linked is not None and body.trangThaiThe == 'khoa'}"
        ),
    )
    db.commit()
    db.refresh(reader)
    return reader


@router.delete("/{ma}")
def delete_reader(
    ma: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
):
    reader = db.get(Reader, ma)
    if reader is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy độc giả.")
    write_audit_log(
        db,
        user,
        "DELETE_READER",
        "READER",
        entity_id=ma,
        details=f"hoTen={reader.hoTen}",
    )
    db.delete(reader)
    db.commit()
    return {"message": "Đã xoá độc giả."}
