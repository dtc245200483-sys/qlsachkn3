"""
Seed database QA riêng (LibraryDB_QA) cho agent QA.

Chạy:
    $env:DATABASE_URL='mssql+pyodbc://@localhost\QUANGHUNG/LibraryDB_QA?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes'
    python QA/backend/seed_qa_db.py

Dữ liệu seed đều có tiền tố QA* / QAS* / QADG* — không đụng dữ liệu thật.
Script idempotent: chạy lại không tạo trùng.
"""

import os
import sys
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKEND = os.path.join(ROOT, "Backend")
sys.path.insert(0, BACKEND)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.database import SessionLocal  # noqa: E402
from app.models import (  # noqa: E402
    AIConfig,
    Book,
    BorrowDetail,
    BorrowSlip,
    DatTruoc,
    FineHistory,
    LibraryConfig,
    Nxb,
    Reader,
    TheLoai,
    User,
)
from app.security import hash_password  # noqa: E402

PASSWORD = "Test@12345"


def _now() -> datetime:
    return datetime.now()


def seed_config(db):
    if db.get(LibraryConfig, 1) is None:
        db.add(
            LibraryConfig(
                id=1,
                max_borrow_days=14,
                overdue_fine_points_per_day=2,
                max_books_at_once=3,
            )
        )
    ai_cfg = db.get(AIConfig, 1)
    if ai_cfg is None:
        db.add(
            AIConfig(
                id=1,
                provider="openai",
                model="gpt-4o-mini",
                api_key="qa-placeholder-key",
                prompt_template=(
                    "Bạn là trợ lý tra cứu thư viện. Chỉ gợi ý sách có trong dữ liệu "
                    "được cung cấp. Không bịa mã sách hoặc tình trạng sách."
                ),
            )
        )
    else:
        ai_cfg.provider = "openai"
        ai_cfg.model = "gpt-4o-mini"
        ai_cfg.api_key = "qa-placeholder-key"
        ai_cfg.prompt_template = (
            "Bạn là trợ lý tra cứu thư viện. Chỉ gợi ý sách có trong dữ liệu "
            "được cung cấp. Không bịa mã sách hoặc tình trạng sách."
        )
    db.commit()


def seed_catalog(db):
    for ma, ten in [("QATL1", "Công nghệ QA"), ("QATL2", "Lịch sử QA"), ("QATL3", "Văn học QA")]:
        if db.get(TheLoai, ma) is None:
            db.add(TheLoai(ma=ma, ten=ten))
    if db.get(Nxb, "QANX1") is None:
        db.add(Nxb(ma="QANX1", ten="NXB QA Test"))
    db.commit()


def seed_books(db):
    books = [
        ("QAS001", "QA Python căn bản", "QA Tác giả 1", "Công nghệ QA", "NXB QA Test", 2024, 1),
        ("QAS002", "QA Thuật toán nâng cao", "QA Tác giả 2", "Công nghệ QA", "NXB QA Test", 2023, 1),
        ("QAS003", "QA Lịch sử hiện đại", "QA Tác giả 3", "Lịch sử QA", "NXB QA Test", 2020, 0),
        ("QAS004", "QA Văn học kinh điển", "QA Tác giả 4", "Văn học QA", "NXB QA Test", 1999, 3),
        ("QAS005", "QA Cơ sở dữ liệu", "QA Tác giả 5", "Công nghệ QA", "NXB QA Test", 2025, 5),
    ]
    the_loai_map = {b.ten: b.ma for b in db.query(TheLoai).all()}
    nxb_map = {b.ten: b.ma for b in db.query(Nxb).all()}
    for ma, ten, tac_gia, the_loai, nxb, nam, so_luong in books:
        if db.get(Book, ma) is None:
            db.add(
                Book(
                    ma=ma,
                    ten=ten,
                    tacGia=tac_gia,
                    theLoai=the_loai,
                    nxb=nxb,
                    namXb=nam,
                    soLuong=so_luong,
                    theLoaiId=the_loai_map.get(the_loai),
                    nxbId=nxb_map.get(nxb),
                )
            )
    db.commit()


def seed_readers(db):
    readers = [
        ("QADG01", "Nguyễn Văn QA1", "DTC901000001@ictu.edu.vn", "0900000001", "sinh_vien", "hoat_dong"),
        ("QADG02", "Trần Thị QA2", "DTC901000002@ictu.edu.vn", "0900000002", "sinh_vien", "hoat_dong"),
        ("QADG03", "Lê Văn QA3", "DTC901000003@ictu.edu.vn", "0900000003", "giang_vien", "khoa"),
    ]
    for ma, ho_ten, email, sdt, loai, trang_thai in readers:
        if db.get(Reader, ma) is None:
            db.add(
                Reader(
                    ma=ma,
                    hoTen=ho_ten,
                    email=email,
                    soDienThoai=sdt,
                    loaiDocGia=loai,
                    trangThaiThe=trang_thai,
                    diem_svnet=100,
                    ngayTao=_now(),
                )
            )
    db.commit()


