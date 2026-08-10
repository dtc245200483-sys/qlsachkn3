import os

from conftest import unique


def test_get_profile_reader(client, headers):
    resp = client.get("/api/profile/me", headers=headers("reader1"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "qa_reader1"
    assert data["role"] == "reader"
    assert data["email"] == "DTC901000001@ictu.edu.vn"
    assert data["loai_doc_gia"] == "sinh_vien"


def test_update_profile_reader(client, headers):
    resp = client.put(
        "/api/profile/me",
        json={"ho_ten": "Nguyễn Văn QA Đổi", "so_dien_thoai": "0911111111"},
        headers=headers("reader1"),
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["ho_ten"] == "Nguyễn Văn QA Đổi"
    assert data["so_dien_thoai"] == "0911111111"


def test_update_profile_invalid_values(client, headers):
    resp = client.put(
        "/api/profile/me",
        json={"email": "sai@example.com"},
        headers=headers("reader1"),
    )
    assert resp.status_code == 422
    resp = client.put(
        "/api/profile/me",
        json={"so_dien_thoai": "123"},
        headers=headers("reader1"),
    )
    assert resp.status_code == 422
    resp = client.put(
        "/api/profile/me",
        json={"ho_ten": "A"},
        headers=headers("reader1"),
    )
    assert resp.status_code == 422


def test_change_password(client, headers):
    resp = client.put(
        "/api/profile/me/password",
        json={
            "mat_khau_cu": "Test@12345",
            "mat_khau_moi": "Test@123456",
            "xac_nhan": "Test@123456",
        },
        headers=headers("reader2"),
    )
    assert resp.status_code == 200, resp.text
    # Sai mật khẩu cũ
    resp = client.put(
        "/api/profile/me/password",
        json={"mat_khau_cu": "Sai", "mat_khau_moi": "Test@1234567"},
        headers=headers("reader2"),
    )
    assert resp.status_code == 400
    # Đăng nhập bằng mật khẩu mới
    assert client.post(
        "/api/auth/login",
        json={"username": "qa_reader2", "password": "Test@123456"},
    ).status_code == 200
    # Trả về mật khẩu cũ để không phá test khác
    assert client.put(
        "/api/profile/me/password",
        json={
            "mat_khau_cu": "Test@123456",
            "mat_khau_moi": "Test@12345",
            "xac_nhan": "Test@12345",
        },
        headers=headers("reader2"),
    ).status_code == 200


def test_upload_avatar(client, headers):
    username = f"qaavt{int(unique('')) % 100000000}"
    reg = client.post(
        "/api/auth/register",
        json={
            "username": username,
            "password": "MatKhau123",
            "hoTen": "Nguyễn Văn QA",
            "email": f"DTC97{int(unique('')) % 10000000}@ictu.edu.vn",
            "soDienThoai": "0910000009",
            "loaiDocGia": "sinh_vien",
        },
    )
    assert reg.status_code == 200, reg.text
    token = reg.json()["token"]
    avatar_path = None
    try:
        # PNG 1x1 hợp lệ
        png = bytes.fromhex(
            "89504e470d0a1a0a0000000d494844520000000100000001080600000"
            "01f15c4890000000d49444154789c626001000000ffff030000060005"
            "57bfabd40000000049454e44ae426082"
        )
        resp = client.post(
            "/api/profile/me/avatar",
            files={"file": ("a.png", png, "image/png")},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["avatar_url"].startswith("/static/avatars/")
        # Sai loại file -> 400
        resp = client.post(
            "/api/profile/me/avatar",
            files={"file": ("a.txt", b"hello", "text/plain")},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 400
        # Tìm file avatar để dọn
        import glob

        matches = glob.glob(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "..",
                "Backend",
                "static",
                "avatars",
                username + ".*",
            )
        )
        if matches:
            avatar_path = matches[0]
    finally:
        if avatar_path and os.path.isfile(avatar_path):
            os.remove(avatar_path)
