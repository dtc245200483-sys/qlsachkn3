import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..audit import write_audit_log
from ..database import get_db
from ..deps import require_roles
from ..models import Book, BorrowDetail, BorrowSlip, DatTruoc, Reader
from ..schemas import ReservationCreate, ReservationOut

router = APIRouter(prefix="/api/reservations", tags=["reservations"])

RESERVATION_STATUSES = ("CHO_XU_LY", "SAN_SANG", "DA_MUON", "HUY")


def _available_count(db: Session, book: Book) -> int:
    borrowed = (
        db.query(func.coalesce(func.sum(BorrowDetail.so_luong), 0))
        .join(BorrowSlip, BorrowSlip.ma_phieu == BorrowDetail.ma_phieu)
        .filter(
            BorrowDetail.ma_sach == book.ma,
            BorrowSlip.trang_thai == "dang_muon",
            BorrowDetail.ngay_tra_chi_tiet.is_(None),
        )
        .scalar()
    )
    return book.soLuong - (borrowed or 0)


def _out(db: Session, res: DatTruoc) -> ReservationOut:
    book = db.get(Book, res.ma_sach)
    return ReservationOut(
        ma_dat=res.ma_dat,
        ma_sach=res.ma_sach,
        ten_sach=book.ten if book is not None else "",
        ma_doc_gia=res.ma_doc_gia,
        ngay_dat=res.ngay_dat,
        trang_thai=res.trang_thai,
    )


def _generate_ma_dat(db: Session) -> str:
    for _ in range(5):
        candidate = (
            "RV"
            + datetime.now().strftime("%Y%m%d%H%M%S")
            + f"{secrets.randbelow(1000):03d}"
        )
        if db.get(DatTruoc, candidate) is None:
            return candidate
    raise HTTPException(status_code=500, detail="Không tạo được mã đặt trước, thử lại.")


@router.get("", response_model=list[ReservationOut])
def list_reservations(
    trangThai: str | None = Query(None, max_length=20),
    db: Session = Depends(get_db),
    user=Depends(require_roles("reader", "librarian")),
) -> list[ReservationOut]:
    query = db.query(DatTruoc)
    if user.role == "reader":
        if not user.reader_id:
            raise HTTPException(
                status_code=403,
                detail="Tài khoản chưa liên kết với độc giả.",
            )
        query = query.filter(DatTruoc.ma_doc_gia == user.reader_id)
    if trangThai:
        if trangThai not in RESERVATION_STATUSES:
            raise HTTPException(status_code=422, detail="trangThai không hợp lệ.")
        query = query.filter(DatTruoc.trang_thai == trangThai)
    rows = query.order_by(DatTruoc.ngay_dat.asc(), DatTruoc.ma_dat.asc()).all()
    return [_out(db, row) for row in rows]


@router.post("", response_model=ReservationOut)
def create_reservation(
    body: ReservationCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("reader")),
) -> ReservationOut:
    if not user.reader_id:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản chưa liên kết với độc giả.",
        )
    reader = db.get(Reader, user.reader_id)
    if reader is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy độc giả.")
    if reader.trangThaiThe != "hoat_dong":
        raise HTTPException(status_code=400, detail="Thẻ độc giả đang bị khoá.")

    book = db.get(Book, body.ma_sach)
    if book is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy sách.")
    if _available_count(db, book) > 0:
        raise HTTPException(status_code=400, detail="Sách còn, không cần đặt trước")

    active = (
        db.query(DatTruoc)
        .filter(
            DatTruoc.ma_sach == body.ma_sach,
            DatTruoc.ma_doc_gia == user.reader_id,
            DatTruoc.trang_thai.in_(["CHO_XU_LY", "SAN_SANG"]),
        )
        .first()
    )
    if active is not None:
        raise HTTPException(status_code=409, detail="Bạn đã đặt trước sách này.")

    ma_dat = _generate_ma_dat(db)
    res = DatTruoc(
        ma_dat=ma_dat,
        ma_sach=body.ma_sach,
        ma_doc_gia=user.reader_id,
        ngay_dat=datetime.now(),
        trang_thai="CHO_XU_LY",
        ngay_xu_ly=None,
    )
    db.add(res)
    write_audit_log(
        db,
        user,
        "CREATE_RESERVATION",
        "RESERVATION",
        entity_id=ma_dat,
        details=f"ma_sach={body.ma_sach}",
    )
    db.commit()
    db.refresh(res)
    return _out(db, res)


@router.put("/{ma_dat}/cancel", response_model=ReservationOut)
def cancel_reservation(
    ma_dat: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles("reader", "librarian")),
) -> ReservationOut:
    res = db.get(DatTruoc, ma_dat)
    if res is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy đặt trước.")
    if user.role == "reader" and res.ma_doc_gia != user.reader_id:
        raise HTTPException(status_code=404, detail="Không tìm thấy đặt trước.")
    if res.trang_thai != "CHO_XU_LY":
        raise HTTPException(
            status_code=400,
            detail="Chỉ huỷ được đặt trước đang chờ xử lý.",
        )
    res.trang_thai = "HUY"
    res.ngay_xu_ly = datetime.now()
    write_audit_log(
        db,
        user,
        "CANCEL_RESERVATION",
        "RESERVATION",
        entity_id=ma_dat,
    )
    db.commit()
    db.refresh(res)
    return _out(db, res)


@router.put("/{ma_dat}/fulfill", response_model=ReservationOut)
def fulfill_reservation(
    ma_dat: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles("librarian")),
) -> ReservationOut:
    res = db.get(DatTruoc, ma_dat)
    if res is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy đặt trước.")
    if res.trang_thai != "CHO_XU_LY":
        raise HTTPException(
            status_code=400,
            detail="Chỉ chuyển SAN_SANG từ trạng thái chờ xử lý.",
        )
    res.trang_thai = "SAN_SANG"
    res.ngay_xu_ly = datetime.now()
    write_audit_log(
        db,
        user,
        "FULFILL_RESERVATION",
        "RESERVATION",
        entity_id=ma_dat,
        details=f"ma_sach={res.ma_sach}",
    )
    db.commit()
    db.refresh(res)
    return _out(db, res)
