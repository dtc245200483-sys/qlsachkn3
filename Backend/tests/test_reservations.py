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
