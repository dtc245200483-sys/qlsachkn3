from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models import AnThongBao, Book, BorrowSlip, DatTruoc, DocThongBao, YeuCau
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
            "hoTen": "Độc giả Thông báo",
            "email": next_test_email(),
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
            "anhBia": "https://example.com/cover.jpg", "ma": ma,
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


def _set_reservation_status(ma_dat: str, trang_thai: str) -> None:
    db = SessionLocal()
    try:
        res = db.get(DatTruoc, ma_dat)
        assert res is not None
        res.trang_thai = trang_thai
        db.commit()
    finally:
        db.close()


def _set_book_stock(book_ma: str, so_luong: int) -> None:
    db = SessionLocal()
    try:
        from app.models import BookCopy
        book = db.get(Book, book_ma)
        assert book is not None
        book.soLuong = so_luong
        
        existing_copies = db.query(BookCopy).filter(BookCopy.book_id == book_ma).count()
        for i in range(existing_copies, so_luong):
            db.add(BookCopy(copy_id=f"{book_ma}-COPY-{i}", book_id=book_ma, status="Có sẵn"))
        db.commit()
    finally:
        db.close()


def _set_request_xuly_date(ma_yeu_cau: str, days_offset: int) -> None:
    db = SessionLocal()
    try:
        req = db.get(YeuCau, ma_yeu_cau)
        assert req is not None
        req.ngay_xu_ly = datetime.now() + timedelta(days=days_offset)
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
    returned = client.put(
        f"/api/borrows/PMNTF6/return",
        headers=_headers(staff),
    )
    assert returned.status_code == 200, returned.text

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


def test_approved_muon_request_notification(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_ntfreq1").json()
    _make_book(client, staff, "TESTNTF8", 2)

    created = client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": "YCTESTNTF1",
            "loai": "MUON",
            "items": [{"ma_sach": "TESTNTF8", "so_luong": 1}],
        },
        headers=_headers(reader["token"]),
    )
    assert created.status_code == 200, created.text
    approved = client.put("/api/requests/YCTESTNTF1/approve", headers=_headers(staff))
    assert approved.status_code == 200, approved.text
    assert approved.json()["ma_phieu"] == "PMYCTESTNTF1"

    items = _notifications(client, reader["token"])
    assert any(
        n["loai"] == "YEU_CAU_DA_DUYET"
        and n["id"] == "YEU_CAU:YCTESTNTF1"
        and "phiếu mượn PMYCTESTNTF1" in n["noi_dung"]
        and n["da_doc"] is False
        for n in items
    )


def test_borrowed_reservation_notification(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    borrower = _register(client, "tmp_backend_test_ntfreq2bor").json()
    reader = _register(client, "tmp_backend_test_ntfreq2").json()
    _make_book(client, staff, "TESTNTF9", 1)
    _borrow(client, staff, "PMNTF8", borrower["reader_ma"], "TESTNTF9")

    reservation = client.post(
        "/api/reservations",
        json={"ma_sach": "TESTNTF9"},
        headers=_headers(reader["token"]),
    ).json()
    _set_book_stock("TESTNTF9", 2)
    client.put(f"/api/reservations/{reservation['ma_dat']}/fulfill", headers=_headers(staff))
    borrowed = client.put(
        f"/api/reservations/{reservation['ma_dat']}/borrow",
        headers=_headers(staff),
    )
    assert borrowed.status_code == 200, borrowed.text
    ma_phieu = "PM" + reservation["ma_dat"][2:]

    items = _notifications(client, reader["token"])
    assert any(
        n["loai"] == "DAT_TRUOC_DA_MUON"
        and n["id"] == f"DAT_TRUOC:{reservation['ma_dat']}"
        and ma_phieu in n["noi_dung"]
        and n["da_doc"] is False
        for n in items
    )


def test_old_request_and_other_reader_not_shown(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader_a = _register(client, "tmp_backend_test_ntfreq3a").json()
    reader_b = _register(client, "tmp_backend_test_ntfreq3b").json()
    _make_book(client, staff, "TESTNTF10", 2)

    client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": "YCTESTNTF2",
            "loai": "MUON",
            "items": [{"ma_sach": "TESTNTF10", "so_luong": 1}],
        },
        headers=_headers(reader_a["token"]),
    )
    client.put("/api/requests/YCTESTNTF2/approve", headers=_headers(staff))
    _set_request_xuly_date("YCTESTNTF2", days_offset=-8)

    mine = _notifications(client, reader_a["token"])
    assert not any(n["id"] == "YEU_CAU:YCTESTNTF2" for n in mine)

    other = _notifications(client, reader_b["token"])
    assert not any(n["id"] == "YEU_CAU:YCTESTNTF2" for n in other)


