from app.database import SessionLocal
from app.models import Book, DatTruoc
from tests.helpers import next_test_email


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


_seq = 0


def _register(client, username: str):
    return client.post(
        "/api/auth/register",
        json={
            "username": username,
            "password": "Pass@123",
            "hoTen": "Độc giả Đặt trước",
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


def _make_out_of_stock_book(client, tokens, book_ma: str):
    """Tạo sách 1 bản và cho 1 reader khác mượn hết để có thể đặt trước."""
    global _seq
    _seq += 1
    staff = tokens["librarian"]
    _make_book(client, staff, book_ma, 1)
    borrower = _register(client, f"tmp_backend_test_rsvbor{_seq}").json()
    assert "reader_ma" in borrower, borrower
    created = client.post(
        "/api/borrows",
        json={
            "ma_phieu": f"PMRSV{_seq}",
            "ma_doc_gia": borrower["reader_ma"],
            "items": [{"ma_sach": book_ma, "so_luong": 1}],
        },
        headers=_headers(staff),
    )
    assert created.status_code == 200, created.text
    return borrower


def _set_book_stock(book_ma: str, so_luong: int) -> None:
    db = SessionLocal()
    try:
        from app.models import BookCopy
        book = db.get(Book, book_ma)
        assert book is not None
        book.soLuong = so_luong
        
        # Add book copies if necessary
        existing_copies = db.query(BookCopy).filter(BookCopy.book_id == book_ma).count()
        for i in range(existing_copies, so_luong):
            db.add(BookCopy(copy_id=f"{book_ma}-{i}", book_id=book_ma, status="Có sẵn"))
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


def test_reserve_when_book_available_fails(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["admin"]
    reader = _register(client, "tmp_backend_test_rsv1").json()
    _make_book(client, admin, "TESTRSV1", 3)

    response = client.post(
        "/api/reservations",
        json={"ma_sach": "TESTRSV1", "ma_doc_gia": "DG_gia"},
        headers=_headers(reader["token"]),
    )
    assert response.status_code == 400
    assert "Sách còn" in response.json()["detail"]


def test_reserve_out_of_stock_succeeds_and_duplicate_fails(client_and_tokens):
    client, tokens = client_and_tokens
    _make_out_of_stock_book(client, tokens, "TESTRSV2")
    reader = _register(client, "tmp_backend_test_rsv2").json()

    created = client.post(
        "/api/reservations",
        json={"ma_sach": "TESTRSV2", "ma_doc_gia": "DG_gia"},
        headers=_headers(reader["token"]),
    )
    assert created.status_code == 200, created.text
    data = created.json()
    assert data["ma_dat"].startswith("RV")
    assert data["ma_sach"] == "TESTRSV2"
    assert data["ten_sach"] == "Sách TESTRSV2"
    assert data["ma_doc_gia"] == reader["reader_ma"]
    assert data["trang_thai"] == "CHO_XU_LY"

    duplicate = client.post(
        "/api/reservations",
        json={"ma_sach": "TESTRSV2"},
        headers=_headers(reader["token"]),
    )
    assert duplicate.status_code == 409


def test_return_promotes_next_reservation_to_san_sang(client_and_tokens):
    client, tokens = client_and_tokens
    borrower = _make_out_of_stock_book(client, tokens, "TESTRSV3")
    reader_a = _register(client, "tmp_backend_test_rsv3a").json()
    reader_c = _register(client, "tmp_backend_test_rsv3c").json()
    librarian = tokens["librarian"]

    a = client.post(
        "/api/reservations",
        json={"ma_sach": "TESTRSV3"},
        headers=_headers(reader_a["token"]),
    )
    c = client.post(
        "/api/reservations",
        json={"ma_sach": "TESTRSV3"},
        headers=_headers(reader_c["token"]),
    )
    assert a.status_code == 200 and c.status_code == 200

    returned = client.put(
        f"/api/borrows/PMRSV{_seq}/return",
        headers=_headers(librarian),
    )
    assert returned.status_code == 200, returned.text

    san_sang = [
        r
        for r in client.get(
        "/api/reservations?trangThai=SAN_SANG",
        headers=_headers(librarian),
        ).json()
        if r["ma_sach"] == "TESTRSV3"
    ]
    assert [r["ma_dat"] for r in san_sang] == [a.json()["ma_dat"]]

    cho_xu_ly = [
        r
        for r in client.get(
        "/api/reservations?trangThai=CHO_XU_LY",
        headers=_headers(librarian),
        ).json()
        if r["ma_sach"] == "TESTRSV3"
    ]
    assert [r["ma_dat"] for r in cho_xu_ly] == [c.json()["ma_dat"]]


def test_renew_with_reservation_fails(client_and_tokens):
    client, tokens = client_and_tokens
    borrower = _make_out_of_stock_book(client, tokens, "TESTRSV4")
    reader = _register(client, "tmp_backend_test_rsv4").json()
    librarian = tokens["librarian"]

    client.post(
        "/api/reservations",
        json={"ma_sach": "TESTRSV4"},
        headers=_headers(reader["token"]),
    )
    renewed = client.put(
        f"/api/borrows/PMRSV{_seq}/renew",
        headers=_headers(librarian),
    )
    assert renewed.status_code == 400
    assert "đặt trước" in renewed.json()["detail"]


def test_cancel_reservation_permissions(client_and_tokens):
    client, tokens = client_and_tokens
    _make_out_of_stock_book(client, tokens, "TESTRSV5")
    reader_a = _register(client, "tmp_backend_test_rsv5a").json()
    reader_b = _register(client, "tmp_backend_test_rsv5b").json()
    librarian = tokens["librarian"]

    own = client.post(
        "/api/reservations",
        json={"ma_sach": "TESTRSV5"},
        headers=_headers(reader_a["token"]),
    ).json()
    other = client.post(
        "/api/reservations",
        json={"ma_sach": "TESTRSV5"},
        headers=_headers(reader_b["token"]),
    ).json()

    cancelled = client.put(
        f"/api/reservations/{own['ma_dat']}/cancel",
        headers=_headers(reader_a["token"]),
    )
    assert cancelled.status_code == 200
    assert cancelled.json()["trang_thai"] == "HUY"

    again = client.put(
        f"/api/reservations/{own['ma_dat']}/cancel",
        headers=_headers(reader_a["token"]),
    )
    assert again.status_code == 400

    not_mine = client.put(
        f"/api/reservations/{other['ma_dat']}/cancel",
        headers=_headers(reader_a["token"]),
    )
    assert not_mine.status_code == 404

    librarian_cancel = client.put(
        f"/api/reservations/{other['ma_dat']}/cancel",
        headers=_headers(librarian),
    )
    assert librarian_cancel.status_code == 200
    assert librarian_cancel.json()["trang_thai"] == "HUY"


def test_fulfill_permissions_and_status(client_and_tokens):
    client, tokens = client_and_tokens
    _make_out_of_stock_book(client, tokens, "TESTRSV6")
    reader = _register(client, "tmp_backend_test_rsv6").json()
    librarian = tokens["librarian"]
    admin = tokens["admin"]

    reservation = client.post(
        "/api/reservations",
        json={"ma_sach": "TESTRSV6"},
        headers=_headers(reader["token"]),
    ).json()
    ma_dat = reservation["ma_dat"]

    no_stock = client.put(
        f"/api/reservations/{ma_dat}/fulfill",
        headers=_headers(librarian),
    )
    assert no_stock.status_code == 400
    assert "Chưa có sách" in no_stock.json()["detail"]

    _set_book_stock("TESTRSV6", 2)
    fulfilled = client.put(
        f"/api/reservations/{ma_dat}/fulfill",
        headers=_headers(librarian),
    )
    assert fulfilled.status_code == 200
    assert fulfilled.json()["trang_thai"] == "SAN_SANG"

    again = client.put(
        f"/api/reservations/{ma_dat}/fulfill",
        headers=_headers(librarian),
    )
    assert again.status_code == 400

    assert client.put(
        f"/api/reservations/{ma_dat}/fulfill",
        headers=_headers(reader["token"]),
    ).status_code == 403
    assert client.put(
        f"/api/reservations/{ma_dat}/fulfill",
        headers=_headers(admin),
    ).status_code == 403
    assert client.get("/api/reservations", headers=_headers(admin)).status_code == 403
    assert client.post(
        "/api/reservations",
        json={"ma_sach": "TESTRSV6"},
        headers=_headers(admin),
    ).status_code == 403


def test_reader_list_only_own_reservations(client_and_tokens):
    client, tokens = client_and_tokens
    _make_out_of_stock_book(client, tokens, "TESTRSV7")
    reader_a = _register(client, "tmp_backend_test_rsv7a").json()
    reader_b = _register(client, "tmp_backend_test_rsv7b").json()

    client.post(
        "/api/reservations",
        json={"ma_sach": "TESTRSV7"},
        headers=_headers(reader_a["token"]),
    )
    client.post(
        "/api/reservations",
        json={"ma_sach": "TESTRSV7"},
        headers=_headers(reader_b["token"]),
    )

    mine = client.get("/api/reservations", headers=_headers(reader_a["token"])).json()
    assert all(r["ma_doc_gia"] == reader_a["reader_ma"] for r in mine)
    assert len(mine) == 1


def test_create_dat_truoc_request(client_and_tokens):
    client, tokens = client_and_tokens
    _make_out_of_stock_book(client, tokens, "TESTRD1")
    reader = _register(client, "tmp_backend_test_rdt1").json()
    token = reader["token"]

    via_items = client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": "YCRDT1",
            "loai": "DAT_TRUOC",
            "items": [{"ma_sach": "TESTRD1", "so_luong": 1}],
        },
        headers=_headers(token),
    )
    assert via_items.status_code == 200, via_items.text
    data = via_items.json()
    assert data["trang_thai"] == "CHO_XU_LY"
    assert data["items"][0]["ma_sach"] == "TESTRD1"

    via_ma_sach = client.post(
        "/api/requests",
        json={"ma_yeu_cau": "YCRDT2", "loai": "DAT_TRUOC", "ma_sach": "TESTRD1"},
        headers=_headers(token),
    )
    assert via_ma_sach.status_code == 200, via_ma_sach.text

    bad = client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": "YCRDT3",
            "loai": "DAT_TRUOC",
            "items": [
                {"ma_sach": "TESTRD1", "so_luong": 1},
                {"ma_sach": "TESTRD1", "so_luong": 1},
            ],
        },
        headers=_headers(token),
    )
    assert bad.status_code == 400