def seed_users(db):
    users = [
        ("qa_admin", "admin", None, "DTC901000101@ictu.edu.vn", "0910000101"),
        ("qa_librarian", "librarian", None, "DTC901000102@ictu.edu.vn", "0910000102"),
        ("qa_reader1", "reader", "QADG01", "DTC901000001@ictu.edu.vn", "0900000001"),
        ("qa_reader2", "reader", "QADG02", "DTC901000002@ictu.edu.vn", "0900000002"),
    ]
    for username, role, reader_id, email, sdt in users:
        if db.query(User).filter(User.username == username).first() is None:
            db.add(
                User(
                    username=username,
                    password_hash=hash_password(PASSWORD),
                    ho_ten=username,
                    email=email,
                    so_dien_thoai=sdt,
                    role=role,
                    reader_id=reader_id,
                    is_active=True,
                )
            )
    db.commit()


def seed_slips(db):
    now = _now()
    points_per_day = 2
    slips = [
        # (ma_phieu, ma_doc_gia, ma_sach, so_luong, muon_off, han_off, tra_off)
        # QAPM01: đang mượn, sắp hết hạn (còn 2 ngày) -> thông báo SAP_HET_HAN
        ("QAPM01", "QADG01", "QAS004", 1, -12, 2, None),
        # QAPM02: đang mượn, quá hạn 2 ngày -> thông báo QUA_HAN + phạt khi trả
        ("QAPM02", "QADG02", "QAS001", 1, -16, -2, None),
        # QAPM03: đã trả đúng hạn, không phạt
        ("QAPM03", "QADG02", "QAS004", 1, -20, -6, -8),
        # QAPM04: đã trả trễ 2 ngày -> có FineHistory
        ("QAPM04", "QADG01", "QAS002", 1, -20, -8, -6),
        # QAPM06: đang mượn, quá hạn 2 ngày (dành test gia hạn trễ)
        ("QAPM06", "QADG01", "QAS005", 1, -16, -2, None),
        # QAPM07: đang mượn, quá hạn 2 ngày (dành test trả trễ)
        ("QAPM07", "QADG01", "QAS004", 1, -16, -2, None),
    ]
    for ma_phieu, ma_doc_gia, ma_sach, so_luong, muon_off, han_off, tra_off in slips:
        if db.get(BorrowSlip, ma_phieu) is not None:
            continue
        ngay_muon = now + timedelta(days=muon_off)
        han_tra = now + timedelta(days=han_off)
        ngay_tra = now + timedelta(days=tra_off) if tra_off is not None else None
        db.add(
            BorrowSlip(
                ma_phieu=ma_phieu,
                ma_doc_gia=ma_doc_gia,
                ngay_muon=ngay_muon,
                han_tra=han_tra,
                ngay_tra=ngay_tra,
                trang_thai="da_tra" if tra_off is not None else "dang_muon",
                so_lan_gia_han=0,
            )
        )
        db.add(
            BorrowDetail(
                ma_phieu=ma_phieu,
                ma_sach=ma_sach,
                so_luong=so_luong,
                ngay_tra_chi_tiet=ngay_tra,
            )
        )
        book = db.get(Book, ma_sach)
        if tra_off is None and book is not None:
            book.soLuong = max(0, book.soLuong - so_luong)
        if ma_phieu == "QAPM04":
            db.add(
                FineHistory(
                    ma_phieu=ma_phieu,
                    ma_doc_gia=ma_doc_gia,
                    so_ngay_qua_han=2,
                    so_diem=2 * points_per_day,
                    ngay_tinh=ngay_tra,
                )
            )
    db.commit()


def seed_reservations(db):
    now = _now()
    rows = [
        # (ma_dat, ma_sach, ma_doc_gia, ngay_dat_off, ngay_xu_ly_off, trang_thai)
        ("RVQA01", "QAS001", "QADG02", -1, None, "CHO_XU_LY"),
        ("RVQA02", "QAS003", "QADG01", -1, None, "CHO_XU_LY"),
        ("RVQA03", "QAS001", "QADG01", -2, -1, "SAN_SANG"),
    ]
    for ma_dat, ma_sach, ma_doc_gia, dat_off, xu_ly_off, trang_thai in rows:
        if db.get(DatTruoc, ma_dat) is not None:
            continue
        db.add(
            DatTruoc(
                ma_dat=ma_dat,
                ma_sach=ma_sach,
                ma_doc_gia=ma_doc_gia,
                ngay_dat=now + timedelta(days=dat_off),
                trang_thai=trang_thai,
                ngay_xu_ly=(
                    now + timedelta(days=xu_ly_off)
                    if xu_ly_off is not None
                    else None
                ),
            )
        )
    db.commit()


def main():
    print("== SEED DB QA (LibraryDB_QA) ==")
    db = SessionLocal()
    try:
        seed_config(db)
        seed_catalog(db)
        seed_books(db)
        seed_readers(db)
        seed_users(db)
        seed_slips(db)
        seed_reservations(db)
    finally:
        db.close()
    print("Xong. Tài khoản: qa_admin / qa_librarian / qa_reader1 / qa_reader2 — mật khẩu Test@12345")


if __name__ == "__main__":
    main()
