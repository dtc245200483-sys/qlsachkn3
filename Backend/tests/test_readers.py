from tests.helpers import next_test_email


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _reader_payload(ma: str = "TEST001", **overrides) -> dict:
    payload = {
        "anhBia": "https://example.com/cover.jpg", "ma": ma,
        "hoTen": "Nguyễn Văn Test",
        "email": next_test_email(),
        "soDienThoai": "0901234567",
        "loaiDocGia": "sinh_vien",
        "trangThaiThe": "hoat_dong",
    }
    payload.update(overrides)
    return payload


def test_create_reader(client_and_tokens):
    client, tokens = client_and_tokens
    response = client.post(
        "/api/readers",
        json=_reader_payload(),
        headers=_headers(tokens["admin"]),
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["ma"] == "TEST001"
    assert data["hoTen"] == "Nguyễn Văn Test"
    assert data["trangThaiThe"] == "hoat_dong"
    assert data["loaiDocGia"] == "sinh_vien"


def test_create_duplicate_reader(client_and_tokens):
    client, tokens = client_and_tokens
    response = client.post(
        "/api/readers",
        json=_reader_payload("TEST002"),
        headers=_headers(tokens["admin"]),
    )
    assert response.status_code == 200, response.text
    duplicate = client.post(
        "/api/readers",
        json=_reader_payload("TEST002"),
        headers=_headers(tokens["admin"]),
    )
    assert duplicate.status_code == 409


def test_update_reader(client_and_tokens):
    client, tokens = client_and_tokens
    client.post(
        "/api/readers",
        json=_reader_payload("TEST003"),
        headers=_headers(tokens["admin"]),
    )
    response = client.put(
        "/api/readers/TEST003",
        json={"hoTen": "Nguyễn Văn Bích", "soDienThoai": "0912345678"},
        headers=_headers(tokens["admin"]),
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["hoTen"] == "Nguyễn Văn Bích"
    assert data["soDienThoai"] == "0912345678"


def test_lock_unlock_card(client_and_tokens):
    client, tokens = client_and_tokens
    client.post(
        "/api/readers",
        json=_reader_payload("TEST004"),
        headers=_headers(tokens["admin"]),
    )
    locked = client.put(
        "/api/readers/TEST004/lock",
        json={"trangThaiThe": "khoa"},
        headers=_headers(tokens["librarian"]),
    )
    assert locked.status_code == 200, locked.text
    assert locked.json()["trangThaiThe"] == "khoa"

    unlocked = client.put(
        "/api/readers/TEST004/lock",
        json={"trangThaiThe": "hoat_dong"},
        headers=_headers(tokens["librarian"]),
    )
    assert unlocked.status_code == 200
    assert unlocked.json()["trangThaiThe"] == "hoat_dong"


def test_delete_reader_and_404_after(client_and_tokens):
    client, tokens = client_and_tokens
    client.post(
        "/api/readers",
        json=_reader_payload("TEST005"),
        headers=_headers(tokens["admin"]),
    )
    deleted = client.delete(
        "/api/readers/TEST005",
        headers=_headers(tokens["admin"]),
    )
    assert deleted.status_code == 200, deleted.text

    missing = client.put(
        "/api/readers/TEST005",
        json={"hoTen": "Không còn"},
        headers=_headers(tokens["admin"]),
    )
    assert missing.status_code == 404
    deleted_again = client.delete(
        "/api/readers/TEST005",
        headers=_headers(tokens["admin"]),
    )
    assert deleted_again.status_code == 404


def test_search_by_name_and_ma(client_and_tokens):
    client, tokens = client_and_tokens
    client.post(
        "/api/readers",
        json=_reader_payload("TEST006", hoTen="Trần Thị Tìm Kiếm"),
        headers=_headers(tokens["admin"]),
    )
    by_name = client.get("/api/readers", params={"q": "Tìm Kiếm"}, headers=_headers(tokens["librarian"]))
    assert by_name.status_code == 200
    assert any(r["ma"] == "TEST006" for r in by_name.json())

    by_ma = client.get("/api/readers", params={"q": "TEST006"}, headers=_headers(tokens["librarian"]))
    assert by_ma.status_code == 200
    assert any(r["ma"] == "TEST006" for r in by_ma.json())

    empty = client.get("/api/readers", params={"q": "không-có-kết-quả"}, headers=_headers(tokens["librarian"]))
    assert empty.status_code == 200
    assert empty.json() == []


def test_permissions(client_and_tokens):
    client, tokens = client_and_tokens
    reader_headers = _headers(tokens["reader"])
    librarian_headers = _headers(tokens["librarian"])
    admin_headers = _headers(tokens["admin"])

    assert client.get("/api/readers", headers=reader_headers).status_code == 403
    assert client.post("/api/readers", json=_reader_payload("TEST007"), headers=reader_headers).status_code == 403

    assert client.post("/api/readers", json=_reader_payload("TEST007"), headers=librarian_headers).status_code == 200
    assert client.put("/api/readers/TEST007", json={"hoTen": "Sửa bởi thủ thư"}, headers=librarian_headers).status_code == 200
    assert client.get("/api/readers", headers=librarian_headers).status_code == 200

    created = client.post("/api/readers", json=_reader_payload("TEST008"), headers=admin_headers)
    assert created.status_code == 200
    assert client.put("/api/readers/TEST007", json={"hoTen": "Sửa bởi admin"}, headers=admin_headers).status_code == 200
    assert client.put("/api/readers/TEST007/lock", json={"trangThaiThe": "khoa"}, headers=librarian_headers).status_code == 200
    assert client.delete("/api/readers/TEST007", headers=librarian_headers).status_code == 403
    assert client.delete("/api/readers/TEST007", headers=admin_headers).status_code == 200


def test_required_fields_and_invalid_values(client_and_tokens):
    client, tokens = client_and_tokens
    headers = _headers(tokens["admin"])

    empty_name = client.post("/api/readers", json=_reader_payload("TEST008", hoTen=""), headers=headers)
    assert empty_name.status_code == 422

    invalid_loai = client.post("/api/readers", json=_reader_payload("TEST008", loaiDocGia="hoc_sinh"), headers=headers)
    assert invalid_loai.status_code == 422

    invalid_trang_thai = client.post("/api/readers", json=_reader_payload("TEST008", trangThaiThe="het_han"), headers=headers)
    assert invalid_trang_thai.status_code == 422


def test_audit_log_for_reader_crud(client_and_tokens):
    client, tokens = client_and_tokens
    client.post(
        "/api/readers",
        json=_reader_payload("TEST009"),
        headers=_headers(tokens["admin"]),
    )
    client.put(
        "/api/readers/TEST009",
        json={"hoTen": "Sửa tên"},
        headers=_headers(tokens["admin"]),
    )
    client.put(
        "/api/readers/TEST009/lock",
        json={"trangThaiThe": "khoa"},
        headers=_headers(tokens["librarian"]),
    )
    client.delete(
        "/api/readers/TEST009",
        headers=_headers(tokens["admin"]),
    )

    audit = client.get(
        "/api/admin/audit-logs",
        headers=_headers(tokens["admin"]),
    )
    assert audit.status_code == 200
    actions = [row["action"] for row in audit.json()]
    assert "CREATE_READER" in actions
    assert "UPDATE_READER" in actions
    assert "UPDATE_READER_STATUS" in actions
    assert "DELETE_READER" in actions
