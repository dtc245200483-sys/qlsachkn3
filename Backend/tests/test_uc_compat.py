from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models import BorrowSlip

_hist_seq = 0


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _register(client, username: str, email: str):
    return client.post(
        "/api/auth/register",
        json={
            "username": username,
            "password": "Pass@123",
            "hoTen": "Độc giả Đăng Ký",
            "email": email,
            "soDienThoai": "0911111111",
            "loaiDocGia": "sinh_vien",
        },
    )


def _make_book(client, token: str, ma: str, so_luong: int = 5) -> None:
    existing = client.get("/api/books", headers=_headers(token)).json()
    if any(b["ma"] == ma for b in existing):
        return
    response = client.post(
        "/api/books",
        json={
            "ma": ma,
            "ten": f"Sách {ma}",
            "tacGia": "Tác giả Test",
            "theLoai": "Test",
            "nxb": "NXB Test",
            "namXb": 2024,
            "soLuong": so_luong,
        },
        headers=_headers(token),
    )
    assert response.status_code == 200, response.text


def _set_han_tra(ma_phieu: str, days_ago: int) -> None:
    db = SessionLocal()
    try:
        slip = db.get(BorrowSlip, ma_phieu)
        assert slip is not None
        slip.han_tra = datetime.now() - timedelta(days=days_ago)
        db.commit()
    finally:
        db.close()


def test_register_reader_and_login(client_and_tokens):
    client, _ = client_and_tokens
    registered = _register(client, "tmp_backend_test_reg1", "tmp_backend_test_reg1@ictu.edu.vn")
    assert registered.status_code == 200, registered.text
    data = registered.json()
    assert data["role"] == "reader"
    assert data["reader_ma"].startswith("DG")

    dup_username = _register(client, "tmp_backend_test_reg1", "tmp_backend_test_reg1b@ictu.edu.vn")
    assert dup_username.status_code == 409

    dup_email = _register(client, "tmp_backend_test_reg2", "tmp_backend_test_reg1@ictu.edu.vn")
    assert dup_email.status_code == 409

    me = client.get("/api/borrows/me", headers=_headers(data["token"]))
    assert me.status_code == 200
    assert me.json() == []


def test_request_muon_approve_flow(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["librarian"]
    librarian = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_reg3", "tmp_backend_test_reg3@ictu.edu.vn").json()
    reader_ma = reader["reader_ma"]
    _make_book(client, admin, "TESTUCB1", 3)

    created = client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": "YCTEST1",
            "loai": "MUON",
            "items": [{"ma_sach": "TESTUCB1", "so_luong": 2}],
        },
        headers=_headers(reader["token"]),
    )
    assert created.status_code == 200, created.text
    assert created.json()["trang_thai"] == "CHO_XU_LY"

    listed = client.get(
        "/api/requests",
        params={"maDocGia": reader_ma},
        headers=_headers(librarian),
    )
    assert listed.status_code == 200
    assert any(r["ma_yeu_cau"] == "YCTEST1" for r in listed.json())

    approved = client.put("/api/requests/YCTEST1/approve", headers=_headers(librarian))
    assert approved.status_code == 200, approved.text
    assert approved.json()["trang_thai"] == "DA_DUYET"
    assert approved.json()["ma_phieu"] == "PMYCTEST1"

    books = client.get("/api/books", headers=_headers(admin)).json()
    assert next(b["soLuong"] for b in books if b["ma"] == "TESTUCB1") == 1

    my_history = client.get("/api/borrows/me", headers=_headers(reader["token"])).json()
    assert any(s["ma_phieu"] == "PMYCTEST1" and s["trang_thai"] == "dang_muon" for s in my_history)


