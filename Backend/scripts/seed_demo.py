"""
Seed dữ liệu mẫu DEMO — Hệ thống quản lý thư viện.

Cách chạy (Backend phải đang chạy để tạo tài khoản qua API register):
    cd Backend
    python scripts/seed_demo.py                # seed + in tóm tắt
    python scripts/seed_demo.py --verify       # seed + gọi API xác minh

Idempotent: chạy lại không đè/không trùng dữ liệu.
"""

import os
import sys
import unicodedata
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from app.database import SessionLocal  # noqa: E402
from app.models import (  # noqa: E402
    Book,
    BorrowDetail,
    BorrowSlip,
    DatTruoc,
    FineHistory,
    LibraryConfig,
    Reader,
    TheLoai,
    Nxb,
    User,
)

BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

VIET_MAP = str.maketrans({"đ": "d", "Đ": "D"})


def _ascii_name(name: str) -> str:
    normalized = unicodedata.normalize("NFD", name)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn").translate(VIET_MAP)


def _email_from_name(name: str) -> str:
    """Email ICTU lấy theo tên người: 'Nguyễn Văn An' -> nguyenvanan@ictu.edu.vn."""
    return "".join(_ascii_name(name).lower().split()) + "@ictu.edu.vn"

DEMO_BOOKS = [
    {
        "ma": "S001",
        "ten": "Nhập môn trí tuệ nhân tạo",
        "tacGia": "Nguyễn Văn A",
        "theLoai": "Công nghệ",
        "nxb": "NXB Giáo dục",
        "namXb": 2023,
        "soLuong": 5,
    },
    {
        "ma": "S002",
        "ten": "Lập trình Python cơ bản",
        "tacGia": "Trần Thị B",
        "theLoai": "Công nghệ",
        "nxb": "NXB Đại học Quốc gia",
        "namXb": 2022,
        "soLuong": 5,
    },
    {
        "ma": "S003",
        "ten": "Cấu trúc dữ liệu và giải thuật",
        "tacGia": "Lê Minh Cường",
        "theLoai": "Công nghệ",
        "nxb": "NXB Bách khoa",
        "namXb": 2021,
        "soLuong": 4,
    },
    {
        "ma": "S004",
        "ten": "Người xa lạ",
        "tacGia": "Albert Camus",
        "theLoai": "Văn học",
        "nxb": "NXB Văn học",
        "namXb": 1942,
        "soLuong": 3,
    },
    {
        "ma": "S005",
        "ten": "Lịch sử Việt Nam hiện đại",
        "tacGia": "Phan Văn D",
        "theLoai": "Lịch sử",
        "nxb": "NXB Chính trị quốc gia",
        "namXb": 2019,
        "soLuong": 2,
    },
]

DEMO_READERS = [
    {
        "ma": "DG001",
        "hoTen": "Nguyễn Văn An",
        "email": "nguyenvanan@ictu.edu.vn",
        "soDienThoai": "0912345001",
        "loaiDocGia": "sinh_vien",
        "trangThaiThe": "hoat_dong",
    },
    {
        "ma": "DG002",
        "hoTen": "Trần Thị Bích",
        "email": "tranthibich@ictu.edu.vn",
        "soDienThoai": "0912345002",
        "loaiDocGia": "sinh_vien",
        "trangThaiThe": "hoat_dong",
    },
    {
        "ma": "DG003",
        "hoTen": "Lê Minh Cường",
        "email": "leminhcuong@ictu.edu.vn",
        "soDienThoai": "0912345003",
        "loaiDocGia": "giang_vien",
        "trangThaiThe": "hoat_dong",
    },
]

# (ma_phieu, ma_doc_gia, ngay_muon_offset, han_tra_offset, ngay_tra_offset, ma_sach, trang_thai)
DEMO_SLIPS = [
    ("PM001", "DG001", -6, 8, None, "S001", "dang_muon"),
    ("PM002", "DG002", -20, -6, -6, "S002", "da_tra"),
    ("PM003", "DG002", -20, -8, -6, "S003", "da_tra"),
    ("PM004", "DG001", -12, 2, None, "S004", "dang_muon"),
]

DEMO_RESERVATIONS = [
    {
        "ma_dat": "RV001",
        "ma_sach": "S002",
        "ma_doc_gia": "DG001",
        "ngay_dat_offset": -3,
        "ngay_xu_ly_offset": -1,
        "trang_thai": "SAN_SANG",
    },
]

DEMO_ACCOUNTS = [
    {
        "username": "docgia1",
        "password": "docgia1",
        "ho_ten": "Nguyễn Văn An",
        "email": "nguyenvanan@ictu.edu.vn",
        "reader_ma": "DG001",
    },
    {
        "username": "docgia2",
        "password": "docgia2",
        "ho_ten": "Trần Thị Bích",
        "email": "tranthibich@ictu.edu.vn",
        "reader_ma": "DG002",
    },
]

