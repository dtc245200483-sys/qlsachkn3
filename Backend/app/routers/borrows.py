from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..audit import write_audit_log
from ..database import get_db
from ..deps import require_roles
from ..models import Book, BorrowDetail, BorrowSlip, DatTruoc, FineHistory, LibraryConfig, Reader
from ..schemas import (
    BorrowCreate,
    BorrowDetailOut,
    BorrowHistoryOut,
    BorrowItemCreate,
    BorrowRenewOut,
    BorrowReturnOut,
    BorrowSlipOut,
    CollectFineOut,
    FineOut,
)

router = APIRouter(prefix="/api/borrows", tags=["borrows"])


def _get_library_config(db: Session) -> LibraryConfig:
    cfg = db.get(LibraryConfig, 1)
    if cfg is None:
        raise HTTPException(status_code=500, detail="Chưa có cấu hình thư viện.")
    return cfg


def _overdue_days(han_tra: datetime, now: datetime) -> int:
    return max(0, (now.date() - han_tra.date()).days)


def _slip_out(db: Session, slip: BorrowSlip) -> BorrowSlipOut:
    details = (
        db.query(BorrowDetail)
        .filter(BorrowDetail.ma_phieu == slip.ma_phieu)
        .order_by(BorrowDetail.ma_sach.asc())
        .all()
    )
    fines = (
        db.query(FineHistory)
        .filter(FineHistory.ma_phieu == slip.ma_phieu)
        .order_by(FineHistory.id.asc())
        .all()
    )
    return BorrowSlipOut(
        ma_phieu=slip.ma_phieu,
        ma_doc_gia=slip.ma_doc_gia,
        ngay_muon=slip.ngay_muon,
        han_tra=slip.han_tra,
        ngay_tra=slip.ngay_tra,
        trang_thai=slip.trang_thai,
        so_lan_gia_han=slip.so_lan_gia_han,
        details=[
            BorrowDetailOut(
                ma_sach=detail.ma_sach,
                ten_sach=db.get(Book, detail.ma_sach).ten if db.get(Book, detail.ma_sach) is not None else "",
                so_luong=detail.so_luong,
                ngay_tra_chi_tiet=detail.ngay_tra_chi_tiet,
            )
            for detail in details
        ],
        fines=[
            FineOut(
                so_ngay_qua_han=fine.so_ngay_qua_han,
                so_diem=fine.so_diem,
                da_thu=fine.da_thu,
                ngay_thu=fine.ngay_thu,
            )
            for fine in fines
        ],
    )


def _history_out(db: Session, slip: BorrowSlip) -> BorrowHistoryOut:
    return BorrowHistoryOut(**_slip_out(db, slip).model_dump())


def _perform_create_borrow(
    db: Session,
    user,
    ma_phieu: str,
    ma_doc_gia: str,
    items: list[BorrowItemCreate],
    so_ngay_muon: int | None = None,
) -> BorrowSlip:
    if db.get(BorrowSlip, ma_phieu) is not None:
        raise HTTPException(status_code=409, detail="Mã phiếu mượn đã tồn tại.")

    reader = db.get(Reader, ma_doc_gia)
    if reader is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy độc giả.")
    if reader.trangThaiThe != "hoat_dong":
        raise HTTPException(status_code=400, detail="Thẻ độc giả đang bị khoá.")

    # Gộp trùng mã sách (VD: 2 dòng cùng S005) để không trùng khóa chính BorrowDetails
    merged: dict[str, int] = {}
    for item in items:
        merged[item.ma_sach] = merged.get(item.ma_sach, 0) + item.so_luong

    cfg = _get_library_config(db)
    total_books = sum(merged.values())
    if total_books > cfg.max_books_at_once:
        raise HTTPException(
            status_code=400,
            detail=f"Vượt quá giới hạn {cfg.max_books_at_once} sách/lần mượn.",
        )

    for ma_sach, qty in merged.items():
        book = db.get(Book, ma_sach)
        if book is None:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy sách {ma_sach}.")
        if book.soLuong <= 0 or book.soLuong < qty:
            raise HTTPException(
                status_code=400,
                detail=f"Sách {ma_sach} không đủ số lượng (còn {book.soLuong}).",
            )

    ngay_muon = datetime.now()
    if so_ngay_muon is not None:
        if so_ngay_muon > cfg.max_borrow_days:
            raise HTTPException(
                status_code=400,
                detail=f"Số ngày mượn vượt quá tối đa {cfg.max_borrow_days} ngày.",
            )
        if so_ngay_muon < 1:
            raise HTTPException(status_code=400, detail="Số ngày mượn phải >= 1.")
        han_tra = ngay_muon + timedelta(days=so_ngay_muon)
    else:
        han_tra = ngay_muon + timedelta(days=cfg.max_borrow_days)
    slip = BorrowSlip(
        ma_phieu=ma_phieu,
        ma_doc_gia=ma_doc_gia,
        ngay_muon=ngay_muon,
        han_tra=han_tra,
        trang_thai="dang_muon",
        so_lan_gia_han=0,
    )
    db.add(slip)
    for ma_sach, qty in merged.items():
        book = db.get(Book, ma_sach)
        book.soLuong -= qty
        db.add(
            BorrowDetail(
                ma_phieu=ma_phieu,
                ma_sach=ma_sach,
                so_luong=qty,
                ngay_tra_chi_tiet=None,
            )
        )
    write_audit_log(
        db,
        user,
        "CREATE_BORROW",
        "BORROW",
        entity_id=ma_phieu,
        details=f"ma_doc_gia={ma_doc_gia}; so_sach={total_books}",
    )
    db.commit()
    db.refresh(slip)
    return slip


