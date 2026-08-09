import time

from conftest import unique


def _book(ma: str, so_luong: int = 2, nam_xb: int = 2024) -> dict:
    return {
        "ma": ma,
        "ten": f"Sách QA {ma}",
        "tacGia": f"Tác giả {ma}",
        "theLoai": "Công nghệ QA",
        "nxb": "NXB QA Test",
        "namXb": nam_xb,
        "soLuong": so_luong,
        "theLoaiId": "QATL1",
        "nxbId": "QANX1",
    }


def test_create_book_success(client, headers):
    ma = unique("QBT")
    resp = client.post("/api/books", json=_book(ma), headers=headers("librarian"))
    assert resp.status_code == 200, resp.text
    assert resp.json()["ma"] == ma


def test_create_book_duplicate(client, headers):
    ma = unique("QBD")
    body = _book(ma)
    assert client.post("/api/books", json=body, headers=headers("librarian")).status_code == 200
    resp = client.post("/api/books", json=body, headers=headers("librarian"))
    assert resp.status_code == 409


def test_create_book_negative_quantity(client, headers):
    body = _book(unique("QBN"))
    body["soLuong"] = -1
    resp = client.post("/api/books", json=body, headers=headers("librarian"))
    assert resp.status_code == 422


def test_create_book_year_boundaries(client, headers):
    ok_low = _book(unique("QBL"), nam_xb=1000)
    ok_high = _book(unique("QBH"), nam_xb=2100)
    bad_low = _book(unique("QBB"), nam_xb=999)
    bad_high = _book(unique("QBA"), nam_xb=2101)
    assert client.post("/api/books", json=ok_low, headers=headers("librarian")).status_code == 200
    assert client.post("/api/books", json=ok_high, headers=headers("librarian")).status_code == 200
    assert client.post("/api/books", json=bad_low, headers=headers("librarian")).status_code == 422
    assert client.post("/api/books", json=bad_high, headers=headers("librarian")).status_code == 422


def test_create_book_missing_fields(client, headers):
    resp = client.post(
        "/api/books",
        json={"ma": unique("QBM")},
        headers=headers("librarian"),
    )
    assert resp.status_code == 422


def test_create_book_invalid_category_id(client, headers):
    body = _book(unique("QBC"))
    body["theLoaiId"] = "KHONG_TON_TAI"
    resp = client.post("/api/books", json=body, headers=headers("librarian"))
    assert resp.status_code == 422


def test_update_book_success(client, headers):
    ma = unique("QBU")
    assert client.post("/api/books", json=_book(ma), headers=headers("librarian")).status_code == 200
    body = _book(ma, so_luong=7)
    body["ten"] = "Sách QA đã sửa"
    resp = client.put(f"/api/books/{ma}", json=body, headers=headers("librarian"))
    assert resp.status_code == 200
    assert resp.json()["soLuong"] == 7
    assert resp.json()["ten"] == "Sách QA đã sửa"


def test_update_book_not_found(client, headers):
    resp = client.put(
        f"/api/books/{unique('QBNF')}",
        json=_book(unique("QBNF")),
        headers=headers("librarian"),
    )
    assert resp.status_code == 404


def test_delete_book_success(client, headers):
    ma = unique("QBX")
    assert client.post("/api/books", json=_book(ma), headers=headers("librarian")).status_code == 200
    resp = client.delete(f"/api/books/{ma}", headers=headers("librarian"))
    assert resp.status_code == 200
    assert client.delete(f"/api/books/{ma}", headers=headers("librarian")).status_code == 404


def test_search_by_title_case_insensitive(client, headers):
    resp = client.get("/api/books", params={"q": "python"}, headers=headers("reader1"))
    assert resp.status_code == 200
    titles = [b["ten"] for b in resp.json()]
    assert any("Python" in t for t in titles)
    resp = client.get("/api/books", params={"q": "PYTHON"}, headers=headers("reader1"))
    assert any("Python" in b["ten"] for b in resp.json())


def test_search_by_author(client, headers):
    resp = client.get(
        "/api/books",
        params={"q": "QA Tác giả 1"},
        headers=headers("reader1"),
    )
    assert resp.status_code == 200
    assert any(b["ma"] == "QAS001" for b in resp.json())


def test_filter_by_category(client, headers):
    resp = client.get(
        "/api/books",
        params={"theLoai": "Văn học QA"},
        headers=headers("reader1"),
    )
    assert resp.status_code == 200
    assert all(b["theLoai"] == "Văn học QA" for b in resp.json())
    assert any(b["ma"] == "QAS004" for b in resp.json())


def test_filter_status_con(client, headers):
    resp = client.get(
        "/api/books",
        params={"trangThai": "con"},
        headers=headers("reader1"),
    )
    data = resp.json()
    assert resp.status_code == 200
    assert all(b["soLuong"] > 0 for b in data)
    assert not any(b["ma"] == "QAS003" for b in data)


def test_filter_status_dang_muon(client, headers):
    resp = client.get(
        "/api/books",
        params={"trangThai": "dang_muon"},
        headers=headers("reader1"),
    )
    assert resp.status_code == 200
    assert any(b["ma"] == "QAS001" for b in resp.json())


def test_filter_invalid_status(client, headers):
    resp = client.get(
        "/api/books",
        params={"trangThai": "het_sach"},
        headers=headers("reader1"),
    )
    assert resp.status_code == 422


def test_create_book_as_reader_forbidden(client, headers):
    resp = client.post(
        "/api/books",
        json=_book(unique("QBR")),
        headers=headers("reader1"),
    )
    assert resp.status_code == 403


def test_books_require_auth(client):
    resp = client.get("/api/books")
    assert resp.status_code == 401
