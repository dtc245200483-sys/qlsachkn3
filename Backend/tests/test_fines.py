from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models import BorrowSlip


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _register(client, username: str):
    return client.post(
        "/api/auth/register",
        json={
            "username": username,
            "password": "Pass@123",
            "hoTen": "Độc giả Thu phạt",
            "email": f"{username}@ictu.edu.vn",
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
            "soLuong": 5,
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


def _fines_of(client, token: str, reader_ma: str, ma_phieu: str) -> list:
    slips = client.get(
        "/api/borrows",
        params={"docGia": reader_ma},
        headers=_headers(token),
    ).json()
    slip = next(s for s in slips if s["ma_phieu"] == ma_phieu)
    return slip["fines"]


def test_collect_fine_success_and_shows_da_thu(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_fine1").json()
    _make_book(client, staff, "TESTFINE1")
    _borrow(client, staff, "PMFINE1", reader["reader_ma"], "TESTFINE1")
    _set_han_tra("PMFINE1", days_offset=-3)
    client.put("/api/borrows/PMFINE1/return", headers=_headers(staff))

    before = _fines_of(client, staff, reader["reader_ma"], "PMFINE1")
    assert before[0]["da_thu"] is False
    assert before[0]["ngay_thu"] is None
    assert before[0]["so_diem"] == 6

    collected = client.post(
        "/api/borrows/PMFINE1/collect-fine",
        headers=_headers(staff),
    )
    assert collected.status_code == 200, collected.text
    data = collected.json()
    assert data["message"] == "Đã trừ điểm SVNET."
    assert data["so_diem_da_thu"] == 6
    assert data["diem_con_lai"] == 94
    assert data["ngay_thu"] is not None

    after = _fines_of(client, staff, reader["reader_ma"], "PMFINE1")
    assert after[0]["da_thu"] is True
    assert after[0]["ngay_thu"] is not None

    readers = client.get(
        "/api/readers",
        params={"q": reader["reader_ma"]},
        headers=_headers(staff),
    ).json()
    assert readers[0]["diem_svnet"] == 94


def test_collect_fine_twice_fails(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_fine2").json()
    _make_book(client, staff, "TESTFINE2")
    _borrow(client, staff, "PMFINE2", reader["reader_ma"], "TESTFINE2")
    _set_han_tra("PMFINE2", days_offset=-2)
    client.put("/api/borrows/PMFINE2/return", headers=_headers(staff))

    assert client.post(
        "/api/borrows/PMFINE2/collect-fine",
        headers=_headers(staff),
    ).status_code == 200
    again = client.post(
        "/api/borrows/PMFINE2/collect-fine",
        headers=_headers(staff),
    )
    assert again.status_code == 400
    assert "Không có phạt để thu" in again.json()["detail"]


def test_collect_fine_not_returned_fails(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_fine3").json()
    _make_book(client, staff, "TESTFINE3")
    _borrow(client, staff, "PMFINE3", reader["reader_ma"], "TESTFINE3")
    _set_han_tra("PMFINE3", days_offset=-4)

    response = client.post(
        "/api/borrows/PMFINE3/collect-fine",
        headers=_headers(staff),
    )
    assert response.status_code == 400
    assert "chưa trả" in response.json()["detail"]


def test_collect_fine_no_fine_fails(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_fine4").json()
    _make_book(client, staff, "TESTFINE4")
    _borrow(client, staff, "PMFINE4", reader["reader_ma"], "TESTFINE4")
    client.put("/api/borrows/PMFINE4/return", headers=_headers(staff))

    response = client.post(
        "/api/borrows/PMFINE4/collect-fine",
        headers=_headers(staff),
    )
    assert response.status_code == 400
    assert "Không có phạt để thu" in response.json()["detail"]


def test_collect_fine_permissions(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_fine5").json()
    _make_book(client, staff, "TESTFINE5")
    _borrow(client, staff, "PMFINE5", reader["reader_ma"], "TESTFINE5")
    _set_han_tra("PMFINE5", days_offset=-1)
    client.put("/api/borrows/PMFINE5/return", headers=_headers(staff))

    assert client.post(
        "/api/borrows/PMFINE5/collect-fine",
        headers=_headers(tokens["admin"]),
    ).status_code == 403
    assert client.post(
        "/api/borrows/PMFINE5/collect-fine",
        headers=_headers(reader["token"]),
    ).status_code == 403