def _perform_return_borrow(db: Session, user, ma: str) -> BorrowReturnOut:
    slip = db.get(BorrowSlip, ma)
    if slip is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiếu mượn.")
    if slip.trang_thai == "da_tra":
        raise HTTPException(status_code=400, detail="Phiếu mượn đã được trả.")

    cfg = _get_library_config(db)
    ngay_tra = datetime.now()
    details = (
        db.query(BorrowDetail)
        .filter(
            BorrowDetail.ma_phieu == ma,
            BorrowDetail.ngay_tra_chi_tiet.is_(None),
        )
        .all()
    )
    for detail in details:
        book = db.get(Book, detail.ma_sach)
        if book is not None:
            book.soLuong += detail.so_luong
        detail.ngay_tra_chi_tiet = ngay_tra

    slip.ngay_tra = ngay_tra
    slip.trang_thai = "da_tra"

    for detail in details:
        promoted = 0
        while promoted < detail.so_luong:
            pending = (
                db.query(DatTruoc)
                .filter(
                    DatTruoc.ma_sach == detail.ma_sach,
                    DatTruoc.trang_thai == "CHO_XU_LY",
                )
                .order_by(DatTruoc.ngay_dat.asc(), DatTruoc.ma_dat.asc())
                .first()
            )
            if pending is None:
                break
            pending.trang_thai = "SAN_SANG"
            pending.ngay_xu_ly = ngay_tra
            write_audit_log(
                db,
                user,
                "RESERVATION_READY",
                "RESERVATION",
                entity_id=pending.ma_dat,
                details=f"ma_sach={detail.ma_sach}",
            )
            promoted += 1

    fine = None
    days = _overdue_days(slip.han_tra, ngay_tra)
    if days > 0:
        points = days * cfg.overdue_fine_points_per_day
        db.add(
            FineHistory(
                ma_phieu=ma,
                ma_doc_gia=slip.ma_doc_gia,
                so_ngay_qua_han=days,
                so_diem=points,
                ngay_tinh=ngay_tra,
            )
        )
        fine = FineOut(so_ngay_qua_han=days, so_diem=points)
        audit_detail = f"quá hạn {days} ngày, phạt {points} điểm"
    else:
        audit_detail = "không quá hạn"

    write_audit_log(
        db,
        user,
        "RETURN_BORROW",
        "BORROW",
        entity_id=ma,
        details=audit_detail,
    )
    db.commit()
    return BorrowReturnOut(message="Đã trả sách.", ngay_tra=ngay_tra, fine=fine)


