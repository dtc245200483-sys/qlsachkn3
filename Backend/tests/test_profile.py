import os

from app.config import AVATAR_DIR


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _register(client, username: str):
    return client.post(
        "/api/auth/register",
        json={
            "username": username,
            "password": "Pass@123",
            "hoTen": "Độc giả Hồ sơ",
            "email": f"{username}@ictu.edu.vn",
            "soDienThoai": "0911111111",
            "loaiDocGia": "sinh_vien",
        },
    )


def test_get_profile_by_role(client_and_tokens):
    client, tokens = client_and_tokens
    admin = client.get("/api/profile/me", headers=_headers(tokens["admin"])).json()
    assert admin["username"] == "tmp_backend_test_admin"
    assert admin["role"] == "admin"

    librarian = client.get("/api/profile/me", headers=_headers(tokens["librarian"])).json()
    assert librarian["role"] == "librarian"
    assert librarian["email"] == ""

    reader = client.get("/api/profile/me", headers=_headers(tokens["reader"])).json()
    assert reader["role"] == "reader"
    assert reader["loai_doc_gia"] == ""


def test_get_profile_registered_reader(client_and_tokens):
    client, _ = client_and_tokens
    reader = _register(client, "tmp_backend_test_prof1").json()
    profile = client.get("/api/profile/me", headers=_headers(reader["token"])).json()
    assert profile["username"] == "tmp_backend_test_prof1"
    assert profile["email"] == "tmp_backend_test_prof1@ictu.edu.vn"
    assert profile["so_dien_thoai"] == "0911111111"
    assert profile["loai_doc_gia"] == "sinh_vien"


def test_update_profile_reader(client_and_tokens):
    client, _ = client_and_tokens
    reader = _register(client, "tmp_backend_test_prof2").json()
    token = reader["token"]

    updated = client.put(
        "/api/profile/me",
        json={
            "ho_ten": "Tên đã sửa",
            "email": "tmp_backend_test_prof2b@ictu.edu.vn",
            "so_dien_thoai": "0999999999",
            "loai_doc_gia": "giang_vien",
        },
        headers=_headers(token),
    )
    assert updated.status_code == 200, updated.text
    profile = updated.json()
    assert profile["ho_ten"] == "Tên đã sửa"
    assert profile["email"] == "tmp_backend_test_prof2b@ictu.edu.vn"
    assert profile["so_dien_thoai"] == "0999999999"
    assert profile["loai_doc_gia"] == "giang_vien"

    bad_email = client.put(
        "/api/profile/me",
        json={"email": "sai-dinh-dang"},
        headers=_headers(token),
    )
    assert bad_email.status_code == 422

    duplicate = client.put(
        "/api/profile/me",
        json={"email": "tmp_backend_test_prof1@ictu.edu.vn"},
        headers=_headers(token),
    )
    assert duplicate.status_code == 409


