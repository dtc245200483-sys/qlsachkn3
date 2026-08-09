import math
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_roles
from ..models import Book, BorrowSlip, DatTruoc
from ..schemas import NotificationOut

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
def list_notifications(
    db: Session = Depends(get_db),
    user=Depends(require_roles("reader")),
) -> list[NotificationOut]:
    if not user.reader_id:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản chưa liên kết với độc giả.",
        )

    now = datetime.now()
    items: list[NotificationOut] = []

    slips = (
        db.query(BorrowSlip)
        .filter(
            BorrowSlip.ma_doc_gia == user.reader_id,
            BorrowSlip.trang_thai == "dang_muon",
        )
        .all()
    )
    for slip in slips:
        days_left = math.ceil((slip.han_tra - now).total_seconds() / 86400)
        if days_left > 3:
            continue
        if days_left < 0:
            loai = "QUA_HAN"
            noi_dung = (
                f"Phiếu {slip.ma_phieu} hạn trả "
                f"{slip.han_tra.strftime('%d/%m/%Y')} — đã quá hạn {-days_left} ngày"
            )
        else:
            loai = "SAP_HET_HAN"
            noi_dung = (
                f"Phiếu {slip.ma_phieu} hạn trả "
                f"{slip.han_tra.strftime('%d/%m/%Y')} — còn {days_left} ngày"
            )
        items.append(
            NotificationOut(
                id=f"BORROW:{slip.ma_phieu}",
                loai=loai,
                noi_dung=noi_dung,
                ngay=slip.han_tra,
                da_doc=False,
            )
        )

    reservations = (
        db.query(DatTruoc)
        .filter(
            DatTruoc.ma_doc_gia == user.reader_id,
            DatTruoc.trang_thai == "SAN_SANG",
        )
        .all()
    )
    for res in reservations:
        book = db.get(Book, res.ma_sach)
        ten_sach = book.ten if book is not None else res.ma_sach
        items.append(
            NotificationOut(
                id=f"RES:{res.ma_dat}",
                loai="SACH_SAN_SANG",
                noi_dung=f"Đặt trước {res.ma_dat} — {ten_sach} đã sẵn sàng",
                ngay=res.ngay_xu_ly or res.ngay_dat,
                da_doc=False,
            )
        )

    items.sort(key=lambda item: item.ngay, reverse=True)
    return items