def _perform_renew_borrow(db: Session, user, ma: str) -> BorrowRenewOut:
    slip = db.get(BorrowSlip, ma)
    if slip is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiếu mượn.")
    if slip.trang_thai == "da_tra":
        raise HTTPException(status_code=400, detail="Phiếu mượn đã được trả, không thể gia hạn.")
    if slip.so_lan_gia_han >= 1:
        raise HTTPException(status_code=400, detail="Phiếu mượn đã gia hạn tối đa 1 lần.")

    slip_books = [
        detail.ma_sach
        for detail in db.query(BorrowDetail)
        .filter(BorrowDetail.ma_phieu == ma)
        .all()
    ]
    if slip_books:
        waiting = (
            db.query(DatTruoc)
            .filter(
                DatTruoc.ma_sach.in_(slip_books),
                DatTruoc.trang_thai.in_(["CHO_XU_LY", "SAN_SANG"]),
            )
            .first()
        )
        if waiting is not None:
            raise HTTPException(
                status_code=400,
                detail="Có độc giả đang đặt trước sách trong phiếu, không thể gia hạn.",
            )

    cfg = _get_library_config(db)
    now = datetime.now()
    fine = None
    days = _overdue_days(slip.han_tra, now)
    if days > 0:
        points = days * cfg.overdue_fine_points_per_day
        db.add(
            FineHistory(
                ma_phieu=ma,
                ma_doc_gia=slip.ma_doc_gia,
                so_ngay_qua_han=days,
                so_diem=points,
                ngay_tinh=now,
            )
        )
        fine = FineOut(so_ngay_qua_han=days, so_diem=points)

    slip.han_tra = slip.han_tra + timedelta(days=cfg.max_borrow_days)
    slip.so_lan_gia_han += 1
    audit_detail = f"han_tra_moi={slip.han_tra}; lan_gia_han={slip.so_lan_gia_han}"
    if fine is not None:
        audit_detail += f"; phạt quá hạn {days} ngày"
    write_audit_log(
        db,
        user,
        "RENEW_BORROW",
        "BORROW",
        entity_id=ma,
        details=audit_detail,
    )
    db.commit()
    return BorrowRenewOut(
        message="Đã gia hạn phiếu mượn.",
        han_tra_moi=slip.han_tra,
        so_lan_gia_han=slip.so_lan_gia_han,
        fine=fine,
    )


@router.get("/me", response_model=list[BorrowHistoryOut])
def my_borrows(
    db: Session = Depends(get_db),
    user=Depends(require_roles("reader")),
) -> list[BorrowHistoryOut]:
    if not user.reader_id:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản chưa liên kết với độc giả.",
        )
    slips = (
        db.query(BorrowSlip)
        .filter(BorrowSlip.ma_doc_gia == user.reader_id)
        .order_by(BorrowSlip.ngay_muon.desc())
        .all()
    )
    return [_history_out(db, slip) for slip in slips]


@router.delete("/me/{ma_phieu}")
def delete_my_borrow_history(
    ma_phieu: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles("reader")),
):
    if not user.reader_id:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản chưa liên kết với độc giả.",
        )
    slip = db.get(BorrowSlip, ma_phieu)
    if slip is None or slip.ma_doc_gia != user.reader_id:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiếu mượn.")
    if slip.trang_thai != "da_tra":
        raise HTTPException(
            status_code=400,
            detail="Chỉ xoá được phiếu đã trả, không xoá phiếu đang mượn.",
        )
    write_audit_log(
        db,
        user,
        "DELETE_BORROW_HISTORY",
        "BORROW",
        entity_id=ma_phieu,
        details="xoá lịch sử phiếu đã trả",
    )
    db.query(FineHistory).filter(FineHistory.ma_phieu == ma_phieu).delete(
        synchronize_session=False
    )
    db.query(BorrowDetail).filter(BorrowDetail.ma_phieu == ma_phieu).delete(
        synchronize_session=False
    )
    db.delete(slip)
    db.commit()
    return {"message": "Đã xoá lịch sử phiếu mượn."}