def test_mark_one_notification_read(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_ntfread1").json()
    _make_book(client, staff, "TESTNTF11", 2)
    client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": "YCTESTNTF3",
            "loai": "MUON",
            "items": [{"ma_sach": "TESTNTF11", "so_luong": 1}],
        },
        headers=_headers(reader["token"]),
    )
    client.put("/api/requests/YCTESTNTF3/approve", headers=_headers(staff))

    before = _notifications(client, reader["token"])
    assert next(n for n in before if n["id"] == "YEU_CAU:YCTESTNTF3")["da_doc"] is False

    marked = client.put(
        "/api/notifications/YEU_CAU:YCTESTNTF3/read",
        headers=_headers(reader["token"]),
    )
    assert marked.status_code == 200

    after = _notifications(client, reader["token"])
    assert next(n for n in after if n["id"] == "YEU_CAU:YCTESTNTF3")["da_doc"] is True


def test_mark_all_notifications_read(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_ntfread2").json()
    _make_book(client, staff, "TESTNTF12", 2)
    client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": "YCTESTNTF4",
            "loai": "MUON",
            "items": [{"ma_sach": "TESTNTF12", "so_luong": 1}],
        },
        headers=_headers(reader["token"]),
    )
    client.put("/api/requests/YCTESTNTF4/approve", headers=_headers(staff))

    borrower = _register(client, "tmp_backend_test_ntfread2bor").json()
    _make_book(client, staff, "TESTNTF13", 1)
    _borrow(client, staff, "PMNTF9", borrower["reader_ma"], "TESTNTF13")
    reservation = client.post(
        "/api/reservations",
        json={"ma_sach": "TESTNTF13"},
        headers=_headers(reader["token"]),
    ).json()
    _set_book_stock("TESTNTF13", 2)
    assert client.put(
        f"/api/reservations/{reservation['ma_dat']}/fulfill",
        headers=_headers(staff),
    ).status_code == 200

    current = _notifications(client, reader["token"])
    assert len(current) == 2
    assert all(n["da_doc"] is False for n in current)

    marked = client.put("/api/notifications/read-all", headers=_headers(reader["token"]))
    assert marked.status_code == 200
    assert marked.json()["so_da_doc"] == 2

    after = _notifications(client, reader["token"])
    assert all(n["da_doc"] is True for n in after)


def test_read_other_reader_not_found(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader_a = _register(client, "tmp_backend_test_ntfread3a").json()
    reader_b = _register(client, "tmp_backend_test_ntfread3b").json()
    _make_book(client, staff, "TESTNTF14", 2)
    client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": "YCTESTNTF5",
            "loai": "MUON",
            "items": [{"ma_sach": "TESTNTF14", "so_luong": 1}],
        },
        headers=_headers(reader_a["token"]),
    )
    client.put("/api/requests/YCTESTNTF5/approve", headers=_headers(staff))

    other = client.put(
        "/api/notifications/YEU_CAU:YCTESTNTF5/read",
        headers=_headers(reader_b["token"]),
    )
    assert other.status_code == 404

    b_items = _notifications(client, reader_b["token"])
    assert not any(n["id"] == "YEU_CAU:YCTESTNTF5" for n in b_items)

    missing = client.put(
        "/api/notifications/KHONGTONTAI/read",
        headers=_headers(reader_a["token"]),
    )
    assert missing.status_code == 404

    a_after = _notifications(client, reader_a["token"])
    assert next(n for n in a_after if n["id"] == "YEU_CAU:YCTESTNTF5")["da_doc"] is False


def _approve_muon_request(client, staff, reader_token, ma_yeu_cau, book_ma):
    client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": ma_yeu_cau,
            "loai": "MUON",
            "items": [{"ma_sach": book_ma, "so_luong": 1}],
        },
        headers=_headers(reader_token),
    )
    assert client.put(
        f"/api/requests/{ma_yeu_cau}/approve",
        headers=_headers(staff),
    ).status_code == 200


