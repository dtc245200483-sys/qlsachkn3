from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models import BorrowSlip, FineHistory


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _make_reader(client, token: str, ma: str = "TESTDG1", trang_thai: str = "hoat_dong") -> None:
    response = client.post(
        "/api/readers",
        json={
            "ma": ma,
            "hoTen": "Độc giả Test",
            "email": f"{ma}@example.com",
            "soDienThoai": "0900000000",
            "loaiDocGia": "sinh_vien",
            "trangThaiThe": trang_thai,
        },
        headers=_headers(token),
    )
    assert response.status_code == 200, response.text


def _make_book(client, token: str, ma: str = "TESTB1", so_luong: int = 5) -> None:
    response = client.post(
        "/api/books",
        json={
            "ma": ma,
            "ten": f"Sách {ma}",
            "tacGia": "Tác giả Test",
            "theLoai": "Test",
            "nxb": "NXB Test",
            "namXb": 2024,
            "soLuong": so_luong,
        },
        headers=_headers(token),
    )
    assert response.status_code == 200, response.text


def _borrow(client, token: str, ma_phieu: str = "PMTEST1", ma_doc_gia: str = "TESTDG1", items=None):
    return client.post(
        "/api/borrows",
        json={
            "ma_phieu": ma_phieu,
            "ma_doc_gia": ma_doc_gia,
            "items": items or [{"ma_sach": "TESTB1", "so_luong": 1}],
        },
        headers=_headers(token),
    )


def _set_han_tra(ma_phieu: str, days_ago: int) -> None:
    db = SessionLocal()
    try:
        slip = db.get(BorrowSlip, ma_phieu)
        assert slip is not None
        slip.han_tra = datetime.now() - timedelta(days=days_ago)
        db.commit()
    finally:
        db.close()


def _book_quantity(client, token: str, ma: str) -> int:
    books = client.get("/api/books", headers=_headers(token)).json()
    return next(b["soLuong"] for b in books if b["ma"] == ma)


def _fine_count(ma_phieu: str) -> int:
    db = SessionLocal()
    try:
        return db.query(FineHistory).filter(FineHistory.ma_phieu == ma_phieu).count()
    finally:
        db.close()