def test_approve_dat_truoc_creates_reservation(client_and_tokens):
    client, tokens = client_and_tokens
    _make_out_of_stock_book(client, tokens, "TESTRD2")
    reader = _register(client, "tmp_backend_test_rdt2").json()
    librarian = tokens["librarian"]

    created = client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": "YCRDT4",
            "loai": "DAT_TRUOC",
            "items": [{"ma_sach": "TESTRD2", "so_luong": 1}],
        },
        headers=_headers(reader["token"]),
    )
    assert created.status_code == 200

    approved = client.put("/api/requests/YCRDT4/approve", headers=_headers(librarian))
    assert approved.status_code == 200, approved.text
    assert approved.json()["trang_thai"] == "DA_DUYET"

    mine = client.get("/api/reservations", headers=_headers(reader["token"])).json()
    assert any(
        r["ma_sach"] == "TESTRD2"
        and r["ma_doc_gia"] == reader["reader_ma"]
        and r["trang_thai"] == "CHO_XU_LY"
        and r["ma_dat"].startswith("RV")
        for r in mine
    )


def test_approve_dat_truoc_when_book_available_fails(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    _make_book(client, staff, "TESTRD3", 2)
    reader = _register(client, "tmp_backend_test_rdt3").json()

    client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": "YCRDT5",
            "loai": "DAT_TRUOC",
            "items": [{"ma_sach": "TESTRD3", "so_luong": 1}],
        },
        headers=_headers(reader["token"]),
    )
    approved = client.put("/api/requests/YCRDT5/approve", headers=_headers(staff))
    assert approved.status_code == 400
    assert "Sách còn" in approved.json()["detail"]

    listed = client.get("/api/requests", headers=_headers(reader["token"])).json()
    assert any(r["ma_yeu_cau"] == "YCRDT5" and r["trang_thai"] == "CHO_XU_LY" for r in listed)


