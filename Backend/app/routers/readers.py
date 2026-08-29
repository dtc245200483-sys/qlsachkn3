from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..audit import write_audit_log
from ..database import get_db
from ..deps import require_roles
from ..models import Reader, User, BorrowSlip, FineHistory, YeuCau, DatTruoc
from ..schemas import LockReaderRequest, ReaderCreate, ReaderOut, ReaderUpdate
from ..validation import ensure_email_unique, validate_email, validate_ho_ten, validate_phone

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
    user=Depends(require_roles("admin", "librarian")),
) -> ReaderOut:
    if db.get(Reader, body.ma) is not None:
        raise HTTPException(status_code=409, detail="Mã độc giả đã tồn tại.")
    ho_ten = validate_ho_ten(body.hoTen)
    email = validate_email(body.email)
    so_dien_thoai = validate_phone(body.soDienThoai)
    ensure_email_unique(db, email)
    reader = Reader(
        ma=body.ma,
        hoTen=ho_ten,
        email=email,
        soDienThoai=so_dien_thoai,
        loaiDocGia=body.loaiDocGia,
        trangThaiThe=body.trangThaiThe,
    )
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
    user=Depends(require_roles("admin", "librarian")),
) -> ReaderOut:
    reader = db.get(Reader, ma)
    if reader is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy độc giả.")
    data = body.model_dump(exclude_unset=True)
    if "email" in data:
        reader.email = validate_email(data["email"])
        ensure_email_unique(db, reader.email, exclude_reader_ma=ma)
    if "hoTen" in data:
        reader.hoTen = validate_ho_ten(data["hoTen"])
    if "soDienThoai" in data:
        reader.soDienThoai = validate_phone(data["soDienThoai"])
    if "loaiDocGia" in data:
        reader.loaiDocGia = data["loaiDocGia"]
    if "trangThaiThe" in data:
        reader.trangThaiThe = data["trangThaiThe"]
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
        
    active_borrows = db.query(BorrowSlip).filter(
        BorrowSlip.ma_doc_gia == ma, 
        BorrowSlip.trang_thai.in_(["dang_muon", "qua_han"])
    ).count()
    if active_borrows > 0:
        raise HTTPException(status_code=400, detail="Không thể xoá độc giả vì đang có phiếu mượn chưa trả sách.")
        
    unpaid_fines = db.query(FineHistory).filter(
        FineHistory.ma_doc_gia == ma,
        FineHistory.da_thu == False
    ).count()
    if unpaid_fines > 0:
        raise HTTPException(status_code=400, detail="Không thể xoá độc giả vì còn khoản phạt chưa đóng.")
        
    pending_requests = db.query(YeuCau).filter(
        YeuCau.ma_doc_gia == ma,
        YeuCau.trang_thai == "CHO_XU_LY"
    ).count()
    
    pending_reservations = db.query(DatTruoc).filter(
        DatTruoc.ma_doc_gia == ma,
        DatTruoc.trang_thai.in_(["CHO_XU_LY", "SAN_SANG"])
    ).count()
    
    if pending_requests > 0 or pending_reservations > 0:
        raise HTTPException(status_code=400, detail="Không thể xoá độc giả vì đang có yêu cầu hoặc đặt trước chờ xử lý.")
        
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