def test_borrow_success_creates_slip_and_decreases_stock(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["librarian"]
    _make_reader(client, tokens["admin"])
    _make_book(client, admin, "TESTB1", 5)

    response = _borrow(client, admin, "PMTEST1", items=[{"ma_sach": "TESTB1", "so_luong": 2}])
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["trang_thai"] == "dang_muon"
    assert data["so_lan_gia_han"] == 0
    assert data["details"][0]["ma_sach"] == "TESTB1"

    ngay_muon = datetime.fromisoformat(data["ngay_muon"])
    han_tra = datetime.fromisoformat(data["han_tra"])
    assert (han_tra - ngay_muon).days == 14
    assert _book_quantity(client, admin, "TESTB1") == 3

    listed = client.get("/api/borrows?docGia=TESTDG1", headers=_headers(admin))
    assert listed.status_code == 200
    assert any(s["ma_phieu"] == "PMTEST1" for s in listed.json())


def test_borrow_book_out_of_stock_fails(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["librarian"]
    _make_reader(client, tokens["admin"], "TESTDG2")
    _make_book(client, admin, "TESTB2", 0)

    response = _borrow(client, admin, "PMTEST2", ma_doc_gia="TESTDG2", items=[{"ma_sach": "TESTB2", "so_luong": 1}])
    assert response.status_code == 400

    _make_book(client, admin, "TESTB3", 1)
    not_enough = _borrow(
        client,
        admin,
        "PMTEST3",
        ma_doc_gia="TESTDG2",
        items=[{"ma_sach": "TESTB3", "so_luong": 2}],
    )
    assert not_enough.status_code == 400


def test_borrow_exceeds_max_books_at_once(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["librarian"]
    _make_reader(client, tokens["admin"], "TESTDG3")
    for i in range(4):
        _make_book(client, admin, f"TESTB4{i}", 5)

    response = _borrow(
        client,
        admin,
        "PMTEST4",
        ma_doc_gia="TESTDG3",
        items=[{"ma_sach": f"TESTB4{i}", "so_luong": 1} for i in range(4)],
    )
    assert response.status_code == 400


def test_borrow_locked_card_fails(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["librarian"]
    _make_reader(client, tokens["admin"], "TESTDG4", trang_thai="khoa")
    _make_book(client, admin, "TESTB5", 5)

    response = _borrow(client, admin, "PMTEST5", ma_doc_gia="TESTDG4", items=[{"ma_sach": "TESTB5", "so_luong": 1}])
    assert response.status_code == 400


def test_borrow_unknown_reader_and_duplicate_slip(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["librarian"]
    _make_book(client, admin, "TESTB6", 5)

    unknown = _borrow(client, admin, "PMTEST6", ma_doc_gia="KHONGTONTAI", items=[{"ma_sach": "TESTB6", "so_luong": 1}])
    assert unknown.status_code == 404

    _make_reader(client, tokens["admin"], "TESTDG5")
    first = _borrow(client, admin, "PMTEST7", ma_doc_gia="TESTDG5", items=[{"ma_sach": "TESTB6", "so_luong": 1}])
    assert first.status_code == 200
    duplicate = _borrow(client, admin, "PMTEST7", ma_doc_gia="TESTDG5", items=[{"ma_sach": "TESTB6", "so_luong": 1}])
    assert duplicate.status_code == 409


def test_return_on_time_restores_stock_and_no_fine(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["librarian"]
    _make_reader(client, tokens["admin"], "TESTDG6")
    _make_book(client, admin, "TESTB7", 4)
    _borrow(client, admin, "PMTEST8", ma_doc_gia="TESTDG6", items=[{"ma_sach": "TESTB7", "so_luong": 2}])

    returned = client.put("/api/borrows/PMTEST8/return", headers=_headers(admin))
    assert returned.status_code == 200, returned.text
    assert returned.json()["fine"] is None
    assert _book_quantity(client, admin, "TESTB7") == 4
    assert _fine_count("PMTEST8") == 0

    again = client.put("/api/borrows/PMTEST8/return", headers=_headers(admin))
    assert again.status_code == 400


def test_return_late_adds_fine_with_correct_formula(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["librarian"]
    _make_reader(client, tokens["admin"], "TESTDG7")
    _make_book(client, admin, "TESTB8", 3)
    _borrow(client, admin, "PMTEST9", ma_doc_gia="TESTDG7", items=[{"ma_sach": "TESTB8", "so_luong": 1}])
    _set_han_tra("PMTEST9", days_ago=5)

    returned = client.put("/api/borrows/PMTEST9/return", headers=_headers(admin))
    assert returned.status_code == 200, returned.text
    fine = returned.json()["fine"]
    assert fine["so_ngay_qua_han"] == 5
    assert fine["so_diem"] == 10
    assert _fine_count("PMTEST9") == 1


def test_renew_once_succeeds_and_twice_fails(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["librarian"]
    _make_reader(client, tokens["admin"], "TESTDG8")
    _make_book(client, admin, "TESTB9", 3)
    slip = _borrow(client, admin, "PMTEST10", ma_doc_gia="TESTDG8", items=[{"ma_sach": "TESTB9", "so_luong": 1}]).json()
    old_han_tra = datetime.fromisoformat(slip["han_tra"])

    renewed = client.put("/api/borrows/PMTEST10/renew", headers=_headers(admin))
    assert renewed.status_code == 200, renewed.text
    data = renewed.json()
    assert data["so_lan_gia_han"] == 1
    assert (datetime.fromisoformat(data["han_tra_moi"]) - old_han_tra).days == 14
    assert data["fine"] is None

    again = client.put("/api/borrows/PMTEST10/renew", headers=_headers(admin))
    assert again.status_code == 400


def test_renew_late_adds_fine(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["librarian"]
    _make_reader(client, tokens["admin"], "TESTDG9")
    _make_book(client, admin, "TESTB10", 3)
    _borrow(client, admin, "PMTEST11", ma_doc_gia="TESTDG9", items=[{"ma_sach": "TESTB10", "so_luong": 1}])
    _set_han_tra("PMTEST11", days_ago=3)

    renewed = client.put("/api/borrows/PMTEST11/renew", headers=_headers(admin))
    assert renewed.status_code == 200, renewed.text
    data = renewed.json()
    assert data["so_lan_gia_han"] == 1
    assert data["fine"]["so_ngay_qua_han"] == 3
    assert data["fine"]["so_diem"] == 6
    assert _fine_count("PMTEST11") == 1


def test_list_borrows_filters_and_permissions(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["librarian"]
    librarian = tokens["librarian"]
    reader = tokens["reader"]

    _make_reader(client, tokens["admin"], "TESTDG10")
    _make_book(client, admin, "TESTB11", 5)
    _borrow(client, librarian, "PMTEST12", ma_doc_gia="TESTDG10", items=[{"ma_sach": "TESTB11", "so_luong": 1}])
    _borrow(client, librarian, "PMTEST13", ma_doc_gia="TESTDG10", items=[{"ma_sach": "TESTB11", "so_luong": 1}])
    client.put("/api/borrows/PMTEST12/return", headers=_headers(librarian))

    active = client.get("/api/borrows?trangThai=dang_muon", headers=_headers(admin)).json()
    active_ids = [s["ma_phieu"] for s in active]
    assert "PMTEST13" in active_ids
    assert "PMTEST12" not in active_ids
    assert all(s["trang_thai"] == "dang_muon" for s in active)

    by_reader = client.get("/api/borrows?docGia=TESTDG10", headers=_headers(librarian)).json()
    assert {s["ma_phieu"] for s in by_reader} == {"PMTEST12", "PMTEST13"}

    assert client.post("/api/borrows", json={"ma_phieu": "PMTESTX", "ma_doc_gia": "TESTDG10", "items": []}, headers=_headers(reader)).status_code == 403
    assert client.get("/api/borrows", headers=_headers(reader)).status_code == 403