def test_approve_dat_truoc_duplicate_fails(client_and_tokens):
    client, tokens = client_and_tokens
    _make_out_of_stock_book(client, tokens, "TESTRD4")
    reader = _register(client, "tmp_backend_test_rdt4").json()
    librarian = tokens["librarian"]

    first = client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": "YCRDT6",
            "loai": "DAT_TRUOC",
            "items": [{"ma_sach": "TESTRD4", "so_luong": 1}],
        },
        headers=_headers(reader["token"]),
    )
    assert first.status_code == 200
    assert client.put("/api/requests/YCRDT6/approve", headers=_headers(librarian)).status_code == 200

    second = client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": "YCRDT7",
            "loai": "DAT_TRUOC",
            "items": [{"ma_sach": "TESTRD4", "so_luong": 1}],
        },
        headers=_headers(reader["token"]),
    )
    assert second.status_code == 200
    duplicate = client.put("/api/requests/YCRDT7/approve", headers=_headers(librarian))
    assert duplicate.status_code == 409
    assert "đã đặt trước" in duplicate.json()["detail"]


def test_delete_single_reservation_history(client_and_tokens):
    client, tokens = client_and_tokens
    _make_out_of_stock_book(client, tokens, "TESTRVH1")
    _make_out_of_stock_book(client, tokens, "TESTRVH2")
    _make_out_of_stock_book(client, tokens, "TESTRVH3")
    reader = _register(client, "tmp_backend_test_rvh1").json()
    token = reader["token"]

    res_huy = client.post(
        "/api/reservations", json={"ma_sach": "TESTRVH1"}, headers=_headers(token)
    ).json()
    res_cho = client.post(
        "/api/reservations", json={"ma_sach": "TESTRVH2"}, headers=_headers(token)
    ).json()
    res_da_muon = client.post(
        "/api/reservations", json={"ma_sach": "TESTRVH3"}, headers=_headers(token)
    ).json()
    _set_reservation_status(res_da_muon["ma_dat"], "DA_MUON")

    cancelled = client.put(
        f"/api/reservations/{res_huy['ma_dat']}/cancel",
        headers=_headers(token),
    )
    assert cancelled.status_code == 200

    deleted = client.delete(
        f"/api/reservations/me/{res_huy['ma_dat']}",
        headers=_headers(token),
    )
    assert deleted.status_code == 200
    assert deleted.json()["so_phieu_da_xoa"] == 1

    blocked = client.delete(
        f"/api/reservations/me/{res_cho['ma_dat']}",
        headers=_headers(token),
    )
    assert blocked.status_code == 400

    deleted_da = client.delete(
        f"/api/reservations/me/{res_da_muon['ma_dat']}",
        headers=_headers(token),
    )
    assert deleted_da.status_code == 200

    missing = client.delete(
        "/api/reservations/me/KHONGTONTAI",
        headers=_headers(token),
    )
    assert missing.status_code == 404


