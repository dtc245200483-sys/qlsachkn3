import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..audit import write_audit_log
from ..database import get_db
from ..deps import require_roles
from ..models import Book, BorrowSlip, DatTruoc, LibraryConfig, Reader, YeuCau
from ..schemas import BorrowItemCreate, RequestApprove, RequestCreate, RequestOut
from .borrows import _perform_create_borrow, _perform_renew_borrow, _perform_return_borrow
from .reservations import _available_count, _generate_ma_dat

router = APIRouter(prefix="/api/requests", tags=["requests"])


def _request_out(req: YeuCau) -> RequestOut:
    items = [BorrowItemCreate(**item) for item in json.loads(req.items or "[]")]
    return RequestOut(
        ma_yeu_cau=req.ma_yeu_cau,
        loai=req.loai,
        ma_doc_gia=req.ma_doc_gia,
        ma_phieu=req.ma_phieu,
        items=items,
        so_ngay_muon=req.so_ngay_muon,
        trang_thai=req.trang_thai,
        ngay_tao=req.ngay_tao,
    )


@router.post("", response_model=RequestOut)
def create_request(
    body: RequestCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("reader")),
) -> RequestOut:
    if not user.reader_id:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản chưa liên kết với độc giả.",
        )
    if db.get(YeuCau, body.ma_yeu_cau) is not None:
        raise HTTPException(status_code=409, detail="Mã yêu cầu đã tồn tại.")

    if body.loai == "MUON":
        reader = db.get(Reader, user.reader_id)
        if reader is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ độc giả.")
        if reader.trangThaiThe != "hoat_dong":
            raise HTTPException(status_code=400, detail="Thẻ độc giả đang bị khoá.")
        if not body.items:
            raise HTTPException(status_code=400, detail="Yêu cầu mượn phải có danh sách sách.")
        seen = set()
        for item in body.items:
            if item.ma_sach in seen:
                raise HTTPException(
                    status_code=400,
                    detail=f"Trùng sách {item.ma_sach} trong yêu cầu — hãy gộp số lượng.",
                )
            seen.add(item.ma_sach)
        for item in body.items:
            if db.get(Book, item.ma_sach) is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Không tìm thấy sách {item.ma_sach}.",
                )
        effective_items = body.items or []
        if body.so_ngay_muon is not None:
            cfg = db.get(LibraryConfig, 1)
            if cfg is None:
                raise HTTPException(status_code=500, detail="Chưa có cấu hình thư viện.")
            if body.so_ngay_muon > cfg.max_borrow_days:
                raise HTTPException(
                    status_code=400,
                    detail=f"Số ngày mượn vượt quá tối đa {cfg.max_borrow_days} ngày.",
                )
    elif body.loai == "DAT_TRUOC":
        ma_sach = (body.ma_sach or "").strip()
        if not ma_sach:
            if body.items and len(body.items) == 1:
                ma_sach = body.items[0].ma_sach
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Yêu cầu đặt trước phải có đúng 1 sách.",
                )
        if db.get(Book, ma_sach) is None:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy sách {ma_sach}.")
        reader = db.get(Reader, user.reader_id)
        if reader is not None and reader.trangThaiThe != "hoat_dong":
            raise HTTPException(status_code=400, detail="Thẻ độc giả đang bị khoá.")
        effective_items = [BorrowItemCreate(ma_sach=ma_sach, so_luong=1)]
    else:
        if not body.ma_phieu:
            raise HTTPException(status_code=400, detail="Thiếu mã phiếu mượn.")
        slip = db.get(BorrowSlip, body.ma_phieu)
        if slip is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy phiếu mượn.")
        if slip.ma_doc_gia != user.reader_id:
            raise HTTPException(status_code=403, detail="Không phải phiếu mượn của bạn.")
        if slip.trang_thai != "dang_muon":
            raise HTTPException(status_code=400, detail="Phiếu mượn không ở trạng thái đang mượn.")
        if body.loai == "GIA_HAN" and slip.so_lan_gia_han >= 1:
            raise HTTPException(status_code=400, detail="Phiếu mượn đã gia hạn tối đa 1 lần.")
        effective_items = []

    items_json = json.dumps(
        [item.model_dump() for item in effective_items],
        ensure_ascii=False,
    )
    req = YeuCau(
        ma_yeu_cau=body.ma_yeu_cau,
        loai=body.loai,
        ma_doc_gia=user.reader_id,
        ma_phieu=body.ma_phieu,
        items=items_json,
        so_ngay_muon=body.so_ngay_muon if body.loai == "MUON" else None,
        trang_thai="CHO_XU_LY",
        ngay_tao=datetime.now(),
    )
    db.add(req)
    write_audit_log(
        db,
        user,
        "CREATE_REQUEST",
        "REQUEST",
        entity_id=body.ma_yeu_cau,
        details=f"loai={body.loai}; ma_phieu={body.ma_phieu or ''}",
    )
    db.commit()
    db.refresh(req)
    return _request_out(req)


