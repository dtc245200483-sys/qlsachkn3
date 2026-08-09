import time

from conftest import unique


def _reader(ma: str, email: str | None = None) -> dict:
    return {
        "ma": ma,
        "hoTen": f"Độc giả QA {ma}",
        "email": email or f"{ma.lower()}@example.com",
        "soDienThoai": "0910000001",
        "loaiDocGia": "sinh_vien",
        "trangThaiThe": "hoat_dong",
    }


def test_create_reader_success(client, headers):
    ma = unique("QDR")
    resp = client.post("/api/readers", json=_reader(ma), headers=headers("librarian"))
    assert resp.status_code == 200, resp.text
    assert resp.json()["ma"] == ma


def test_create_reader_duplicate_ma(client, headers):
    ma = unique("QDD")
    body = _reader(ma)
    assert client.post("/api/readers", json=body, headers=headers("librarian")).status_code == 200
    assert client.post("/api/readers", json=body, headers=headers("librarian")).status_code == 409


def test_create_reader_duplicate_email(client, headers):
    resp = client.post(
        "/api/readers",
        json=_reader(unique("QDE"), email="qa1@example.com"),
        headers=headers("librarian"),
    )
    assert resp.status_code == 409


def test_create_reader_invalid_values(client, headers):
    body = _reader(unique("QDI"))
    body["loaiDocGia"] = "hoc_sinh"
    assert client.post("/api/readers", json=body, headers=headers("librarian")).status_code == 422
    body = _reader(unique("QDI2"))
    body["trangThaiThe"] = "bih_khoa"
    assert client.post("/api/readers", json=body, headers=headers("librarian")).status_code == 422
    body = _reader(unique("QDI3"))
    body["email"] = ""
    assert client.post("/api/readers", json=body, headers=headers("librarian")).status_code == 422


def test_update_reader_success(client, headers):
    ma = unique("QDU")
    assert client.post("/api/readers", json=_reader(ma), headers=headers("librarian")).status_code == 200
    resp = client.put(
        f"/api/readers/{ma}",
        json={"hoTen": "Tên đã đổi"},
        headers=headers("librarian"),
    )
    assert resp.status_code == 200
    assert resp.json()["hoTen"] == "Tên đã đổi"


def test_lock_reader_card(client, headers):
    ma = unique("QDL")
    assert client.post("/api/readers", json=_reader(ma), headers=headers("librarian")).status_code == 200
    resp = client.put(
        f"/api/readers/{ma}",
        json={"trangThaiThe": "khoa"},
        headers=headers("librarian"),
    )
    assert resp.status_code == 200
    assert resp.json()["trangThaiThe"] == "khoa"


def test_delete_reader_admin_only(client, headers):
    ma = unique("QDX")
    assert client.post("/api/readers", json=_reader(ma), headers=headers("librarian")).status_code == 200
    resp = client.delete(f"/api/readers/{ma}", headers=headers("librarian"))
    assert resp.status_code == 403
    resp = client.delete(f"/api/readers/{ma}", headers=headers("admin"))
    assert resp.status_code == 200


def test_search_reader(client, headers):
    resp = client.get("/api/readers", params={"q": "QA1"}, headers=headers("librarian"))
    assert resp.status_code == 200
    assert any(r["ma"] == "QADG01" for r in resp.json())


def test_reader_list_permissions(client, headers):
    assert client.get("/api/readers", headers=headers("reader1")).status_code == 403
    assert client.get("/api/readers", headers=headers("admin")).status_code == 200
