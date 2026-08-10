import time

from conftest import unique


def test_top_books_sorted_and_limit(client, headers):
    resp = client.get("/api/stats/top-books", params={"limit": 3}, headers=headers("librarian"))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) <= 3
    counts = [row["so_lan_muon"] for row in data]
    assert counts == sorted(counts, reverse=True)
    assert all({"ma_sach", "ten_sach", "so_lan_muon"} <= set(row) for row in data)
    assert client.get("/api/stats/top-books", params={"limit": 0}, headers=headers("librarian")).status_code == 422
    assert client.get("/api/stats/top-books", params={"limit": 101}, headers=headers("librarian")).status_code == 422


def test_top_readers(client, headers):
    resp = client.get("/api/stats/top-readers", headers=headers("librarian"))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) <= 10
    assert all({"ma_doc_gia", "ho_ten", "so_phieu_muon"} <= set(row) for row in data)


def test_overdue_books(client, headers):
    resp = client.get("/api/stats/overdue-books", headers=headers("admin"))
    assert resp.status_code == 200
    data = resp.json()
    assert any(row["ma_phieu"] == "QAPM02" for row in data)
    for row in data:
        assert row["so_ngay_qua_han"] >= 1
        assert {"ma_phieu", "ma_sach", "ten_sach", "ma_doc_gia", "ho_ten", "so_ngay_qua_han"} <= set(row)


def test_stats_permissions(client, headers):
    for path in ("/api/stats/top-books", "/api/stats/top-readers", "/api/stats/overdue-books"):
        assert client.get(path, headers=headers("reader1")).status_code == 403


def test_export_books_csv(client, headers):
    resp = client.get("/api/export/books.csv", headers=headers("librarian"))
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    assert "attachment" in resp.headers["content-disposition"]
    assert resp.content.startswith(b"\xef\xbb\xbf")
    assert "Mã".encode("utf-8") in resp.content
    assert b"QAS001" in resp.content


def test_export_borrows_csv(client, headers):
    resp = client.get("/api/export/borrows.csv", headers=headers("librarian"))
    assert resp.status_code == 200
    assert resp.content.startswith(b"\xef\xbb\xbf")
    assert "Điểm phạt".encode("utf-8") in resp.content
    assert b"QAPM01" in resp.content


def test_export_report_csv(client, headers):
    resp = client.get("/api/export/report.csv", headers=headers("admin"))
    assert resp.status_code == 200
    assert resp.content.startswith(b"\xef\xbb\xbf")
    assert "SÁCH MƯỢN NHIỀU".encode("utf-8") in resp.content
    assert "SÁCH QUÁ HẠN".encode("utf-8") in resp.content


def test_export_reservations_csv_permissions(client, headers):
    resp = client.get("/api/export/reservations.csv", headers=headers("librarian"))
    assert resp.status_code == 200
    assert resp.content.startswith(b"\xef\xbb\xbf")
    assert "Mã đặt".encode("utf-8") in resp.content
    # Admin bị chặn (chỉ librarian)
    assert client.get("/api/export/reservations.csv", headers=headers("admin")).status_code == 403
    assert client.get("/api/export/reservations.csv", headers=headers("reader1")).status_code == 403


def test_export_permissions(client, headers):
    for path in ("/api/export/books.csv", "/api/export/borrows.csv", "/api/export/report.csv"):
        assert client.get(path, headers=headers("reader1")).status_code == 403


def test_library_config_get_put_permissions(client, headers):
    assert client.get("/api/admin/config/library", headers=headers("librarian")).status_code == 200
    assert client.get("/api/admin/config/library", headers=headers("admin")).status_code == 200
    assert client.get("/api/admin/config/library", headers=headers("reader1")).status_code == 403
    body = {"max_borrow_days": 14, "overdue_fine_points_per_day": 2, "max_books_at_once": 3}
    assert client.put("/api/admin/config/library", json=body, headers=headers("librarian")).status_code == 403
    resp = client.put("/api/admin/config/library", json=body, headers=headers("admin"))
    assert resp.status_code == 200
    assert resp.json()["overdue_fine_points_per_day"] == 2
    bad = {"max_borrow_days": 0, "overdue_fine_points_per_day": 2, "max_books_at_once": 3}
    assert client.put("/api/admin/config/library", json=bad, headers=headers("admin")).status_code == 422


