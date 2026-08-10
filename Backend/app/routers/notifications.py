import math
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_roles
from ..models import AnThongBao, Book, BorrowSlip, DatTruoc, DocThongBao, YeuCau
from ..schemas import NotificationOut

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


def _build_items(db: Session, reader_id: str, now: datetime) -> list[tuple[str, str, str, datetime]]:
    """Trả [(id, loai, noi_dung, ngay)] cho các thông báo hiện tại của reader."""
    items: list[tuple[str, str, str, datetime]] = []

    slips = (
        db.query(BorrowSlip)
        .filter(
            BorrowSlip.ma_doc_gia == reader_id,
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
        items.append((f"BORROW:{slip.ma_phieu}", loai, noi_dung, slip.han_tra))

    reservations = (
        db.query(DatTruoc)
        .filter(
            DatTruoc.ma_doc_gia == reader_id,
            DatTruoc.trang_thai == "SAN_SANG",
        )
        .all()
    )
    for res in reservations:
        book = db.get(Book, res.ma_sach)
        ten_sach = book.ten if book is not None else res.ma_sach
        items.append(
            (
                f"RES:{res.ma_dat}",
                "SACH_SAN_SANG",
                f"Đặt trước {res.ma_dat} — {ten_sach} đã sẵn sàng",
                res.ngay_xu_ly or res.ngay_dat,
            )
        )

    seven_days_ago = now - timedelta(days=7)
    approved_requests = (
        db.query(YeuCau)
        .filter(
            YeuCau.ma_doc_gia == reader_id,
            YeuCau.trang_thai == "DA_DUYET",
            YeuCau.ngay_xu_ly.isnot(None),
            YeuCau.ngay_xu_ly >= seven_days_ago,
        )
        .all()
    )
    for req in approved_requests:
        noi_dung = f"Yêu cầu {req.ma_yeu_cau} ({req.loai}) đã được duyệt"
        if req.loai == "MUON" and req.ma_phieu:
            noi_dung += f" — phiếu mượn {req.ma_phieu}"
        items.append(
            (
                f"YEU_CAU:{req.ma_yeu_cau}",
                "YEU_CAU_DA_DUYET",
                noi_dung,
                req.ngay_xu_ly,
            )
        )

    borrowed_reservations = (
        db.query(DatTruoc)
        .filter(
            DatTruoc.ma_doc_gia == reader_id,
            DatTruoc.trang_thai == "DA_MUON",
            DatTruoc.ngay_xu_ly.isnot(None),
            DatTruoc.ngay_xu_ly >= seven_days_ago,
        )
        .all()
    )
    for res in borrowed_reservations:
        book = db.get(Book, res.ma_sach)
        ten_sach = book.ten if book is not None else res.ma_sach
        ma_phieu = "PM" + res.ma_dat[2:]
        items.append(
            (
                f"DAT_TRUOC:{res.ma_dat}",
                "DAT_TRUOC_DA_MUON",
                f"Đặt trước {res.ma_dat} — {ten_sach} đã xác nhận, phiếu mượn {ma_phieu}",
                res.ngay_xu_ly,
            )
        )

    return items


def _mark_read(db: Session, reader_id: str, source_id: str, now: datetime) -> None:
    row = (
        db.query(DocThongBao)
        .filter(
            DocThongBao.ma_doc_gia == reader_id,
            DocThongBao.nguon_id == source_id,
        )
        .first()
    )
    if row is None:
        db.add(
            DocThongBao(
                ma_doc_gia=reader_id,
                nguon_id=source_id,
                da_doc=True,
                ngay_doc=now,
            )
        )
    else:
        row.da_doc = True
        row.ngay_doc = now


def _hide_source(db: Session, reader_id: str, source_id: str, now: datetime) -> None:
    row = (
        db.query(AnThongBao)
        .filter(
            AnThongBao.ma_doc_gia == reader_id,
            AnThongBao.nguon_id == source_id,
        )
        .first()
    )
    if row is None:
        db.add(
            AnThongBao(
                ma_doc_gia=reader_id,
                nguon_id=source_id,
                ngay_an=now,
            )
        )
    else:
        row.ngay_an = now
    db.query(DocThongBao).filter(
        DocThongBao.ma_doc_gia == reader_id,
        DocThongBao.nguon_id == source_id,
    ).delete(synchronize_session=False)


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
    raw_items = _build_items(db, user.reader_id, now)
    source_ids = [item[0] for item in raw_items]
    hidden_rows = (
        db.query(AnThongBao.nguon_id)
        .filter(
            AnThongBao.ma_doc_gia == user.reader_id,
            AnThongBao.nguon_id.in_(source_ids),
        )
        .all()
    )
    hidden_ids = {row[0] for row in hidden_rows}
    raw_items = [item for item in raw_items if item[0] not in hidden_ids]
    source_ids = [item[0] for item in raw_items]
    read_rows = (
        db.query(DocThongBao.nguon_id)
        .filter(
            DocThongBao.ma_doc_gia == user.reader_id,
            DocThongBao.nguon_id.in_(source_ids),
            DocThongBao.da_doc == True,  # noqa: E712
        )
        .all()
    )
    read_ids = {row[0] for row in read_rows}

    items = [
        NotificationOut(
            id=item_id,
            loai=loai,
            noi_dung=noi_dung,
            ngay=ngay,
            da_doc=item_id in read_ids,
        )
        for item_id, loai, noi_dung, ngay in raw_items
    ]
    items.sort(key=lambda item: item.ngay, reverse=True)
    return items


@router.delete("")
def hide_all_notifications(
    db: Session = Depends(get_db),
    user=Depends(require_roles("reader")),
):
    if not user.reader_id:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản chưa liên kết với độc giả.",
        )
    now = datetime.now()
    source_ids = [item[0] for item in _build_items(db, user.reader_id, now)]
    for source_id in source_ids:
        _hide_source(db, user.reader_id, source_id, now)
    db.commit()
    return {
        "message": "Đã xoá tất cả thông báo.",
        "da_xoa": len(source_ids),
    }


@router.delete("/{source_id}")
def hide_notification(
    source_id: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles("reader")),
):
    if not user.reader_id:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản chưa liên kết với độc giả.",
        )
    now = datetime.now()
    current_ids = {item[0] for item in _build_items(db, user.reader_id, now)}
    if source_id not in current_ids:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông báo.")
    _hide_source(db, user.reader_id, source_id, now)
    db.commit()
    return {"message": "Đã xoá thông báo.", "da_xoa": 1}


@router.put("/read-all")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    user=Depends(require_roles("reader")),
):
    if not user.reader_id:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản chưa liên kết với độc giả.",
        )
    now = datetime.now()
    source_ids = [item[0] for item in _build_items(db, user.reader_id, now)]
    for source_id in source_ids:
        _mark_read(db, user.reader_id, source_id, now)
    db.commit()
    return {"message": "Đã đánh dấu tất cả thông báo đã đọc.", "so_da_doc": len(source_ids)}


@router.put("/{source_id}/read")
def mark_notification_read(
    source_id: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles("reader")),
):
    if not user.reader_id:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản chưa liên kết với độc giả.",
        )
    now = datetime.now()
    current_ids = {item[0] for item in _build_items(db, user.reader_id, now)}
    if source_id not in current_ids:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông báo.")
    _mark_read(db, user.reader_id, source_id, now)
    db.commit()
    return {"message": "Đã đánh dấu thông báo đã đọc.", "id": source_id}
