import time

from conftest import unique


def _reader(ma: str, email: str | None = None) -> dict:
    return {
        "ma": ma,
        "hoTen": "Nguyễn Văn QA",
        "email": email or f"DTC98{int(time.time() * 1000) % 10000000}@ictu.edu.vn",
        "soDienThoai": "0910000001",
        "loaiDocGia": "sinh_vien",
        "trangThaiThe": "hoat_dong",
    }


def test_create_reader_success(client, headers):
    ma = unique("QDR")
    resp = client.post("/api/readers", json=_reader(ma), headers=headers("admin"))
    assert resp.status_code == 200, resp.text
    assert resp.json()["ma"] == ma
    assert resp.json()["diem_svnet"] == 100


def test_create_reader_duplicate_ma(client, headers):
    ma = unique("QDD")
    body = _reader(ma)
    assert client.post("/api/readers", json=body, headers=headers("admin")).status_code == 200
    assert client.post("/api/readers", json=body, headers=headers("admin")).status_code == 409


def test_create_reader_duplicate_email(client, headers):
    resp = client.post(
        "/api/readers",
        json=_reader(unique("QDE"), email="DTC901000001@ictu.edu.vn"),
        headers=headers("admin"),
    )
    assert resp.status_code == 409


def test_create_reader_invalid_values(client, headers):
    body = _reader(unique("QDI"))
    body["loaiDocGia"] = "hoc_sinh"
    assert client.post("/api/readers", json=body, headers=headers("admin")).status_code == 422
    body = _reader(unique("QDI2"))
    body["trangThaiThe"] = "bih_khoa"
    assert client.post("/api/readers", json=body, headers=headers("admin")).status_code == 422
    body = _reader(unique("QDI3"))
    body["email"] = "a@example.com"
    assert client.post("/api/readers", json=body, headers=headers("admin")).status_code == 422
    body = _reader(unique("QDI4"))
    body["hoTen"] = "A"
    assert client.post("/api/readers", json=body, headers=headers("admin")).status_code == 422


def test_librarian_cannot_create_or_edit_reader(client, headers):
    ma = unique("QDLB")
    assert client.post("/api/readers", json=_reader(ma), headers=headers("librarian")).status_code == 403
    assert client.put(f"/api/readers/QADG01", json={"hoTen": "Đổi Tên QA"}, headers=headers("librarian")).status_code == 403


def test_update_reader_success(client, headers):
    ma = unique("QDU")
    assert client.post("/api/readers", json=_reader(ma), headers=headers("admin")).status_code == 200
    resp = client.put(
        f"/api/readers/{ma}",
        json={"hoTen": "Trần Văn QA"},
        headers=headers("admin"),
    )
    assert resp.status_code == 200
    assert resp.json()["hoTen"] == "Trần Văn QA"


def test_lock_reader_by_librarian(client, headers):
    ma = unique("QDL")
    assert client.post("/api/readers", json=_reader(ma), headers=headers("admin")).status_code == 200
    resp = client.put(
        f"/api/readers/{ma}/lock",
        json={"trangThaiThe": "khoa"},
        headers=headers("librarian"),
    )
    assert resp.status_code == 200
    assert resp.json()["trangThaiThe"] == "khoa"
    resp = client.put(
        f"/api/readers/{ma}/lock",
        json={"trangThaiThe": "hoat_dong"},
        headers=headers("librarian"),
    )
    assert resp.status_code == 200


def test_lock_linked_account_blocks_login(client, headers):
    # Khoá thẻ QADG01 -> tài khoản qa_reader1 liên kết phải bị khoá
    resp = client.put(
        "/api/readers/QADG01/lock",
        json={"trangThaiThe": "khoa"},
        headers=headers("admin"),
    )
    assert resp.status_code == 200
    assert client.post(
        "/api/auth/login",
        json={"username": "qa_reader1", "password": "Test@12345"},
    ).status_code == 401
    # Mở lại để không phá test khác
    assert client.put(
        "/api/readers/QADG01/lock",
        json={"trangThaiThe": "hoat_dong"},
        headers=headers("admin"),
    ).status_code == 200


def test_delete_reader_admin_only(client, headers):
    ma = unique("QDX")
    assert client.post("/api/readers", json=_reader(ma), headers=headers("admin")).status_code == 200
    assert client.delete(f"/api/readers/{ma}", headers=headers("librarian")).status_code == 403
    assert client.delete(f"/api/readers/{ma}", headers=headers("admin")).status_code == 200


def test_search_reader(client, headers):
    resp = client.get("/api/readers", params={"q": "QA1"}, headers=headers("librarian"))
    assert resp.status_code == 200
    assert any(r["ma"] == "QADG01" for r in resp.json())


def test_reader_list_permissions(client, headers):
    assert client.get("/api/readers", headers=headers("reader1")).status_code == 403
    assert client.get("/api/readers", headers=headers("admin")).status_code == 200
