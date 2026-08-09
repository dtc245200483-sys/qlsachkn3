from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models import BorrowSlip

_seq = 0


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _register(client, username: str):
    return client.post(
        "/api/auth/register",
        json={
            "username": username,
            "password": "Pass@123",
            "hoTen": "Độc giả Thông báo",
            "email": f"{username}@example.com",
            "soDienThoai": "0911111111",
            "loaiDocGia": "sinh_vien",
        },
    )


def _make_book(client, token: str, ma: str, so_luong: int = 5) -> None:
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
            "soLuong": so_luong,
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


def _notifications(client, token: str) -> list:
    response = client.get("/api/notifications", headers=_headers(token))
    assert response.status_code == 200, response.text
    return response.json()


def test_returned_slip_not_reminded_and_only_own(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader_a = _register(client, "tmp_backend_test_ntf1a").json()
    reader_b = _register(client, "tmp_backend_test_ntf1b").json()
    _make_book(client, staff, "TESTNTF1", 3)

    _borrow(client, staff, "PMNTF1", reader_a["reader_ma"], "TESTNTF1")
    client.put("/api/borrows/PMNTF1/return", headers=_headers(staff))
    assert _notifications(client, reader_a["token"]) == []

    _borrow(client, staff, "PMNTF2", reader_a["reader_ma"], "TESTNTF1")
    _set_han_tra("PMNTF2", days_offset=2)

    mine = _notifications(client, reader_a["token"])
    assert any(
        n["id"] == "BORROW:PMNTF2" and n["loai"] == "SAP_HET_HAN" and n["da_doc"] is False
        for n in mine
    )
    assert _notifications(client, reader_b["token"]) == []


def test_near_due_and_overdue_slips_appear(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_ntf2").json()
    _make_book(client, staff, "TESTNTF2", 5)

    _borrow(client, staff, "PMNTF3", reader["reader_ma"], "TESTNTF2")
    _set_han_tra("PMNTF3", days_offset=2)
    _borrow(client, staff, "PMNTF4", reader["reader_ma"], "TESTNTF2")
    _set_han_tra("PMNTF4", days_offset=-3)
    _borrow(client, staff, "PMNTF5", reader["reader_ma"], "TESTNTF2")
    _set_han_tra("PMNTF5", days_offset=10)

    items = _notifications(client, reader["token"])
    by_id = {n["id"]: n for n in items}
    assert by_id["BORROW:PMNTF3"]["loai"] == "SAP_HET_HAN"
    assert by_id["BORROW:PMNTF4"]["loai"] == "QUA_HAN"
    assert "đã quá hạn 3 ngày" in by_id["BORROW:PMNTF4"]["noi_dung"]
    assert "BORROW:PMNTF5" not in by_id


def test_san_sang_reservation_notification(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    borrower = _register(client, "tmp_backend_test_ntf3bor").json()
    reader_a = _register(client, "tmp_backend_test_ntf3a").json()
    reader_b = _register(client, "tmp_backend_test_ntf3b").json()
    _make_book(client, staff, "TESTNTF3", 1)

    _borrow(client, staff, "PMNTF6", borrower["reader_ma"], "TESTNTF3")
    reservation = client.post(
        "/api/reservations",
        json={"ma_sach": "TESTNTF3"},
        headers=_headers(reader_a["token"]),
    ).json()
    fulfilled = client.put(
        f"/api/reservations/{reservation['ma_dat']}/fulfill",
        headers=_headers(staff),
    )
    assert fulfilled.status_code == 200

    mine = _notifications(client, reader_a["token"])
    ready = [n for n in mine if n["loai"] == "SACH_SAN_SANG"]
    assert any(n["id"] == f"RES:{reservation['ma_dat']}" for n in ready)
    assert all(n["da_doc"] is False for n in ready)

    other = _notifications(client, reader_b["token"])
    assert not any(n["loai"] == "SACH_SAN_SANG" for n in other)


def test_notifications_permissions(client_and_tokens):
    client, tokens = client_and_tokens
    assert client.get("/api/notifications", headers=_headers(tokens["librarian"])).status_code == 403
    assert client.get("/api/notifications", headers=_headers(tokens["admin"])).status_code == 403
    assert client.get("/api/notifications", headers=_headers(tokens["reader"])).status_code == 403
