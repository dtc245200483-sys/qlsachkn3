from datetime import datetime

from fastapi import APIRouter, Depends, Response
from sqlalchemy import Date, cast, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_roles
from ..models import Book, BorrowDetail, BorrowSlip, FineHistory, Reader

router = APIRouter(prefix="/api/export", tags=["export"])


def _cell(value) -> str:
    s = "" if value is None else str(value)
    if any(ch in s for ch in ',"\r\n'):
        return '"' + s.replace('"', '""') + '"'
    return s


def _csv_response(filename: str, rows: list[list]) -> Response:
    lines = [",".join(_cell(cell) for cell in row) for row in rows]
    content = "\ufeff" + "\r\n".join(lines) + "\r\n"
    return Response(
        content=content.encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


def _fmt(value) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S") if value else ""


@router.get("/books.csv")
def export_books(
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "librarian")),
) -> Response:
    books = db.query(Book).order_by(Book.ma.asc()).all()
    rows = [["Mã", "Tên", "Tác giả", "Thể loại", "NXB", "Năm", "Số lượng"]]
    for book in books:
        rows.append(
            [
                book.ma,
                book.ten,
                book.tacGia,
                book.theLoai,
                book.nxb,
                book.namXb,
                book.soLuong,
            ]
        )
    filename = f"danh_sach_sach_{datetime.now():%Y%m%d_%H%M%S}.csv"
    return _csv_response(filename, rows)


@router.get("/borrows.csv")
def export_borrows(
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "librarian")),
) -> Response:
    now = datetime.now()
    slips = db.query(BorrowSlip).order_by(BorrowSlip.ngay_muon.desc()).all()
    rows = [
        [
            "Mã phiếu",
            "Mã độc giả",
            "Ngày mượn",
            "Hạn trả",
            "Ngày trả",
            "Trạng thái",
            "Số ngày quá hạn",
            "Phạt",
        ]
    ]
    for slip in slips:
        if slip.ngay_tra is not None:
            so_ngay_qua_han = max(0, (slip.ngay_tra.date() - slip.han_tra.date()).days)
            trang_thai = "Đã trả"
        else:
            so_ngay_qua_han = max(0, (now.date() - slip.han_tra.date()).days)
            trang_thai = "Đang mượn"
        fine = (
            db.query(func.coalesce(func.sum(FineHistory.so_tien), 0))
            .filter(FineHistory.ma_phieu == slip.ma_phieu)
            .scalar()
        )
        rows.append(
            [
                slip.ma_phieu,
                slip.ma_doc_gia,
                _fmt(slip.ngay_muon),
                _fmt(slip.han_tra),
                _fmt(slip.ngay_tra),
                trang_thai,
                so_ngay_qua_han,
                float(fine or 0),
            ]
        )
    filename = f"danh_sach_phieu_muon_{datetime.now():%Y%m%d_%H%M%S}.csv"
    return _csv_response(filename, rows)


@router.get("/report.csv")
def export_report(
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "librarian")),
) -> Response:
    rows: list[list] = []

    rows.append(["SÁCH MƯỢN NHIỀU"])
    rows.append(["Mã sách", "Tên sách", "Số lần mượn"])
    top_books = (
        db.query(
            BorrowDetail.ma_sach,
            Book.ten,
            func.count(BorrowDetail.ma_sach).label("so_lan"),
        )
        .join(Book, Book.ma == BorrowDetail.ma_sach)
        .group_by(BorrowDetail.ma_sach, Book.ten)
        .order_by(func.count(BorrowDetail.ma_sach).desc(), BorrowDetail.ma_sach.asc())
        .limit(10)
        .all()
    )
    for row in top_books:
        rows.append([row.ma_sach, row.ten, row.so_lan])
    rows.append([])

    rows.append(["ĐỘC GIẢ HOẠT ĐỘNG"])
    rows.append(["Mã độc giả", "Họ tên", "Số phiếu mượn"])
    top_readers = (
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
    for row in top_readers:
        rows.append([row.ma_doc_gia, row.hoTen, row.so_phieu])
    rows.append([])

    rows.append(["SÁCH QUÁ HẠN"])
    rows.append(
        [
            "Mã phiếu",
            "Mã sách",
            "Tên sách",
            "Mã độc giả",
            "Họ tên",
            "Số ngày quá hạn",
        ]
    )
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
    for slip, ho_ten in slips:
        details = (
            db.query(BorrowDetail.ma_sach, Book.ten)
            .join(Book, Book.ma == BorrowDetail.ma_sach)
            .filter(BorrowDetail.ma_phieu == slip.ma_phieu)
            .all()
        )
        so_ngay = max(0, (today - slip.han_tra.date()).days)
        for ma_sach, ten_sach in details:
            rows.append(
                [
                    slip.ma_phieu,
                    ma_sach,
                    ten_sach,
                    slip.ma_doc_gia,
                    ho_ten,
                    so_ngay,
                ]
            )

    filename = f"bao_cao_thong_ke_{datetime.now():%Y%m%d_%H%M%S}.csv"
    return _csv_response(filename, rows)