# SĐT mặc định cho các tài khoản cũ chưa có (email tự sinh theo tên người).
DEMO_USER_CONTACTS_PHONES = {
    "admin": "0912345001",
    "librarian": "0912345002",
    "reader": "0912345003",
    "docgia1": "0912345004",
    "docgia2": "0912345005",
}


def _now() -> datetime:
    return datetime.now()


def _delete_orphan_reader(db, reader_ma: str | None) -> None:
    if not reader_ma:
        return
    reader = db.get(Reader, reader_ma)
    if reader is None:
        return
    has_slip = (
        db.query(BorrowSlip).filter(BorrowSlip.ma_doc_gia == reader_ma).first()
        is not None
    )
    has_res = (
        db.query(DatTruoc).filter(DatTruoc.ma_doc_gia == reader_ma).first()
        is not None
    )
    has_user = (
        db.query(User).filter(User.reader_id == reader_ma).first() is not None
    )
    if not has_slip and not has_res and not has_user:
        db.delete(reader)
        db.commit()


def seed_books(db) -> list[str]:
    created = []
    for data in DEMO_BOOKS:
        if db.get(Book, data["ma"]) is not None:
            continue
        the_loai = db.query(TheLoai).filter(TheLoai.ten == data["theLoai"]).first()
        nxb = db.query(Nxb).filter(Nxb.ten == data["nxb"]).first()
        db.add(
            Book(
                ma=data["ma"],
                ten=data["ten"],
                tacGia=data["tacGia"],
                theLoai=data["theLoai"],
                nxb=data["nxb"],
                namXb=data["namXb"],
                soLuong=data["soLuong"],
                theLoaiId=the_loai.ma if the_loai else None,
                nxbId=nxb.ma if nxb else None,
            )
        )
        created.append(data["ma"])
    db.commit()
    return created


def seed_readers(db) -> list[str]:
    created = []
    for data in DEMO_READERS:
        existing = db.get(Reader, data["ma"])
        if existing is not None:
            if existing.email != data["email"]:
                existing.email = data["email"]
            continue
        db.add(
            Reader(
                ma=data["ma"],
                hoTen=data["hoTen"],
                email=data["email"],
                soDienThoai=data["soDienThoai"],
                loaiDocGia=data["loaiDocGia"],
                trangThaiThe=data["trangThaiThe"],
                ngayTao=_now(),
            )
        )
        created.append(data["ma"])
    db.commit()
    return created


def seed_slips_and_fines(db) -> tuple[list[str], list[str]]:
    cfg = db.get(LibraryConfig, 1)
    fine_per_day = cfg.overdue_fine_points_per_day if cfg else 2
    now = _now()
    created_slips: list[str] = []
    created_fines: list[str] = []

    for ma_phieu, ma_doc_gia, muon_off, han_off, tra_off, ma_sach, trang_thai in DEMO_SLIPS:
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
                trang_thai=trang_thai,
                so_lan_gia_han=0,
            )
        )
        db.add(
            BorrowDetail(
                ma_phieu=ma_phieu,
                ma_sach=ma_sach,
                so_luong=1,
                ngay_tra_chi_tiet=ngay_tra,
            )
        )
        book = db.get(Book, ma_sach)
        if trang_thai == "dang_muon" and book is not None:
            book.soLuong = max(0, book.soLuong - 1)
        if ma_phieu == "PM003":
            so_ngay_qua_han = 2
            db.add(
                FineHistory(
                    ma_phieu=ma_phieu,
                    ma_doc_gia=ma_doc_gia,
                    so_ngay_qua_han=so_ngay_qua_han,
                    so_diem=so_ngay_qua_han * fine_per_day,
                    ngay_tinh=ngay_tra,
                )
            )
            created_fines.append(ma_phieu)
        created_slips.append(ma_phieu)

    db.commit()
    return created_slips, created_fines


def seed_reservations(db) -> list[str]:
    now = _now()
    created = []
    for data in DEMO_RESERVATIONS:
        if db.get(DatTruoc, data["ma_dat"]) is not None:
            continue
        db.add(
            DatTruoc(
                ma_dat=data["ma_dat"],
                ma_sach=data["ma_sach"],
                ma_doc_gia=data["ma_doc_gia"],
                ngay_dat=now + timedelta(days=data["ngay_dat_offset"]),
                trang_thai=data["trang_thai"],
                ngay_xu_ly=(
                    now + timedelta(days=data["ngay_xu_ly_offset"])
                    if data["ngay_xu_ly_offset"] is not None
                    else None
                ),
            )
        )
        created.append(data["ma_dat"])
    db.commit()
    return created


