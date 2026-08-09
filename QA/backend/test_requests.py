from conftest import unique


def test_create_muon_and_approve(client, headers):
    ma_yc = unique("QAYC")
    resp = client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": ma_yc,
            "loai": "MUON",
            "items": [{"ma_sach": "QAS002", "so_luong": 1}],
        },
        headers=headers("reader1"),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["trang_thai"] == "CHO_XU_LY"
    resp = client.put(f"/api/requests/{ma_yc}/approve", headers=headers("librarian"))
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["trang_thai"] == "DA_DUYET"
    assert data["ma_phieu"] == "PM" + ma_yc
    # approve lần 2 -> 400
    assert client.put(f"/api/requests/{ma_yc}/approve", headers=headers("librarian")).status_code == 400


def test_create_tra_and_approve(client, headers):
    ma_yc = unique("QAYT")
    resp = client.post(
        "/api/requests",
        json={"ma_yeu_cau": ma_yc, "loai": "TRA", "ma_phieu": "QAPM01"},
        headers=headers("reader1"),
    )
    assert resp.status_code == 200
    resp = client.put(f"/api/requests/{ma_yc}/approve", headers=headers("librarian"))
    assert resp.status_code == 200, resp.text
    assert resp.json()["trang_thai"] == "DA_DUYET"


def test_create_gia_han_and_approve(client, headers):
    # Tạo phiếu mới cho reader1
    ma_book = unique("QBRQ")
    body = {
        "ma": ma_book,
        "ten": f"Sách yêu cầu {ma_book}",
        "tacGia": "Tác giả QA",
        "theLoai": "Công nghệ QA",
        "nxb": "NXB QA Test",
        "namXb": 2024,
        "soLuong": 2,
        "theLoaiId": "QATL1",
        "nxbId": "QANX1",
    }
    assert client.post("/api/books", json=body, headers=headers("librarian")).status_code == 200
    ma_phieu = unique("QAPMRQ")
    resp = client.post(
        "/api/borrows",
        json={
            "ma_phieu": ma_phieu,
            "ma_doc_gia": "QADG01",
            "items": [{"ma_sach": ma_book, "so_luong": 1}],
        },
        headers=headers("librarian"),
    )
    assert resp.status_code == 200
    ma_yc = unique("QAYG")
    resp = client.post(
        "/api/requests",
        json={"ma_yeu_cau": ma_yc, "loai": "GIA_HAN", "ma_phieu": ma_phieu},
        headers=headers("reader1"),
    )
    assert resp.status_code == 200
    resp = client.put(f"/api/requests/{ma_yc}/approve", headers=headers("librarian"))
    assert resp.status_code == 200, resp.text
    assert resp.json()["trang_thai"] == "DA_DUYET"
    # Kiểm tra phiếu đã gia hạn
    slips = client.get(
        "/api/borrows",
        params={"docGia": "QADG01"},
        headers=headers("librarian"),
    ).json()
    slip = next(s for s in slips if s["ma_phieu"] == ma_phieu)
    assert slip["so_lan_gia_han"] == 1


def test_request_reject(client, headers):
    ma_yc = unique("QAYR")
    resp = client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": ma_yc,
            "loai": "MUON",
            "items": [{"ma_sach": "QAS005", "so_luong": 1}],
        },
        headers=headers("reader1"),
    )
    assert resp.status_code == 200
    resp = client.put(f"/api/requests/{ma_yc}/reject", headers=headers("librarian"))
    assert resp.status_code == 200
    assert resp.json()["trang_thai"] == "TU_CHOI"
    assert client.put(f"/api/requests/{ma_yc}/approve", headers=headers("librarian")).status_code == 400


def test_request_invalid_flows(client, headers):
    # MUON thiếu items
    resp = client.post(
        "/api/requests",
        json={"ma_yeu_cau": unique("QAYI1"), "loai": "MUON"},
        headers=headers("reader1"),
    )
    assert resp.status_code == 400
    # TRA phiếu không tồn tại
    resp = client.post(
        "/api/requests",
        json={"ma_yeu_cau": unique("QAYI2"), "loai": "TRA", "ma_phieu": unique("QAPMI")},
        headers=headers("reader1"),
    )
    assert resp.status_code == 404
    # TRA phiếu của người khác
    resp = client.post(
        "/api/requests",
        json={"ma_yeu_cau": unique("QAYI3"), "loai": "TRA", "ma_phieu": "QAPM02"},
        headers=headers("reader1"),
    )
    assert resp.status_code == 403
    # Trùng mã yêu cầu
    ma_yc = unique("QAYI4")
    body = {
        "ma_yeu_cau": ma_yc,
        "loai": "MUON",
        "items": [{"ma_sach": "QAS005", "so_luong": 1}],
    }
    assert client.post("/api/requests", json=body, headers=headers("reader1")).status_code == 200
    assert client.post("/api/requests", json=body, headers=headers("reader1")).status_code == 409


def test_approve_permissions(client, headers):
    ma_yc = unique("QAYP")
    body = {
        "ma_yeu_cau": ma_yc,
        "loai": "MUON",
        "items": [{"ma_sach": "QAS005", "so_luong": 1}],
    }
    assert client.post("/api/requests", json=body, headers=headers("reader1")).status_code == 200
    assert client.put(f"/api/requests/{ma_yc}/approve", headers=headers("reader1")).status_code == 403
    assert client.put(f"/api/requests/{ma_yc}/approve", headers=headers("admin")).status_code == 403
    assert client.get("/api/requests", headers=headers("librarian")).status_code == 200


def test_reader_delete_request_history(client, headers):
    # Tạo và reject một yêu cầu, sau đó reader xoá được
    ma_yc = unique("QAYD")
    body = {
        "ma_yeu_cau": ma_yc,
        "loai": "MUON",
        "items": [{"ma_sach": "QAS005", "so_luong": 1}],
    }
    assert client.post("/api/requests", json=body, headers=headers("reader1")).status_code == 200
    assert client.put(f"/api/requests/{ma_yc}/reject", headers=headers("librarian")).status_code == 200
    resp = client.delete(f"/api/requests/me/{ma_yc}", headers=headers("reader1"))
    assert resp.status_code == 200
    # Yêu cầu đang chờ không xoá được
    ma_yc2 = unique("QAYD2")
    body2 = {
        "ma_yeu_cau": ma_yc2,
        "loai": "MUON",
        "items": [{"ma_sach": "QAS005", "so_luong": 1}],
    }
    assert client.post("/api/requests", json=body2, headers=headers("reader1")).status_code == 200
    assert client.delete(f"/api/requests/me/{ma_yc2}", headers=headers("reader1")).status_code == 400