def test_request_tra_approve_flow(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["librarian"]
    librarian = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_reg4", "tmp_backend_test_reg4@ictu.edu.vn").json()
    reader_ma = reader["reader_ma"]
    _make_book(client, admin, "TESTUCB2", 3)
    client.post(
        "/api/borrows",
        json={
            "ma_phieu": "PMTESTTR",
            "ma_doc_gia": reader_ma,
            "items": [{"ma_sach": "TESTUCB2", "so_luong": 1}],
        },
        headers=_headers(admin),
    )

    request = client.post(
        "/api/requests",
        json={"ma_yeu_cau": "YCTEST2", "loai": "TRA", "ma_phieu": "PMTESTTR"},
        headers=_headers(reader["token"]),
    )
    assert request.status_code == 200, request.text

    approved = client.put("/api/requests/YCTEST2/approve", headers=_headers(librarian))
    assert approved.status_code == 200, approved.text
    assert approved.json()["trang_thai"] == "DA_DUYET"

    books = client.get("/api/books", headers=_headers(admin)).json()
    assert next(b["soLuong"] for b in books if b["ma"] == "TESTUCB2") == 3
    history = client.get("/api/borrows/me", headers=_headers(reader["token"])).json()
    assert any(s["ma_phieu"] == "PMTESTTR" and s["trang_thai"] == "da_tra" for s in history)


def test_request_gia_han_approve_and_second_fails(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["librarian"]
    librarian = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_reg5", "tmp_backend_test_reg5@ictu.edu.vn").json()
    reader_ma = reader["reader_ma"]
    _make_book(client, admin, "TESTUCB3", 3)
    client.post(
        "/api/borrows",
        json={
            "ma_phieu": "PMTESTGH",
            "ma_doc_gia": reader_ma,
            "items": [{"ma_sach": "TESTUCB3", "so_luong": 1}],
        },
        headers=_headers(admin),
    )

    first = client.post(
        "/api/requests",
        json={"ma_yeu_cau": "YCTEST3", "loai": "GIA_HAN", "ma_phieu": "PMTESTGH"},
        headers=_headers(reader["token"]),
    )
    assert first.status_code == 200, first.text
    approved = client.put("/api/requests/YCTEST3/approve", headers=_headers(librarian))
    assert approved.status_code == 200, approved.text

    second = client.post(
        "/api/requests",
        json={"ma_yeu_cau": "YCTEST4", "loai": "GIA_HAN", "ma_phieu": "PMTESTGH"},
        headers=_headers(reader["token"]),
    )
    assert second.status_code == 400


def test_request_reject(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["admin"]
    librarian = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_reg6", "tmp_backend_test_reg6@ictu.edu.vn").json()
    _make_book(client, admin, "TESTUCB7", 2)
    client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": "YCTEST5",
            "loai": "MUON",
            "items": [{"ma_sach": "TESTUCB7", "so_luong": 1}],
        },
        headers=_headers(reader["token"]),
    )
    rejected = client.put("/api/requests/YCTEST5/reject", headers=_headers(librarian))
    assert rejected.status_code == 200, rejected.text
    assert rejected.json()["trang_thai"] == "TU_CHOI"


def test_reader_history_includes_fine(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_reg7", "tmp_backend_test_reg7@ictu.edu.vn").json()
    reader_ma = reader["reader_ma"]
    _make_book(client, admin, "TESTUCB4", 3)
    client.post(
        "/api/borrows",
        json={
            "ma_phieu": "PMTESTFINE",
            "ma_doc_gia": reader_ma,
            "items": [{"ma_sach": "TESTUCB4", "so_luong": 1}],
        },
        headers=_headers(admin),
    )
    _set_han_tra("PMTESTFINE", days_ago=5)
    client.put("/api/borrows/PMTESTFINE/return", headers=_headers(admin))

    history = client.get("/api/borrows/me", headers=_headers(reader["token"])).json()
    slip = next(s for s in history if s["ma_phieu"] == "PMTESTFINE")
    assert slip["fines"] == [
        {
            "so_ngay_qua_han": 5,
            "so_diem": 10,
            "da_thu": False,
            "ngay_thu": None,
        }
    ]


def test_admin_accounts_crud_and_lock(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["admin"]

    created = client.post(
        "/api/admin/accounts",
        json={
            "username": "tmp_backend_test_acct1",
            "password": "Pass@123",
            "ho_ten": "Tài khoản Một",
            "email": "tmp_backend_test_acct1@ictu.edu.vn",
            "so_dien_thoai": "0912345001",
            "role": "librarian",
        },
        headers=_headers(admin),
    )
    assert created.status_code == 200, created.text
    account_id = created.json()["id"]

    reader_rejected = client.post(
        "/api/admin/accounts",
        json={
            "username": "tmp_backend_test_acct2",
            "password": "Pass@123",
            "ho_ten": "Tài khoản Hai",
            "email": "tmp_backend_test_acct2@ictu.edu.vn",
            "so_dien_thoai": "0912345002",
            "role": "reader",
        },
        headers=_headers(admin),
    )
    assert reader_rejected.status_code == 400
    assert "tự đăng ký" in reader_rejected.json()["detail"]

    duplicate = client.post(
        "/api/admin/accounts",
        json={
            "username": "tmp_backend_test_acct1",
            "password": "Pass@123",
            "ho_ten": "Người Trùng",
            "email": "tmp_backend_test_acct1@ictu.edu.vn",
            "so_dien_thoai": "0912345001",
            "role": "librarian",
        },
        headers=_headers(admin),
    )
    assert duplicate.status_code == 409

    locked = client.put(
        f"/api/admin/accounts/{account_id}",
        json={"is_active": False},
        headers=_headers(admin),
    )
    assert locked.status_code == 200
    assert locked.json()["is_active"] is False
    login_locked = client.post(
        "/api/auth/login",
        json={"username": "tmp_backend_test_acct1", "password": "Pass@123"},
    )
    assert login_locked.status_code == 401

    deleted = client.delete(f"/api/admin/accounts/{account_id}", headers=_headers(admin))
    assert deleted.status_code == 200, deleted.text
    remaining = client.get("/api/admin/accounts", headers=_headers(admin)).json()
    assert not any(a["id"] == account_id for a in remaining)


def test_categories_publishers_crud(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["admin"]

    category = client.post(
        "/api/admin/categories",
        json={"ma": "TESTTL1", "ten": "Thể loại test"},
        headers=_headers(admin),
    )
    assert category.status_code == 200, category.text
    assert client.post(
        "/api/admin/categories",
        json={"ma": "TESTTL1", "ten": "Trùng"},
        headers=_headers(admin),
    ).status_code == 409
    updated = client.put(
        "/api/admin/categories/TESTTL1",
        json={"ten": "Thể loại test 2"},
        headers=_headers(admin),
    )
    assert updated.status_code == 200
    assert updated.json()["ten"] == "Thể loại test 2"

    publisher = client.post(
        "/api/admin/publishers",
        json={"ma": "TESTNXB1", "ten": "NXB test"},
        headers=_headers(admin),
    )
    assert publisher.status_code == 200, publisher.text
    updated_pub = client.put(
        "/api/admin/publishers/TESTNXB1",
        json={"ten": "NXB test 2"},
        headers=_headers(admin),
    )
    assert updated_pub.status_code == 200

    book = client.post(
        "/api/books",
        json={
            "ma": "TESTUCB5",
            "ten": "Sách danh mục",
            "tacGia": "Tác giả",
            "theLoai": "Thể loại test 2",
            "nxb": "NXB test 2",
            "namXb": 2024,
            "soLuong": 1,
            "theLoaiId": "TESTTL1",
            "nxbId": "TESTNXB1",
        },
        headers=_headers(admin),
    )
    assert book.status_code == 200, book.text
    assert book.json()["theLoaiId"] == "TESTTL1"
    assert book.json()["nxbId"] == "TESTNXB1"

    assert client.delete("/api/admin/categories/TESTTL1", headers=_headers(admin)).status_code == 400
    assert client.delete("/api/admin/publishers/TESTNXB1", headers=_headers(admin)).status_code == 400
    assert client.delete("/api/books/TESTUCB5", headers=_headers(admin)).status_code == 200
    assert client.delete("/api/admin/categories/TESTTL1", headers=_headers(admin)).status_code == 200
    assert client.delete("/api/admin/publishers/TESTNXB1", headers=_headers(admin)).status_code == 200


def test_books_reject_invalid_category_and_publisher(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["admin"]
    bad = client.post(
        "/api/books",
        json={
            "ma": "TESTUCB6",
            "ten": "Sách sai danh mục",
            "tacGia": "Tác giả",
            "theLoai": "Test",
            "nxb": "NXB Test",
            "namXb": 2024,
            "soLuong": 1,
            "theLoaiId": "KHONGTONTAI",
        },
        headers=_headers(admin),
    )
    assert bad.status_code == 422


def test_restore_validates_file(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["admin"]
    response = client.post(
        "/api/admin/restore",
        json={"file_path": r"Z:\khong-ton-tai.bak"},
        headers=_headers(admin),
    )
    assert response.status_code == 404


def test_role_display_vietnamese(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["admin"]

    login_admin = client.post(
        "/api/auth/login",
        json={"username": "tmp_backend_test_admin", "password": "Test@12345"},
    )
    assert login_admin.status_code == 200
    assert login_admin.json()["role"] == "admin"
    assert login_admin.json()["role_display"] == "Quản trị viên"

    login_librarian = client.post(
        "/api/auth/login",
        json={"username": "tmp_backend_test_librarian", "password": "Test@12345"},
    )
    assert login_librarian.json()["role_display"] == "Thủ thư"

    login_reader = client.post(
        "/api/auth/login",
        json={"username": "tmp_backend_test_reader", "password": "Test@12345"},
    )
    assert login_reader.json()["role_display"] == "Độc giả"

    registered = _register(client, "tmp_backend_test_roledisp", "tmp_backend_test_roledisp@ictu.edu.vn").json()
    assert registered["role_display"] == "Độc giả"

    accounts = client.get("/api/admin/accounts", headers=_headers(admin)).json()
    by_username = {a["username"]: a for a in accounts}
    assert by_username["tmp_backend_test_librarian"]["role_display"] == "Thủ thư"
    assert by_username["tmp_backend_test_reader"]["role_display"] == "Độc giả"


def _han_tra_days(client, token, reader_ma, ma_phieu):
    slips = client.get(
        "/api/borrows",
        params={"docGia": reader_ma},
        headers=_headers(token),
    ).json()
    slip = next(s for s in slips if s["ma_phieu"] == ma_phieu)
    return (datetime.fromisoformat(slip["han_tra"]) - datetime.fromisoformat(slip["ngay_muon"])).days


def test_muon_request_so_ngay_muon_used_on_approve(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_ycso1", "tmp_backend_test_ycso1@ictu.edu.vn").json()
    _make_book(client, staff, "TESTYCSO1", 3)

    created = client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": "YCSO1",
            "loai": "MUON",
            "items": [{"ma_sach": "TESTYCSO1", "so_luong": 1}],
            "so_ngay_muon": 10,
        },
        headers=_headers(reader["token"]),
    )
    assert created.status_code == 200, created.text
    assert created.json()["so_ngay_muon"] == 10

    approved = client.put("/api/requests/YCSO1/approve", headers=_headers(staff))
    assert approved.status_code == 200, approved.text
    assert _han_tra_days(client, staff, reader["reader_ma"], "PMYCSO1") == 10


def test_muon_request_so_ngay_muon_exceeds_max_fails(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_ycso2", "tmp_backend_test_ycso2@ictu.edu.vn").json()
    _make_book(client, staff, "TESTYCSO2", 3)

    response = client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": "YCSO2",
            "loai": "MUON",
            "items": [{"ma_sach": "TESTYCSO2", "so_luong": 1}],
            "so_ngay_muon": 20,
        },
        headers=_headers(reader["token"]),
    )
    assert response.status_code == 400
    assert "vượt quá tối đa 14 ngày" in response.json()["detail"]


def test_approve_muon_body_overrides_request_days(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_ycso3", "tmp_backend_test_ycso3@ictu.edu.vn").json()
    _make_book(client, staff, "TESTYCSO3", 3)

    client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": "YCSO3",
            "loai": "MUON",
            "items": [{"ma_sach": "TESTYCSO3", "so_luong": 1}],
            "so_ngay_muon": 5,
        },
        headers=_headers(reader["token"]),
    )
    approved = client.put(
        "/api/requests/YCSO3/approve",
        json={"so_ngay_muon": 8},
        headers=_headers(staff),
    )
    assert approved.status_code == 200, approved.text
    assert _han_tra_days(client, staff, reader["reader_ma"], "PMYCSO3") == 8


def test_approve_muon_without_days_uses_max(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_ycso4", "tmp_backend_test_ycso4@ictu.edu.vn").json()
    _make_book(client, staff, "TESTYCSO4", 3)

    client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": "YCSO4",
            "loai": "MUON",
            "items": [{"ma_sach": "TESTYCSO4", "so_luong": 1}],
        },
        headers=_headers(reader["token"]),
    )
    approved = client.put("/api/requests/YCSO4/approve", headers=_headers(staff))
    assert approved.status_code == 200, approved.text
    assert _han_tra_days(client, staff, reader["reader_ma"], "PMYCSO4") == 14


def test_approve_muon_body_exceeds_max_fails(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_ycso5", "tmp_backend_test_ycso5@ictu.edu.vn").json()
    _make_book(client, staff, "TESTYCSO5", 3)

    client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": "YCSO5",
            "loai": "MUON",
            "items": [{"ma_sach": "TESTYCSO5", "so_luong": 1}],
        },
        headers=_headers(reader["token"]),
    )
    approved = client.put(
        "/api/requests/YCSO5/approve",
        json={"so_ngay_muon": 20},
        headers=_headers(staff),
    )
    assert approved.status_code == 400
    assert "vượt quá tối đa 14 ngày" in approved.json()["detail"]

    listed = client.get("/api/requests", headers=_headers(reader["token"])).json()
    assert any(r["ma_yeu_cau"] == "YCSO5" and r["trang_thai"] == "CHO_XU_LY" for r in listed)


def _reader_with_returned_and_active_slips(client, tokens, prefix: str):
    global _hist_seq
    _hist_seq += 1
    admin = tokens["librarian"]
    username = f"tmp_backend_test_hist{_hist_seq}"
    reader = _register(client, username, f"{username}@ictu.edu.vn").json()
    assert "reader_ma" in reader, reader
    book_ma = f"TESTUCB{prefix}"
    _make_book(client, admin, book_ma, 4)
    for n in ("1", "2"):
        ma_phieu = f"PMHIST{prefix}{n}"
        client.post(
            "/api/borrows",
            json={
                "ma_phieu": ma_phieu,
                "ma_doc_gia": reader["reader_ma"],
                "items": [{"ma_sach": book_ma, "so_luong": 1}],
            },
            headers=_headers(admin),
        )
        client.put(f"/api/borrows/{ma_phieu}/return", headers=_headers(admin))
    client.post(
        "/api/borrows",
        json={
            "ma_phieu": f"PMHIST{prefix}3",
            "ma_doc_gia": reader["reader_ma"],
            "items": [{"ma_sach": book_ma, "so_luong": 1}],
        },
        headers=_headers(admin),
    )
    return reader


def test_reader_delete_one_returned_history(client_and_tokens):
    client, tokens = client_and_tokens
    admin = tokens["admin"]
    reader = _reader_with_returned_and_active_slips(client, tokens, "A")
    token = reader["token"]

    deleted = client.delete("/api/borrows/me/PMHISTA1", headers=_headers(token))
    assert deleted.status_code == 200, deleted.text

    history = client.get("/api/borrows/me", headers=_headers(token)).json()
    ma_phieus = [s["ma_phieu"] for s in history]
    assert "PMHISTA1" not in ma_phieus
    assert "PMHISTA2" in ma_phieus
    assert "PMHISTA3" in ma_phieus

    books = client.get("/api/books", headers=_headers(admin)).json()
    assert next(b["soLuong"] for b in books if b["ma"] == "TESTUCBA") == 3


def test_reader_cannot_delete_active_slip(client_and_tokens):
    client, tokens = client_and_tokens
    reader = _reader_with_returned_and_active_slips(client, tokens, "B")
    token = reader["token"]

    blocked = client.delete("/api/borrows/me/PMHISTB3", headers=_headers(token))
    assert blocked.status_code == 400
    history = client.get("/api/borrows/me", headers=_headers(token)).json()
    assert any(s["ma_phieu"] == "PMHISTB3" for s in history)


def test_reader_delete_all_returned_history(client_and_tokens):
    client, tokens = client_and_tokens
    reader = _reader_with_returned_and_active_slips(client, tokens, "C")
    token = reader["token"]

    deleted = client.delete("/api/borrows/me", headers=_headers(token))
    assert deleted.status_code == 200, deleted.text
    assert deleted.json()["so_phieu_da_xoa"] == 2

    history = client.get("/api/borrows/me", headers=_headers(token)).json()
    ma_phieus = [s["ma_phieu"] for s in history]
    assert "PMHISTC1" not in ma_phieus
    assert "PMHISTC2" not in ma_phieus
    assert "PMHISTC3" in ma_phieus


def test_reader_cannot_delete_other_reader_history(client_and_tokens):
    client, tokens = client_and_tokens
    _reader_with_returned_and_active_slips(client, tokens, "D")
    other = _register(client, "tmp_backend_test_hist_other", "tmp_backend_test_hist_other@ictu.edu.vn").json()
    assert "token" in other, other

    response = client.delete("/api/borrows/me/PMHISTD1", headers=_headers(other["token"]))
    assert response.status_code == 404


def test_reader_delete_history_roles(client_and_tokens):
    client, tokens = client_and_tokens
    assert client.delete("/api/borrows/me", headers=_headers(tokens["librarian"])).status_code == 403
    assert client.delete("/api/borrows/me/PMHISTD1", headers=_headers(tokens["admin"])).status_code == 403
