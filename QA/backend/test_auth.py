import time


def _email(prefix="qareg"):
    return f"DTC99{int(time.time() * 1000)}@ictu.edu.vn"


def test_login_success_all_roles(client, tokens):
    for role in ("admin", "librarian", "reader1", "reader2"):
        assert tokens[role]


def test_login_wrong_password(client):
    resp = client.post(
        "/api/auth/login",
        json={"username": "qa_reader1", "password": "SaiMatKhau"},
    )
    assert resp.status_code == 401


def test_login_unknown_user(client):
    resp = client.post(
        "/api/auth/login",
        json={"username": "khong_ton_tai", "password": "Test@12345"},
    )
    assert resp.status_code == 401


def test_login_missing_fields(client):
    resp = client.post("/api/auth/login", json={"username": ""})
    assert resp.status_code == 400
    resp = client.post("/api/auth/login", json={})
    assert resp.status_code == 400


def test_register_success(client):
    username = f"qareg{int(time.time() * 1000)}"
    resp = client.post(
        "/api/auth/register",
        json={
            "username": username,
            "password": "MatKhau123",
            "hoTen": "Nguyễn Văn QA",
            "email": _email(),
            "soDienThoai": "0910000001",
            "loaiDocGia": "sinh_vien",
        },
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["role"] == "reader"
    assert data["role_display"] == "Độc giả"
    assert data["reader_ma"].startswith("DG")


def test_register_duplicate_username(client):
    resp = client.post(
        "/api/auth/register",
        json={
            "username": "qa_reader1",
            "password": "MatKhau123",
            "hoTen": "Trần Văn QA",
            "email": _email(),
            "soDienThoai": "0910000002",
            "loaiDocGia": "sinh_vien",
        },
    )
    assert resp.status_code == 409


def test_register_duplicate_email(client):
    resp = client.post(
        "/api/auth/register",
        json={
            "username": f"qadup{int(time.time() * 1000)}",
            "password": "MatKhau123",
            "hoTen": "Lê Thị QA",
            "email": "DTC901000001@ictu.edu.vn",
            "soDienThoai": "0910000003",
            "loaiDocGia": "sinh_vien",
        },
    )
    assert resp.status_code == 409


def test_register_short_username(client):
    resp = client.post(
        "/api/auth/register",
        json={
            "username": "abc",
            "password": "MatKhau123",
            "hoTen": "Nguyễn Văn QA",
            "email": _email(),
            "soDienThoai": "0910000004",
            "loaiDocGia": "sinh_vien",
        },
    )
    assert resp.status_code == 400


def test_register_short_password(client):
    resp = client.post(
        "/api/auth/register",
        json={
            "username": f"qashort{int(time.time() * 1000)}",
            "password": "123",
            "hoTen": "Phạm Văn QA",
            "email": _email(),
            "soDienThoai": "0910000005",
            "loaiDocGia": "sinh_vien",
        },
    )
    assert resp.status_code == 400


def test_register_invalid_email(client):
    resp = client.post(
        "/api/auth/register",
        json={
            "username": f"qaemail{int(time.time() * 1000)}",
            "password": "MatKhau123",
            "hoTen": "Vũ Văn QA",
            "email": "a@example.com",
            "soDienThoai": "0910000006",
            "loaiDocGia": "sinh_vien",
        },
    )
    assert resp.status_code == 422


def test_register_invalid_phone(client):
    resp = client.post(
        "/api/auth/register",
        json={
            "username": f"qasdt{int(time.time() * 1000)}",
            "password": "MatKhau123",
            "hoTen": "Đỗ Văn QA",
            "email": _email(),
            "soDienThoai": "0123",
            "loaiDocGia": "sinh_vien",
        },
    )
    assert resp.status_code == 422


def test_register_invalid_reader_type(client):
    resp = client.post(
        "/api/auth/register",
        json={
            "username": f"qaloai{int(time.time() * 1000)}",
            "password": "MatKhau123",
            "hoTen": "Bùi Văn QA",
            "email": _email(),
            "soDienThoai": "0910000007",
            "loaiDocGia": "hoc_sinh",
        },
    )
    assert resp.status_code == 422


def test_register_invalid_ho_ten(client):
    resp = client.post(
        "/api/auth/register",
        json={
            "username": f"qahoten{int(time.time() * 1000)}",
            "password": "MatKhau123",
            "hoTen": "A",
            "email": _email(),
            "soDienThoai": "0910000008",
            "loaiDocGia": "sinh_vien",
        },
    )
    assert resp.status_code == 422


def test_reader_cannot_access_admin_apis(client, headers):
    resp = client.get("/api/admin/accounts", headers=headers("reader1"))
    assert resp.status_code == 403


def test_admin_cannot_borrow(client, headers):
    resp = client.post(
        "/api/borrows",
        json={
            "ma_phieu": "QAPMADMIN",
            "ma_doc_gia": "QADG01",
            "items": [{"ma_sach": "QAS002", "so_luong": 1}],
        },
        headers=headers("admin"),
    )
    assert resp.status_code == 403


def test_no_token_returns_401(client):
    resp = client.get("/api/books")
    assert resp.status_code == 401
