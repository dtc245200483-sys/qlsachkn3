import time


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
    resp = client.post("/api/auth/login", json={"username": "qa_reader1"})
    assert resp.status_code == 422
    resp = client.post("/api/auth/login", json={})
    assert resp.status_code == 422


def test_register_success(client):
    username = f"qareg{int(time.time() * 1000)}"
    resp = client.post(
        "/api/auth/register",
        json={
            "username": username,
            "password": "MatKhau123",
            "hoTen": "QA Người Đăng Ký",
            "email": f"{username}@example.com",
            "soDienThoai": "0909999001",
            "loaiDocGia": "sinh_vien",
        },
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["role"] == "reader"
    assert data["reader_ma"].startswith("DG")


def test_register_duplicate_username(client):
    resp = client.post(
        "/api/auth/register",
        json={
            "username": "qa_reader1",
            "password": "MatKhau123",
            "hoTen": "Trùng username",
            "email": f"dupuser{int(time.time() * 1000)}@example.com",
            "soDienThoai": "0909999002",
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
            "hoTen": "Trùng email",
            "email": "qa1@example.com",
            "soDienThoai": "0909999003",
            "loaiDocGia": "sinh_vien",
        },
    )
    assert resp.status_code == 409


def test_register_short_password(client):
    resp = client.post(
        "/api/auth/register",
        json={
            "username": f"qashort{int(time.time() * 1000)}",
            "password": "123",
            "hoTen": "Mật khẩu ngắn",
            "email": f"qashort{int(time.time() * 1000)}@example.com",
            "soDienThoai": "0909999004",
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
            "hoTen": "Sai loại độc giả",
            "email": f"qaloai{int(time.time() * 1000)}@example.com",
            "soDienThoai": "0909999005",
            "loaiDocGia": "hoc_sinh",
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