@router.delete("/me")
def delete_all_my_borrow_history(
    db: Session = Depends(get_db),
    user=Depends(require_roles("reader")),
):
    if not user.reader_id:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản chưa liên kết với độc giả.",
        )
    slips = (
        db.query(BorrowSlip)
        .filter(
            BorrowSlip.ma_doc_gia == user.reader_id,
            BorrowSlip.trang_thai == "da_tra",
        )
        .all()
    )
    count = len(slips)
    if count:
        slip_ids = [slip.ma_phieu for slip in slips]
        db.query(FineHistory).filter(FineHistory.ma_phieu.in_(slip_ids)).delete(
            synchronize_session=False
        )
        db.query(BorrowDetail).filter(BorrowDetail.ma_phieu.in_(slip_ids)).delete(
            synchronize_session=False
        )
        for slip in slips:
            db.delete(slip)
    write_audit_log(
        db,
        user,
        "DELETE_BORROW_HISTORY_ALL",
        "BORROW",
        details=f"so_phieu_da_xoa={count}",
    )
    db.commit()
    return {
        "message": "Đã xoá lịch sử các phiếu đã trả.",
        "so_phieu_da_xoa": count,
    }


@router.get("", response_model=list[BorrowSlipOut])
def list_borrows(
    docGia: str | None = Query(None, max_length=20),
    trangThai: str | None = Query(None, max_length=20),
    db: Session = Depends(get_db),
    user=Depends(require_roles("librarian")),
) -> list[BorrowSlipOut]:
    query = db.query(BorrowSlip)
    if docGia:
        query = query.filter(BorrowSlip.ma_doc_gia == docGia)
    if trangThai:
        if trangThai not in ("dang_muon", "da_tra"):
            raise HTTPException(status_code=422, detail="trangThai chỉ nhận dang_muon hoặc da_tra.")
        query = query.filter(BorrowSlip.trang_thai == trangThai)
    slips = query.order_by(BorrowSlip.ngay_muon.desc()).all()
    return [_slip_out(db, slip) for slip in slips]


@router.post("", response_model=BorrowSlipOut)
def create_borrow(
    body: BorrowCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("librarian")),
) -> BorrowSlipOut:
    slip = _perform_create_borrow(
        db,
        user,
        ma_phieu=body.ma_phieu,
        ma_doc_gia=body.ma_doc_gia,
        items=body.items,
        so_ngay_muon=body.so_ngay_muon,
    )
    return _slip_out(db, slip)


@router.put("/{ma}/return", response_model=BorrowReturnOut)
def return_borrow(
    ma: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles("librarian")),
) -> BorrowReturnOut:
    return _perform_return_borrow(db, user, ma)


@router.put("/{ma}/renew", response_model=BorrowRenewOut)
def renew_borrow(
    ma: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles("librarian")),
) -> BorrowRenewOut:
    return _perform_renew_borrow(db, user, ma)


@router.post("/{ma}/collect-fine", response_model=CollectFineOut)
def collect_fine(
    ma: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles("librarian")),
) -> CollectFineOut:
    slip = db.get(BorrowSlip, ma)
    if slip is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiếu mượn.")
    if slip.trang_thai != "da_tra":
        raise HTTPException(
            status_code=400,
            detail="Phiếu chưa trả, không thể thu phạt.",
        )
    fines = (
        db.query(FineHistory)
        .filter(
            FineHistory.ma_phieu == ma,
            FineHistory.da_thu == False,  # noqa: E712
        )
        .all()
    )
    if not fines:
        raise HTTPException(status_code=400, detail="Không có phạt để thu.")

    ngay_thu = datetime.now()
    reader = db.get(Reader, slip.ma_doc_gia)
    total_days = sum(fine.so_ngay_qua_han for fine in fines)
    so_diem_da_thu = sum(fine.so_diem for fine in fines)
    diem_con_lai = reader.diem_svnet if reader is not None else 0
    if reader is not None:
        diem_con_lai = max(0, reader.diem_svnet - so_diem_da_thu)
        reader.diem_svnet = diem_con_lai
    for fine in fines:
        fine.da_thu = True
        fine.ngay_thu = ngay_thu
    write_audit_log(
        db,
        user,
        "COLLECT_FINE",
        "FINE",
        entity_id=ma,
        details=f"so_ngay_qua_han={total_days}; so_diem_da_thu={so_diem_da_thu}; diem_con_lai={diem_con_lai}",
    )
    db.commit()
    return CollectFineOut(
        message="Đã trừ điểm SVNET.",
        so_diem_da_thu=so_diem_da_thu,
        diem_con_lai=diem_con_lai,
        ngay_thu=ngay_thu,
    )
