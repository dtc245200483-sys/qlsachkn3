from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import Date, cast, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_roles
from ..models import Book, BorrowDetail, BorrowSlip, Reader
from ..schemas import StatsBookOut, StatsOverdueOut, StatsReaderOut

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/top-books", response_model=list[StatsBookOut])
def top_books(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "librarian")),
) -> list[StatsBookOut]:
    rows = (
        db.query(
            BorrowDetail.ma_sach,
            Book.ten,
            func.count(BorrowDetail.ma_sach).label("so_lan"),
        )
        .join(Book, Book.ma == BorrowDetail.ma_sach)
        .group_by(BorrowDetail.ma_sach, Book.ten)
        .order_by(func.count(BorrowDetail.ma_sach).desc(), BorrowDetail.ma_sach.asc())
        .limit(limit)
        .all()
    )
    return [
        StatsBookOut(ma_sach=row.ma_sach, ten_sach=row.ten, so_lan_muon=row.so_lan)
        for row in rows
    ]


@router.get("/top-readers", response_model=list[StatsReaderOut])
def top_readers(
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "librarian")),
) -> list[StatsReaderOut]:
    rows = (
        db.query(
            BorrowSlip.ma_doc_gia,
            Reader.hoTen,
            func.count(BorrowSlip.ma_phieu).label("so_phieu"),
        )
        .join(Reader, Reader.ma == BorrowSlip.ma_doc_gia)
        .group_by(BorrowSlip.ma_doc_gia, Reader.hoTen)
        .order_by(
            func.count(BorrowSlip.ma_phieu).desc(),
            BorrowSlip.ma_doc_gia.asc(),
        )
        .limit(10)
        .all()
    )
    return [
        StatsReaderOut(
            ma_doc_gia=row.ma_doc_gia,
            ho_ten=row.hoTen,
            so_phieu_muon=row.so_phieu,
        )
        for row in rows
    ]


@router.get("/overdue-books", response_model=list[StatsOverdueOut])
def overdue_books(
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "librarian")),
) -> list[StatsOverdueOut]:
    today = datetime.now().date()
    slips = (
        db.query(BorrowSlip, Reader.hoTen)
        .join(Reader, Reader.ma == BorrowSlip.ma_doc_gia)
        .filter(
            BorrowSlip.trang_thai == "dang_muon",
            cast(BorrowSlip.han_tra, Date) < today,
        )
        .order_by(BorrowSlip.han_tra.asc())
        .all()
    )
    result: list[StatsOverdueOut] = []
    for slip, ho_ten in slips:
        details = (
            db.query(BorrowDetail.ma_sach, Book.ten)
            .join(Book, Book.ma == BorrowDetail.ma_sach)
            .filter(BorrowDetail.ma_phieu == slip.ma_phieu)
            .all()
        )
        so_ngay_qua_han = max(0, (today - slip.han_tra.date()).days)
        for ma_sach, ten_sach in details:
            result.append(
                StatsOverdueOut(
                    ma_phieu=slip.ma_phieu,
                    ma_sach=ma_sach,
                    ten_sach=ten_sach,
                    ma_doc_gia=slip.ma_doc_gia,
                    ho_ten=ho_ten,
                    so_ngay_qua_han=so_ngay_qua_han,
                )
            )
    return result