def test_delete_all_reservation_history(client_and_tokens):
    client, tokens = client_and_tokens
    for book_ma in ("TESTRVH4", "TESTRVH5", "TESTRVH6", "TESTRVH7"):
        _make_out_of_stock_book(client, tokens, book_ma)
    reader = _register(client, "tmp_backend_test_rvh4").json()
    token = reader["token"]

    res_huy = client.post(
        "/api/reservations", json={"ma_sach": "TESTRVH4"}, headers=_headers(token)
    ).json()
    res_cho = client.post(
        "/api/reservations", json={"ma_sach": "TESTRVH5"}, headers=_headers(token)
    ).json()
    res_san = client.post(
        "/api/reservations", json={"ma_sach": "TESTRVH6"}, headers=_headers(token)
    ).json()
    res_da_muon = client.post(
        "/api/reservations", json={"ma_sach": "TESTRVH7"}, headers=_headers(token)
    ).json()
    _set_reservation_status(res_da_muon["ma_dat"], "DA_MUON")
    _set_reservation_status(res_san["ma_dat"], "SAN_SANG")
    client.put(
        f"/api/reservations/{res_huy['ma_dat']}/cancel",
        headers=_headers(token),
    )

    deleted = client.delete("/api/reservations/me", headers=_headers(token))
    assert deleted.status_code == 200
    assert deleted.json()["so_phieu_da_xoa"] == 2

    remaining = client.get("/api/reservations", headers=_headers(token)).json()
    ma_dats = {r["ma_dat"] for r in remaining}
    assert res_cho["ma_dat"] in ma_dats
    assert res_san["ma_dat"] in ma_dats
    assert res_huy["ma_dat"] not in ma_dats
    assert res_da_muon["ma_dat"] not in ma_dats


def test_reader_cannot_delete_other_reservation_history(client_and_tokens):
    client, tokens = client_and_tokens
    _make_out_of_stock_book(client, tokens, "TESTRVH8")
    reader_a = _register(client, "tmp_backend_test_rvh8a").json()
    res = client.post(
        "/api/reservations",
        json={"ma_sach": "TESTRVH8"},
        headers=_headers(reader_a["token"]),
    ).json()
    client.put(
        f"/api/reservations/{res['ma_dat']}/cancel",
        headers=_headers(reader_a["token"]),
    )
    reader_b = _register(client, "tmp_backend_test_rvh8b").json()
    response = client.delete(
        f"/api/reservations/me/{res['ma_dat']}",
        headers=_headers(reader_b["token"]),
    )
    assert response.status_code == 404


def test_reservation_history_roles(client_and_tokens):
    client, tokens = client_and_tokens
    # Librarian được phép dọn lịch sử đã xử lý (2026-08-10)
    assert client.delete("/api/reservations/me", headers=_headers(tokens["librarian"])).status_code == 200
    assert client.delete("/api/reservations/me", headers=_headers(tokens["admin"])).status_code == 403
    assert client.delete("/api/reservations/me", headers=_headers(tokens["reader"])).status_code == 403