def seed_accounts(db) -> list[str]:
    import httpx

    # Dọn reader tự động do register tạo nhưng không còn liên kết (chạy lại an toàn).
    for account in DEMO_ACCOUNTS:
        orphan = db.query(Reader).filter(Reader.email == account["email"]).first()
        if orphan is not None and orphan.ma != account["reader_ma"]:
            _delete_orphan_reader(db, orphan.ma)

    results = []
    for account in DEMO_ACCOUNTS:
        user = db.query(User).filter(User.username == account["username"]).first()
        if user is not None:
            old_ma = user.reader_id
            if user.reader_id != account["reader_ma"]:
                user.reader_id = account["reader_ma"]
                db.commit()
                _delete_orphan_reader(db, old_ma)
            results.append(f"SKIP {account['username']} (đã tồn tại)")
            continue
        try:
            resp = httpx.post(
                f"{BASE_URL}/api/auth/register",
                json={
                    "username": account["username"],
                    "password": account["password"],
                    "hoTen": account["ho_ten"],
                    "email": account["email"],
                    "soDienThoai": "0912345004",
                    "loaiDocGia": "sinh_vien",
                },
                timeout=15,
            )
        except Exception as exc:  # noqa: BLE001
            results.append(f"ERROR {account['username']} (backend không chạy?): {exc}")
            continue
        if resp.status_code != 200:
            results.append(
                f"ERROR {account['username']}: HTTP {resp.status_code} {resp.text}"
            )
            continue
        data = resp.json()
        user = db.query(User).filter(User.username == account["username"]).first()
        auto_ma = data.get("reader_ma")
        if user is not None:
            user.reader_id = account["reader_ma"]
            db.commit()
        _delete_orphan_reader(db, auto_ma)
        results.append(f"CREATED {account['username']} -> {account['reader_ma']}")
    return results


def seed_user_contacts(db) -> list[str]:
    """Điền email theo tên người + SĐT cho tài khoản cũ (idempotent, không ghi đè SĐT đã có)."""
    updated = []
    for username, phone in DEMO_USER_CONTACTS_PHONES.items():
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            continue
        email = _email_from_name(user.ho_ten)
        changed = False
        if user.email != email:
            user.email = email
            changed = True
        if not (user.so_dien_thoai or "").strip():
            user.so_dien_thoai = phone
            changed = True
        if user.reader_id:
            reader = db.get(Reader, user.reader_id)
            if reader is not None and reader.email != email:
                reader.email = email
                changed = True
        if changed:
            updated.append(username)
    db.commit()
    return updated


def verify() -> None:
    import httpx

    from app.security import create_access_token

    admin_token = create_access_token("admin", "admin", "Quản trị viên")
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    librarian_token = create_access_token("librarian", "librarian", "Thủ thư")
    headers_librarian = {"Authorization": f"Bearer {librarian_token}"}
    reader_token = create_access_token("docgia1", "reader", "docgia1")
    headers_reader = {"Authorization": f"Bearer {reader_token}"}

    with httpx.Client(base_url=BASE_URL, timeout=15) as client:
        checks = [
            ("/api/books", headers_admin),
            ("/api/readers", headers_admin),
            ("/api/borrows", headers_librarian),
            ("/api/stats/top-books", headers_admin),
            ("/api/stats/top-readers", headers_admin),
            ("/api/stats/overdue-books", headers_admin),
            ("/api/notifications", headers_reader),
        ]
        print("\n== XÁC MINH API ==")
        for path, headers in checks:
            resp = client.get(path, headers=headers)
            count = len(resp.json()) if resp.status_code == 200 and isinstance(resp.json(), list) else "?"
            print(f"{path}: HTTP {resp.status_code} — {count} dòng")


def main() -> None:
    print("== SEED DỮ LIỆU DEMO (idempotent) ==")
    db = SessionLocal()
    try:
        created_books = seed_books(db)
        created_readers = seed_readers(db)
        created_slips, created_fines = seed_slips_and_fines(db)
        created_res = seed_reservations(db)
        account_results = seed_accounts(db)
        updated_contacts = seed_user_contacts(db)
    finally:
        db.close()

    print(f"Sách tạo mới: {created_books or 'không (đã có S001–S005)'}")
    print(f"Độc giả tạo mới: {created_readers or 'không (đã có DG001–DG003)'}")
    print(f"Phiếu mượn tạo mới: {created_slips or 'không (đã có PM001–PM004)'}")
    print(f"FineHistory tạo mới: {created_fines or 'không'}")
    print(f"Đặt trước tạo mới: {created_res or 'không (đã có RV001–RV002)'}")
    for result in account_results:
        print(f"Tài khoản: {result}")
    print(f"Email/SĐT đã điền cho tài khoản cũ: {updated_contacts or 'không (đã có đủ)'}")

    if "--verify" in sys.argv:
        verify()

    print("\nTài khoản demo: docgia1/docgia1 (DG001), docgia2/docgia2 (DG002)")


if __name__ == "__main__":
    main()
