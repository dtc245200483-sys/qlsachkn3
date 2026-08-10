from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models import BorrowSlip
from tests.helpers import next_test_email

_seq = 0


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _register(client, username: str):
    return client.post(
        "/api/auth/register",
        json={
            "username": username,
            "password": "Pass@123",
            "hoTen": "Độc giả Thống kê",
            "email": next_test_email(),
            "soDienThoai": "0911111111",
            "loaiDocGia": "sinh_vien",
        },
    )


def _make_book(client, token: str, ma: str) -> None:
    existing = client.get("/api/books", headers=_headers(token)).json()
    if any(b["ma"] == ma for b in existing):
        return
    response = client.post(
        "/api/books",
        json={
            "ma": ma,
            "ten": f"Sách {ma}",
            "tacGia": "Tác giả Test",
            "theLoai": "Test",
            "nxb": "NXB Test",
            "namXb": 2024,
            "soLuong": 10,
        },
        headers=_headers(token),
    )
    assert response.status_code == 200, response.text


def _borrow(client, token: str, ma_phieu: str, reader_ma: str, book_ma: str) -> None:
    response = client.post(
        "/api/borrows",
        json={
            "ma_phieu": ma_phieu,
            "ma_doc_gia": reader_ma,
            "items": [{"ma_sach": book_ma, "so_luong": 1}],
        },
        headers=_headers(token),
    )
    assert response.status_code == 200, response.text


def _set_han_tra(ma_phieu: str, days_offset: int) -> None:
    db = SessionLocal()
    try:
        slip = db.get(BorrowSlip, ma_phieu)
        assert slip is not None
        slip.han_tra = datetime.now() + timedelta(days=days_offset)
        db.commit()
    finally:
        db.close()


def test_top_books_order_and_limit(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    admin = tokens["admin"]
    reader = _register(client, "tmp_backend_test_stats1").json()
    _make_book(client, staff, "TESTSTT1")
    _make_book(client, staff, "TESTSTT2")

    _borrow(client, staff, "PMSTT1", reader["reader_ma"], "TESTSTT1")
    _borrow(client, staff, "PMSTT2", reader["reader_ma"], "TESTSTT1")
    _borrow(client, staff, "PMSTT3", reader["reader_ma"], "TESTSTT2")

    top = client.get("/api/stats/top-books", headers=_headers(admin)).json()
    by_ma = {row["ma_sach"]: row for row in top}
    assert by_ma["TESTSTT1"]["so_lan_muon"] == 2
    assert by_ma["TESTSTT2"]["so_lan_muon"] == 1
    assert top.index(by_ma["TESTSTT1"]) < top.index(by_ma["TESTSTT2"])

    limited = client.get(
        "/api/stats/top-books?limit=1",
        headers=_headers(staff),
    ).json()
    assert len(limited) == 1
    assert limited[0]["ma_sach"] == "TESTSTT1"


def test_top_readers_order(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader_x = _register(client, "tmp_backend_test_statsx").json()
    reader_y = _register(client, "tmp_backend_test_statsy").json()
    _make_book(client, staff, "TESTSTT3")

    _borrow(client, staff, "PMSTT4", reader_x["reader_ma"], "TESTSTT3")
    _borrow(client, staff, "PMSTT5", reader_x["reader_ma"], "TESTSTT3")
    _borrow(client, staff, "PMSTT6", reader_y["reader_ma"], "TESTSTT3")

    top = client.get("/api/stats/top-readers", headers=_headers(staff)).json()
    by_ma = {row["ma_doc_gia"]: row for row in top}
    assert by_ma[reader_x["reader_ma"]]["so_phieu_muon"] == 2
    assert by_ma[reader_x["reader_ma"]]["ho_ten"] == "Độc giả Thống kê"
    assert by_ma[reader_y["reader_ma"]]["so_phieu_muon"] == 1
    assert top.index(by_ma[reader_x["reader_ma"]]) < top.index(by_ma[reader_y["reader_ma"]])


def test_overdue_books_only_active_overdue_slips(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_statso").json()
    _make_book(client, staff, "TESTSTT4")

    _borrow(client, staff, "PMSTT7", reader["reader_ma"], "TESTSTT4")
    _set_han_tra("PMSTT7", days_offset=-3)
    _borrow(client, staff, "PMSTT8", reader["reader_ma"], "TESTSTT4")
    _set_han_tra("PMSTT8", days_offset=-5)
    client.put("/api/borrows/PMSTT8/return", headers=_headers(staff))
    _borrow(client, staff, "PMSTT9", reader["reader_ma"], "TESTSTT4")
    _set_han_tra("PMSTT9", days_offset=5)

    overdue = client.get("/api/stats/overdue-books", headers=_headers(staff)).json()
    rows = [r for r in overdue if r["ma_phieu"].startswith("PMSTT")]
    assert any(
        r["ma_phieu"] == "PMSTT7"
        and r["ma_sach"] == "TESTSTT4"
        and r["ten_sach"] == "Sách TESTSTT4"
        and r["ho_ten"] == "Độc giả Thống kê"
        and r["so_ngay_qua_han"] == 3
        for r in rows
    )
    assert not any(r["ma_phieu"] == "PMSTT8" for r in rows)
    assert not any(r["ma_phieu"] == "PMSTT9" for r in rows)


def test_stats_permissions(client_and_tokens):
    client, tokens = client_and_tokens
    reader = tokens["reader"]
    assert client.get("/api/stats/top-books", headers=_headers(reader)).status_code == 403
    assert client.get("/api/stats/top-readers", headers=_headers(reader)).status_code == 403
    assert client.get("/api/stats/overdue-books", headers=_headers(reader)).status_code == 403
    assert client.get("/api/stats/top-books", headers=_headers(tokens["librarian"])).status_code == 200
    assert client.get("/api/stats/top-books", headers=_headers(tokens["admin"])).status_code == 200