def test_hide_one_notification(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader_a = _register(client, "tmp_backend_test_ntfhide1a").json()
    reader_b = _register(client, "tmp_backend_test_ntfhide1b").json()
    _make_book(client, staff, "TESTNTF15", 2)
    _make_book(client, staff, "TESTNTF16", 2)
    _approve_muon_request(client, staff, reader_a["token"], "YCTESTNTF6", "TESTNTF15")
    _approve_muon_request(client, staff, reader_b["token"], "YCTESTNTF7", "TESTNTF16")

    mine = _notifications(client, reader_a["token"])
    assert any(n["id"] == "YEU_CAU:YCTESTNTF6" for n in mine)
    other = _notifications(client, reader_b["token"])
    assert any(n["id"] == "YEU_CAU:YCTESTNTF7" for n in other)

    hidden = client.delete(
        "/api/notifications/YEU_CAU:YCTESTNTF6",
        headers=_headers(reader_a["token"]),
    )
    assert hidden.status_code == 200
    assert hidden.json()["da_xoa"] == 1

    mine_after = _notifications(client, reader_a["token"])
    assert not any(n["id"] == "YEU_CAU:YCTESTNTF6" for n in mine_after)

    other_after = _notifications(client, reader_b["token"])
    assert any(n["id"] == "YEU_CAU:YCTESTNTF7" for n in other_after)
    assert not any(n["id"] == "YEU_CAU:YCTESTNTF6" for n in other_after)

    mine_again = _notifications(client, reader_a["token"])
    assert not any(n["id"] == "YEU_CAU:YCTESTNTF6" for n in mine_again)


def test_hide_all_notifications(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_ntfhide2").json()
    _make_book(client, staff, "TESTNTF17", 2)
    _approve_muon_request(client, staff, reader["token"], "YCTESTNTF8", "TESTNTF17")

    borrower = _register(client, "tmp_backend_test_ntfhide2bor").json()
    _make_book(client, staff, "TESTNTF18", 1)
    _borrow(client, staff, "PMNTF10", borrower["reader_ma"], "TESTNTF18")
    reservation = client.post(
        "/api/reservations",
        json={"ma_sach": "TESTNTF18"},
        headers=_headers(reader["token"]),
    ).json()
    _set_book_stock("TESTNTF18", 2)
    assert client.put(
        f"/api/reservations/{reservation['ma_dat']}/fulfill",
        headers=_headers(staff),
    ).status_code == 200

    before = _notifications(client, reader["token"])
    assert len(before) == 2
    hidden = client.delete("/api/notifications", headers=_headers(reader["token"]))
    assert hidden.status_code == 200
    assert hidden.json()["da_xoa"] == 2

    after = _notifications(client, reader["token"])
    assert not any(n["loai"] in ("YEU_CAU_DA_DUYET", "SACH_SAN_SANG") for n in after)


def test_hide_other_reader_not_found(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader_a = _register(client, "tmp_backend_test_ntfhide3a").json()
    reader_b = _register(client, "tmp_backend_test_ntfhide3b").json()
    _make_book(client, staff, "TESTNTF19", 2)
    _approve_muon_request(client, staff, reader_a["token"], "YCTESTNTF9", "TESTNTF19")

    response = client.delete(
        "/api/notifications/YEU_CAU:YCTESTNTF9",
        headers=_headers(reader_b["token"]),
    )
    assert response.status_code == 404

    missing = client.delete(
        "/api/notifications/KHONGTONTAI",
        headers=_headers(reader_a["token"]),
    )
    assert missing.status_code == 404


def test_hide_removes_read_state(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_ntfhide4").json()
    _make_book(client, staff, "TESTNTF20", 2)
    _approve_muon_request(client, staff, reader["token"], "YCTESTNTF10", "TESTNTF20")

    client.put(
        "/api/notifications/YEU_CAU:YCTESTNTF10/read",
        headers=_headers(reader["token"]),
    )
    db = SessionLocal()
    try:
        assert db.query(DocThongBao).filter(
            DocThongBao.ma_doc_gia == reader["reader_ma"],
            DocThongBao.nguon_id == "YEU_CAU:YCTESTNTF10",
        ).count() == 1
    finally:
        db.close()

    client.delete(
        "/api/notifications/YEU_CAU:YCTESTNTF10",
        headers=_headers(reader["token"]),
    )
    db = SessionLocal()
    try:
        assert db.query(DocThongBao).filter(
            DocThongBao.ma_doc_gia == reader["reader_ma"],
            DocThongBao.nguon_id == "YEU_CAU:YCTESTNTF10",
        ).count() == 0
        assert db.query(AnThongBao).filter(
            AnThongBao.ma_doc_gia == reader["reader_ma"],
            AnThongBao.nguon_id == "YEU_CAU:YCTESTNTF10",
        ).count() == 1
    finally:
        db.close()