def test_update_profile_librarian_updates_email(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    updated = client.put(
        "/api/profile/me",
        json={"ho_ten": "Thủ thư mới", "email": "tmp_backend_test_librarian@ictu.edu.vn"},
        headers=_headers(staff),
    )
    assert updated.status_code == 200
    assert updated.json()["ho_ten"] == "Thủ thư mới"
    assert updated.json()["email"] == "tmp_backend_test_librarian@ictu.edu.vn"


def test_change_password(client_and_tokens):
    client, _ = client_and_tokens
    reader = _register(client, "tmp_backend_test_prof3").json()
    token = reader["token"]
    username = "tmp_backend_test_prof3"

    wrong_old = client.put(
        "/api/profile/me/password",
        json={"mat_khau_cu": "sai", "mat_khau_moi": "Moi@123"},
        headers=_headers(token),
    )
    assert wrong_old.status_code == 400

    mismatch = client.put(
        "/api/profile/me/password",
        json={
            "mat_khau_cu": "Pass@123",
            "mat_khau_moi": "Moi@123",
            "xac_nhan": "khac",
        },
        headers=_headers(token),
    )
    assert mismatch.status_code == 400

    changed = client.put(
        "/api/profile/me/password",
        json={"mat_khau_cu": "Pass@123", "mat_khau_moi": "Moi@123"},
        headers=_headers(token),
    )
    assert changed.status_code == 200

    assert client.post(
        "/api/auth/login",
        json={"username": username, "password": "Moi@123"},
    ).status_code == 200
    assert client.post(
        "/api/auth/login",
        json={"username": username, "password": "Pass@123"},
    ).status_code == 401


def test_upload_avatar(client_and_tokens):
    client, _ = client_and_tokens
    reader = _register(client, "tmp_backend_test_prof4").json()
    token = reader["token"]
    username = "tmp_backend_test_prof4"

    png = b"\x89PNG\r\n\x1a\n" + b"0" * 100
    uploaded = client.post(
        "/api/profile/me/avatar",
        files={"file": ("avatar.png", png, "image/png")},
        headers=_headers(token),
    )
    assert uploaded.status_code == 200, uploaded.text
    avatar_url = uploaded.json()["avatar_url"]
    assert avatar_url == f"/static/avatars/{username}.png"
    assert os.path.isfile(os.path.join(AVATAR_DIR, f"{username}.png"))

    profile = client.get("/api/profile/me", headers=_headers(token)).json()
    assert profile["avatar_url"] == avatar_url

    jpg = b"\xff\xd8\xff\xe0" + b"1" * 100
    uploaded_jpg = client.post(
        "/api/profile/me/avatar",
        files={"file": ("avatar.jpg", jpg, "image/jpeg")},
        headers=_headers(token),
    )
    assert uploaded_jpg.status_code == 200
    assert uploaded_jpg.json()["avatar_url"] == f"/static/avatars/{username}.jpg"
    assert not os.path.isfile(os.path.join(AVATAR_DIR, f"{username}.png"))
    assert os.path.isfile(os.path.join(AVATAR_DIR, f"{username}.jpg"))


def test_upload_avatar_invalid_type_and_size(client_and_tokens):
    client, _ = client_and_tokens
    reader = _register(client, "tmp_backend_test_prof5").json()
    token = reader["token"]

    wrong_type = client.post(
        "/api/profile/me/avatar",
        files={"file": ("a.txt", b"hello", "text/plain")},
        headers=_headers(token),
    )
    assert wrong_type.status_code == 400

    too_large = client.post(
        "/api/profile/me/avatar",
        files={"file": ("a.png", b"0" * (2 * 1024 * 1024 + 1), "image/png")},
        headers=_headers(token),
    )
    assert too_large.status_code == 400


def test_register_validation_rules(client_and_tokens):
    client, _ = client_and_tokens
    base = {
        "username": "tmp_backend_test_val1",
        "password": "Pass@123",
        "hoTen": "Nguyễn Văn An",
        "email": "tmp_backend_test_val1@ictu.edu.vn",
        "soDienThoai": "0912345001",
        "loaiDocGia": "sinh_vien",
    }

    bad_email = client.post("/api/auth/register", json={**base, "email": "abc@example.com"})
    assert bad_email.status_code == 422
    assert "ICTU" in bad_email.json()["detail"]

    bad_phone = client.post("/api/auth/register", json={**base, "soDienThoai": "12345"})
    assert bad_phone.status_code == 422
    assert "Số điện thoại" in bad_phone.json()["detail"]

    bad_name = client.post("/api/auth/register", json={**base, "hoTen": "An"})
    assert bad_name.status_code == 422
    assert "2 từ" in bad_name.json()["detail"]

    bad_name_digit = client.post("/api/auth/register", json={**base, "hoTen": "Nguyễn Văn 123"})
    assert bad_name_digit.status_code == 422


def test_profile_update_validation_rules(client_and_tokens):
    client, _ = client_and_tokens
    reader = _register(client, "tmp_backend_test_val2").json()
    token = reader["token"]

    bad_email = client.put(
        "/api/profile/me",
        json={"email": "sai@example.com"},
        headers=_headers(token),
    )
    assert bad_email.status_code == 422

    bad_phone = client.put(
        "/api/profile/me",
        json={"so_dien_thoai": "12345"},
        headers=_headers(token),
    )
    assert bad_phone.status_code == 422

    bad_name = client.put(
        "/api/profile/me",
        json={"ho_ten": "An"},
        headers=_headers(token),
    )
    assert bad_name.status_code == 422


def test_admin_accounts_validation_rules(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["admin"]
    base = {
        "username": "tmp_backend_test_valacct",
        "password": "Pass@123",
        "ho_ten": "Tài Khoản Kiểm Tra",
        "email": "tmp_backend_test_valacct@ictu.edu.vn",
        "so_dien_thoai": "0912345001",
        "role": "librarian",
    }

    assert client.post(
        "/api/admin/accounts",
        json={**base, "email": "sai"},
        headers=_headers(admin),
    ).status_code == 422
    assert client.post(
        "/api/admin/accounts",
        json={**base, "so_dien_thoai": "12345"},
        headers=_headers(admin),
    ).status_code == 422
    assert client.post(
        "/api/admin/accounts",
        json={**base, "ho_ten": "Một"},
        headers=_headers(admin),
    ).status_code == 422


def test_update_profile_success_for_all_roles(client_and_tokens):
    client, tokens = client_and_tokens
    for username, role, email in [
        ("tmp_backend_test_admin", "admin", "tmp_backend_test_admin@ictu.edu.vn"),
        ("tmp_backend_test_librarian", "librarian", "tmp_backend_test_librarian2@ictu.edu.vn"),
        ("tmp_backend_test_reader", "reader", "tmp_backend_test_reader@ictu.edu.vn"),
    ]:
        login = client.post(
            "/api/auth/login",
            json={"username": username, "password": "Test@12345"},
        )
        assert login.status_code == 200, login.text
        token = login.json()["token"]
        updated = client.put(
            "/api/profile/me",
            json={
                "ho_ten": "Người Cập Nhật",
                "email": email,
                "so_dien_thoai": "0912345999",
            },
            headers=_headers(token),
        )
        assert updated.status_code == 200, updated.text
        profile = updated.json()
        assert profile["role"] == role
        assert profile["ho_ten"] == "Người Cập Nhật"
        assert profile["email"] == email
        assert profile["so_dien_thoai"] == "0912345999"