@router.get("", response_model=list[RequestOut])
def list_requests(
    maDocGia: str | None = Query(None, max_length=20),
    trangThai: str | None = Query(None, max_length=20),
    db: Session = Depends(get_db),
    user=Depends(require_roles("reader", "librarian", "admin")),
) -> list[RequestOut]:
    query = db.query(YeuCau)
    if user.role == "reader":
        if not user.reader_id:
            raise HTTPException(status_code=403, detail="Tài khoản chưa liên kết với độc giả.")
        query = query.filter(YeuCau.ma_doc_gia == user.reader_id)
    elif maDocGia:
        query = query.filter(YeuCau.ma_doc_gia == maDocGia)
    if trangThai:
        if trangThai not in ("CHO_XU_LY", "DA_DUYET", "TU_CHOI"):
            raise HTTPException(status_code=422, detail="trangThai không hợp lệ.")
        query = query.filter(YeuCau.trang_thai == trangThai)
    return [_request_out(req) for req in query.order_by(YeuCau.ngay_tao.desc()).all()]


@router.put("/{ma}/approve", response_model=RequestOut)
def approve_request(
    ma: str,
    body: RequestApprove | None = None,
    db: Session = Depends(get_db),
    user=Depends(require_roles("librarian")),
) -> RequestOut:
    req = db.get(YeuCau, ma)
    if req is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu.")
    if req.trang_thai != "CHO_XU_LY":
        raise HTTPException(status_code=400, detail="Yêu cầu không ở trạng thái chờ xử lý.")

    if req.loai == "MUON":
        items = [BorrowItemCreate(**item) for item in json.loads(req.items)]
        so_ngay_muon = None
        if body is not None and body.so_ngay_muon is not None:
            so_ngay_muon = body.so_ngay_muon
        elif req.so_ngay_muon is not None:
            so_ngay_muon = req.so_ngay_muon
        slip = _perform_create_borrow(
            db,
            user,
            ma_phieu="PM" + req.ma_yeu_cau,
            ma_doc_gia=req.ma_doc_gia,
            items=items,
            so_ngay_muon=so_ngay_muon,
        )
        req.ma_phieu = slip.ma_phieu
    elif req.loai == "DAT_TRUOC":
        items = json.loads(req.items or "[]")
        if len(items) != 1:
            raise HTTPException(
                status_code=400,
                detail="Yêu cầu đặt trước phải có đúng 1 sách.",
            )
        ma_sach = items[0]["ma_sach"]
        book = db.get(Book, ma_sach)
        if book is None:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy sách {ma_sach}.")
        if _available_count(db, book) > 0:
            raise HTTPException(status_code=400, detail="Sách còn, không cần đặt trước")
        active = (
            db.query(DatTruoc)
            .filter(
                DatTruoc.ma_sach == ma_sach,
                DatTruoc.ma_doc_gia == req.ma_doc_gia,
                DatTruoc.trang_thai.in_(["CHO_XU_LY", "SAN_SANG"]),
            )
            .first()
        )
        if active is not None:
            raise HTTPException(status_code=409, detail="Bạn đã đặt trước sách này.")
        ma_dat = _generate_ma_dat(db)
        db.add(
            DatTruoc(
                ma_dat=ma_dat,
                ma_sach=ma_sach,
                ma_doc_gia=req.ma_doc_gia,
                ngay_dat=datetime.now(),
                trang_thai="CHO_XU_LY",
                ngay_xu_ly=None,
            )
        )
        write_audit_log(
            db,
            user,
            "CREATE_RESERVATION",
            "RESERVATION",
            entity_id=ma_dat,
            details=f"ma_sach={ma_sach}; via_request={req.ma_yeu_cau}",
        )
        req.ma_phieu = None
    elif req.loai == "TRA":
        _perform_return_borrow(db, user, req.ma_phieu)
    else:
        _perform_renew_borrow(db, user, req.ma_phieu)

    req.trang_thai = "DA_DUYET"
    write_audit_log(
        db,
        user,
        "APPROVE_REQUEST",
        "REQUEST",
        entity_id=req.ma_yeu_cau,
        details=f"loai={req.loai}; ma_phieu={req.ma_phieu or ''}",
    )
    db.commit()
    db.refresh(req)
    return _request_out(req)


