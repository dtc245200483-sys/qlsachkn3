def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _make_book(client, token: str, ma: str, ten: str, tac_gia: str, the_loai: str, so_luong: int) -> None:
    response = client.post(
        "/api/books",
        json={
            "ma": ma,
            "ten": ten,
            "tacGia": tac_gia,
            "theLoai": the_loai,
            "nxb": "NXB Test",
            "namXb": 2024,
            "soLuong": so_luong,
        },
        headers=_headers(token),
    )
    assert response.status_code == 200, response.text


def _setup_books(client, token: str) -> None:
    books = [
        ("TESTBK1", "Lập trình Python nâng cao", "Nguyễn Văn A", "Công nghệ", 5),
        ("TESTBK2", "Tiểu thuyết Người xa lạ", "Albert Camus", "Văn học", 0),
        ("TESTBK3", "Nhập môn Trí tuệ nhân tạo", "Nguyễn Văn A", "Công nghệ", 3),
        ("TESTBK4", "Python cho người mới", "Trần Thị B", "Giáo dục", 2),
    ]
    existing = {b["ma"] for b in client.get("/api/books", headers=_headers(token)).json()}
    for ma, ten, tac_gia, the_loai, so_luong in books:
        if ma not in existing:
            _make_book(client, token, ma, ten, tac_gia, the_loai, so_luong)


def _search(client, token: str, **params) -> list:
    response = client.get("/api/books", params=params, headers=_headers(token))
    assert response.status_code == 200, response.text
    return response.json()


def test_search_by_title_contains_case_insensitive(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["admin"]
    _setup_books(client, admin)

    result = _search(client, admin, q="python")
    mas = {b["ma"] for b in result if b["ma"].startswith("TESTBK")}
    assert mas == {"TESTBK1", "TESTBK4"}


def test_search_by_author(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["admin"]
    _setup_books(client, admin)

    result = _search(client, admin, q="Nguyễn Văn A")
    mas = {b["ma"] for b in result if b["ma"].startswith("TESTBK")}
    assert mas == {"TESTBK1", "TESTBK3"}


def test_filter_by_category_exact(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["admin"]
    _setup_books(client, admin)

    result = _search(client, admin, theLoai="Công nghệ")
    mas = {b["ma"] for b in result if b["ma"].startswith("TESTBK")}
    assert mas == {"TESTBK1", "TESTBK3"}


def test_filter_status_con(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["admin"]
    _setup_books(client, admin)

    result = _search(client, admin, trangThai="con")
    mas = {b["ma"] for b in result if b["ma"].startswith("TESTBK")}
    assert "TESTBK2" not in mas
    assert mas == {"TESTBK1", "TESTBK3", "TESTBK4"}


def test_filter_status_dang_muon_stock_zero(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["admin"]
    _setup_books(client, admin)

    result = _search(client, admin, trangThai="dang_muon")
    mas = {b["ma"] for b in result if b["ma"].startswith("TESTBK")}
    assert "TESTBK2" in mas


def test_filter_status_dang_muon_with_active_borrow(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["librarian"]
    _setup_books(client, admin)

    reader = client.post(
        "/api/readers",
        json={
            "ma": "TESTDGX",
            "hoTen": "Độc giả X",
            "email": "x@example.com",
            "soDienThoai": "0900000001",
            "loaiDocGia": "sinh_vien",
            "trangThaiThe": "hoat_dong",
        },
        headers=_headers(tokens["admin"]),
    )
    assert reader.status_code == 200, reader.text

    borrowed = client.post(
        "/api/borrows",
        json={
            "ma_phieu": "PMTESTBK3",
            "ma_doc_gia": "TESTDGX",
            "items": [{"ma_sach": "TESTBK3", "so_luong": 1}],
        },
        headers=_headers(admin),
    )
    assert borrowed.status_code == 200, borrowed.text

    dang_muon = {b["ma"] for b in _search(client, admin, trangThai="dang_muon") if b["ma"].startswith("TESTBK")}
    con = {b["ma"] for b in _search(client, admin, trangThai="con") if b["ma"].startswith("TESTBK")}
    assert "TESTBK3" in dang_muon
    assert "TESTBK3" in con

    returned = client.put("/api/borrows/PMTESTBK3/return", headers=_headers(admin))
    assert returned.status_code == 200, returned.text
    dang_muon_after = {b["ma"] for b in _search(client, admin, trangThai="dang_muon") if b["ma"].startswith("TESTBK")}
    assert "TESTBK3" not in dang_muon_after


def test_combined_params(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["admin"]
    _setup_books(client, admin)

    by_q_and_loai = _search(client, admin, q="Python", theLoai="Giáo dục")
    assert {b["ma"] for b in by_q_and_loai if b["ma"].startswith("TESTBK")} == {"TESTBK4"}

    by_q_and_status = _search(client, admin, q="Nguyễn", trangThai="con")
    mas = {b["ma"] for b in by_q_and_status if b["ma"].startswith("TESTBK")}
    assert mas == {"TESTBK1", "TESTBK3"}

    by_three = _search(client, admin, q="Python", theLoai="Công nghệ", trangThai="con")
    assert {b["ma"] for b in by_three if b["ma"].startswith("TESTBK")} == {"TESTBK1"}


def test_no_params_returns_all(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["admin"]
    _setup_books(client, admin)

    result = _search(client, admin)
    mas = {b["ma"] for b in result if b["ma"].startswith("TESTBK")}
    assert {"TESTBK1", "TESTBK2", "TESTBK3", "TESTBK4"} <= mas


def test_invalid_trang_thai_rejected(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["admin"]
    response = client.get(
        "/api/books",
        params={"trangThai": "het"},
        headers=_headers(admin),
    )
    assert response.status_code == 422
