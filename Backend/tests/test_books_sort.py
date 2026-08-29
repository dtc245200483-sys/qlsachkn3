def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _make_book(client, token: str, ma: str, ten: str, tac_gia: str, the_loai: str, nam_xb: int, so_luong: int) -> None:
    existing = client.get("/api/books", headers=_headers(token)).json()
    if any(b["ma"] == ma for b in existing):
        return
    response = client.post(
        "/api/books",
        json={
            "anhBia": "https://example.com/cover.jpg", "ma": ma,
            "ten": ten,
            "tacGia": tac_gia,
            "theLoai": the_loai,
            "nxb": "NXB Test",
            "namXb": nam_xb,
            "soLuong": so_luong,
        },
        headers=_headers(token),
    )
    assert response.status_code == 200, response.text


def _setup_books(client, token: str) -> None:
    _make_book(client, token, "TESTSORT1", "Alpha sách", "Tac gia B", "Khoa học", 2022, 5)
    _make_book(client, token, "TESTSORT2", "Beta sách", "Tac gia A", "Văn học", 2020, 1)
    _make_book(client, token, "TESTSORT3", "Gamma sách", "Tac gia C", "Khoa học", 2024, 3)


def _test_mas(client, token: str, **params) -> list:
    response = client.get("/api/books", params=params, headers=_headers(token))
    assert response.status_code == 200, response.text
    return [b["ma"] for b in response.json() if b["ma"].startswith("TESTSORT")]


def test_default_sort_by_ten_asc(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    _setup_books(client, staff)
    assert _test_mas(client, staff) == ["TESTSORT1", "TESTSORT2", "TESTSORT3"]
    assert _test_mas(client, staff, sort="ten", order="asc") == ["TESTSORT1", "TESTSORT2", "TESTSORT3"]


def test_sort_by_ten_desc(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    _setup_books(client, staff)
    assert _test_mas(client, staff, sort="ten", order="desc") == ["TESTSORT3", "TESTSORT2", "TESTSORT1"]


def test_sort_by_nam_xb_asc_desc(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    _setup_books(client, staff)
    assert _test_mas(client, staff, sort="namXb", order="asc") == ["TESTSORT2", "TESTSORT1", "TESTSORT3"]
    assert _test_mas(client, staff, sort="namXb", order="desc") == ["TESTSORT3", "TESTSORT1", "TESTSORT2"]


def test_sort_by_so_luong_asc_desc(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    _setup_books(client, staff)
    assert _test_mas(client, staff, sort="soLuong", order="asc") == ["TESTSORT2", "TESTSORT3", "TESTSORT1"]
    assert _test_mas(client, staff, sort="soLuong", order="desc") == ["TESTSORT1", "TESTSORT3", "TESTSORT2"]


def test_sort_by_tac_gia_asc(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    _setup_books(client, staff)
    assert _test_mas(client, staff, sort="tacGia", order="asc") == ["TESTSORT2", "TESTSORT1", "TESTSORT3"]


def test_sort_combined_with_filter(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    _setup_books(client, staff)
    by_loai = client.get(
        "/api/books",
        params={"theLoai": "Khoa học", "sort": "ten", "order": "asc"},
        headers=_headers(staff),
    )
    assert by_loai.status_code == 200
    assert [b["ma"] for b in by_loai.json() if b["ma"].startswith("TESTSORT")] == [
        "TESTSORT1",
        "TESTSORT3",
    ]

    by_q = client.get(
        "/api/books",
        params={"q": "sách", "sort": "soLuong", "order": "desc"},
        headers=_headers(staff),
    )
    assert by_q.status_code == 200
    assert [b["ma"] for b in by_q.json() if b["ma"].startswith("TESTSORT")] == [
        "TESTSORT1",
        "TESTSORT3",
        "TESTSORT2",
    ]


def test_sort_invalid_values_rejected(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    assert client.get("/api/books", params={"sort": "sai"}, headers=_headers(staff)).status_code == 422
    assert client.get("/api/books", params={"order": "sai"}, headers=_headers(staff)).status_code == 422