@router.put("/{ma}/reject", response_model=RequestOut)
def reject_request(
    ma: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles("librarian")),
) -> RequestOut:
    req = db.get(YeuCau, ma)
    if req is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu.")
    if req.trang_thai != "CHO_XU_LY":
        raise HTTPException(status_code=400, detail="Yêu cầu không ở trạng thái chờ xử lý.")
    req.trang_thai = "TU_CHOI"
    write_audit_log(
        db,
        user,
        "REJECT_REQUEST",
        "REQUEST",
        entity_id=req.ma_yeu_cau,
        details=f"loai={req.loai}",
    )
    db.commit()
    db.refresh(req)
    return _request_out(req)


@router.delete("/me/{ma_yeu_cau}")
def delete_my_request_history(
    ma_yeu_cau: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles("reader")),
):
    if not user.reader_id:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản chưa liên kết với độc giả.",
        )
    req = db.get(YeuCau, ma_yeu_cau)
    if req is None or req.ma_doc_gia != user.reader_id:
        raise HTTPException(status_code=404, detail="Không tìm thấy yêu cầu.")
    if req.trang_thai == "CHO_XU_LY":
        raise HTTPException(
            status_code=400,
            detail="Yêu cầu đang chờ xử lý, không thể xoá.",
        )
    db.delete(req)
    write_audit_log(
        db,
        user,
        "DELETE_REQUEST_HISTORY",
        "REQUEST",
        entity_id=ma_yeu_cau,
        details=f"trang_thai={req.trang_thai}",
    )
    db.commit()
    return {"message": "Đã xoá yêu cầu khỏi lịch sử."}


@router.delete("/me")
def delete_all_my_request_history(
    db: Session = Depends(get_db),
    user=Depends(require_roles("reader")),
):
    if not user.reader_id:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản chưa liên kết với độc giả.",
        )
    targets = (
        db.query(YeuCau)
        .filter(
            YeuCau.ma_doc_gia == user.reader_id,
            YeuCau.trang_thai.in_(["DA_DUYET", "TU_CHOI"]),
        )
        .all()
    )
    count = len(targets)
    for req in targets:
        db.delete(req)
    write_audit_log(
        db,
        user,
        "DELETE_REQUEST_HISTORY_ALL",
        "REQUEST",
        entity_id="ALL",
        details=f"so_yeu_cau_da_xoa={count}",
    )
    db.commit()
    return {
        "message": "Đã xoá lịch sử các yêu cầu đã xử lý.",
        "so_yeu_cau_da_xoa": count,
    }