def test_ai_config_masked_and_permissions(client, headers):
    assert client.get("/api/admin/config/ai", headers=headers("reader1")).status_code == 403
    assert client.get("/api/admin/config/ai", headers=headers("librarian")).status_code == 403
    resp = client.get("/api/admin/config/ai", headers=headers("admin"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["has_api_key"] is True
    assert "qa-placeholder-key" not in data["api_key_masked"]
    assert data["prompt_template"]
    resp = client.put(
        "/api/admin/config/ai",
        json={"model": "gpt-4o-mini", "provider": "openai"},
        headers=headers("admin"),
    )
    assert resp.status_code == 200


def test_audit_logs_admin_only(client, headers):
    assert client.get("/api/admin/audit-logs", headers=headers("librarian")).status_code == 403
    resp = client.get("/api/admin/audit-logs", params={"limit": 5}, headers=headers("admin"))
    assert resp.status_code == 200
    assert len(resp.json()) <= 5
    resp = client.get("/api/admin/audit-logs", params={"action": "LOGIN_SUCCESS"}, headers=headers("admin"))
    assert resp.status_code == 200
    assert all(row["action"] == "LOGIN_SUCCESS" for row in resp.json())


def test_admin_accounts_librarian_only(client, headers):
    username = f"qaacc{int(time.time() * 1000) % 100000000}"
    resp = client.post(
        "/api/admin/accounts",
        json={
            "username": username,
            "password": "MatKhau123",
            "ho_ten": "Nguyễn Văn QA",
            "email": f"DTC96{int(time.time() * 1000)}@ictu.edu.vn",
            "so_dien_thoai": "0910000001",
            "role": "librarian",
        },
        headers=headers("admin"),
    )
    assert resp.status_code == 200, resp.text
    acc_id = resp.json()["id"]
    # Tạo tài khoản reader qua admin -> 400
    resp = client.post(
        "/api/admin/accounts",
        json={
            "username": f"qareaderacc{int(time.time() * 1000)}",
            "password": "MatKhau123",
            "ho_ten": "Trần Văn QA",
            "email": f"DTC96{int(time.time() * 1000) + 1}@ictu.edu.vn",
            "so_dien_thoai": "0910000002",
            "role": "reader",
        },
        headers=headers("admin"),
    )
    assert resp.status_code == 400
    # Trùng username -> 409
    assert client.post(
        "/api/admin/accounts",
        json={
            "username": username,
            "password": "MatKhau123",
            "ho_ten": "Lê Văn QA",
            "email": f"DTC96{int(time.time() * 1000) + 2}@ictu.edu.vn",
            "so_dien_thoai": "0910000003",
            "role": "librarian",
        },
        headers=headers("admin"),
    ).status_code == 409
    # Khoá tài khoản -> không đăng nhập được
    resp = client.put(f"/api/admin/accounts/{acc_id}", json={"is_active": False}, headers=headers("admin"))
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False
    assert client.post(
        "/api/auth/login",
        json={"username": username, "password": "MatKhau123"},
    ).status_code == 401
    resp = client.delete(f"/api/admin/accounts/{acc_id}", headers=headers("admin"))
    assert resp.status_code == 200
    assert client.get("/api/admin/accounts", params={"role": "reader"}, headers=headers("admin")).status_code == 200
    assert client.get("/api/admin/accounts", params={"role": "sai"}, headers=headers("admin")).status_code == 422


def test_categories_crud(client, headers):
    ma = unique("QACA")
    resp = client.post("/api/admin/categories", json={"ma": ma, "ten": "Thể loại QA"}, headers=headers("admin"))
    assert resp.status_code == 200, resp.text
    assert client.post("/api/admin/categories", json={"ma": ma, "ten": "Trùng"}, headers=headers("admin")).status_code == 409
    resp = client.put(f"/api/admin/categories/{ma}", json={"ten": "Thể loại QA sửa"}, headers=headers("admin"))
    assert resp.status_code == 200
    assert resp.json()["ten"] == "Thể loại QA sửa"
    assert client.delete(f"/api/admin/categories/{ma}", headers=headers("admin")).status_code == 200
    assert client.delete("/api/admin/categories/QATL1", headers=headers("admin")).status_code == 400
    assert client.get("/api/admin/categories", headers=headers("librarian")).status_code == 403


def test_publishers_crud(client, headers):
    ma = unique("QANX")
    resp = client.post("/api/admin/publishers", json={"ma": ma, "ten": "NXB QA"}, headers=headers("admin"))
    assert resp.status_code == 200, resp.text
    assert client.post("/api/admin/publishers", json={"ma": ma, "ten": "Trùng"}, headers=headers("admin")).status_code == 409
    resp = client.put(f"/api/admin/publishers/{ma}", json={"ten": "NXB QA sửa"}, headers=headers("admin"))
    assert resp.status_code == 200
    assert resp.json()["ten"] == "NXB QA sửa"
    assert client.delete(f"/api/admin/publishers/{ma}", headers=headers("admin")).status_code == 200
    assert client.delete("/api/admin/publishers/QANX1", headers=headers("admin")).status_code == 400


def test_restore_validates_file(client, headers):
    resp = client.post(
        "/api/admin/restore",
        json={"file_path": "C:\\khong_ton_tai\\abc.bak"},
        headers=headers("admin"),
    )
    assert resp.status_code == 404
    resp = client.post(
        "/api/admin/restore",
        json={"file_path": "C:\\khong_ton_tai\\abc.txt"},
        headers=headers("admin"),
    )
    assert resp.status_code == 404
    assert client.post(
        "/api/admin/restore",
        json={"file_path": "C:\\x.bak"},
        headers=headers("librarian"),
    ).status_code == 403
