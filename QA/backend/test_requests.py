from datetime import datetime

from conftest import unique


def _create_book(client, headers, ma: str, so_luong: int = 2) -> None:
    body = {
        "ma": ma,
        "ten": f"Sách yêu cầu {ma}",
        "tacGia": "Tác giả QA",
        "theLoai": "Công nghệ QA",
        "nxb": "NXB QA Test",
        "namXb": 2024,
        "soLuong": so_luong,
        "theLoaiId": "QATL1",
        "nxbId": "QANX1",
    }
    assert client.post("/api/books", json=body, headers=headers("librarian")).status_code == 200


def test_create_muon_and_approve_with_so_ngay_muon(client, headers):
    ma_book = unique("QBRQ1")
    _create_book(client, headers, ma_book, so_luong=2)
    ma_yc = unique("QAYC")
    resp = client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": ma_yc,
            "loai": "MUON",
            "items": [{"ma_sach": ma_book, "so_luong": 1}],
            "so_ngay_muon": 5,
        },
        headers=headers("reader1"),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["so_ngay_muon"] == 5
    resp = client.put(
        f"/api/requests/{ma_yc}/approve",
        json={"so_ngay_muon": 7},
        headers=headers("librarian"),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["trang_thai"] == "DA_DUYET"
    assert resp.json()["ma_phieu"] == "PM" + ma_yc
    slips = client.get("/api/borrows", headers=headers("librarian")).json()
    slip = next(s for s in slips if s["ma_phieu"] == "PM" + ma_yc)
    days = (datetime.fromisoformat(slip["han_tra"].replace("Z", "+00:00")) - datetime.fromisoformat(slip["ngay_muon"].replace("Z", "+00:00"))).days
    assert days == 7
    # Duyệt lần 2 -> 400
    assert client.put(f"/api/requests/{ma_yc}/approve", headers=headers("librarian")).status_code == 400


def test_create_muon_so_ngay_muon_exceeds_max(client, headers):
    ma_book = unique("QBRQ2")
    _create_book(client, headers, ma_book, so_luong=2)
    resp = client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": unique("QAYX"),
            "loai": "MUON",
            "items": [{"ma_sach": ma_book, "so_luong": 1}],
            "so_ngay_muon": 30,
        },
        headers=headers("reader1"),
    )
    assert resp.status_code == 400


def test_approve_muon_so_ngay_muon_exceeds_max(client, headers):
    ma_book = unique("QBRQ3")
    _create_book(client, headers, ma_book, so_luong=2)
    ma_yc = unique("QAYY")
    assert client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": ma_yc,
            "loai": "MUON",
            "items": [{"ma_sach": ma_book, "so_luong": 1}],
            "so_ngay_muon": 5,
        },
        headers=headers("reader1"),
    ).status_code == 200
    resp = client.put(
        f"/api/requests/{ma_yc}/approve",
        json={"so_ngay_muon": 30},
        headers=headers("librarian"),
    )
    assert resp.status_code == 400


def test_dat_truoc_request_and_approve(client, headers):
    ma_book = unique("QBRQ4")
    _create_book(client, headers, ma_book, so_luong=0)
    ma_yc = unique("QAYD1")
    resp = client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": ma_yc,
            "loai": "DAT_TRUOC",
            "ma_sach": ma_book,
        },
        headers=headers("reader1"),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["loai"] == "DAT_TRUOC"
    resp = client.put(f"/api/requests/{ma_yc}/approve", headers=headers("librarian"))
    assert resp.status_code == 200, resp.text
    assert resp.json()["trang_thai"] == "DA_DUYET"
    # Phải tạo được đặt trước thật
    reservations = client.get("/api/reservations", headers=headers("reader1")).json()
    assert any(r["ma_sach"] == ma_book and r["trang_thai"] == "CHO_XU_LY" for r in reservations)


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
    ma_book = unique("QBRQ5")
    _create_book(client, headers, ma_book, so_luong=2)
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
    slips = client.get(
        "/api/borrows",
        params={"docGia": "QADG01"},
        headers=headers("librarian"),
    ).json()
    slip = next(s for s in slips if s["ma_phieu"] == ma_phieu)
    assert slip["so_lan_gia_han"] == 1


def test_request_reject(client, headers):
    ma_book = unique("QBRQ6")
    _create_book(client, headers, ma_book, so_luong=2)
    ma_yc = unique("QAYR")
    resp = client.post(
        "/api/requests",
        json={
            "ma_yeu_cau": ma_yc,
            "loai": "MUON",
            "items": [{"ma_sach": ma_book, "so_luong": 1}],
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
    # DAT_TRUOC thiếu sách
    resp = client.post(
        "/api/requests",
        json={"ma_yeu_cau": unique("QAYI5"), "loai": "DAT_TRUOC"},
        headers=headers("reader1"),
    )
    assert resp.status_code == 400
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
    ma_book = unique("QBRQ7")
    _create_book(client, headers, ma_book, so_luong=2)
    ma_yc = unique("QAYP")
    body = {
        "ma_yeu_cau": ma_yc,
        "loai": "MUON",
        "items": [{"ma_sach": ma_book, "so_luong": 1}],
    }
    assert client.post("/api/requests", json=body, headers=headers("reader1")).status_code == 200
    assert client.put(f"/api/requests/{ma_yc}/approve", headers=headers("reader1")).status_code == 403
    assert client.put(f"/api/requests/{ma_yc}/approve", headers=headers("admin")).status_code == 403
    assert client.get("/api/requests", headers=headers("librarian")).status_code == 200


def test_reader_delete_request_history(client, headers):
    ma_book = unique("QBRQ8")
    _create_book(client, headers, ma_book, so_luong=2)
    ma_yc = unique("QAYD")
    body = {
        "ma_yeu_cau": ma_yc,
        "loai": "MUON",
        "items": [{"ma_sach": ma_book, "so_luong": 1}],
    }
    assert client.post("/api/requests", json=body, headers=headers("reader1")).status_code == 200
    assert client.put(f"/api/requests/{ma_yc}/reject", headers=headers("librarian")).status_code == 200
    assert client.delete(f"/api/requests/me/{ma_yc}", headers=headers("reader1")).status_code == 200
    # Yêu cầu đang chờ không xoá được
    ma_yc2 = unique("QAYD2")
    body2 = {
        "ma_yeu_cau": ma_yc2,
        "loai": "MUON",
        "items": [{"ma_sach": ma_book, "so_luong": 1}],
    }
    assert client.post("/api/requests", json=body2, headers=headers("reader1")).status_code == 200
    assert client.delete(f"/api/requests/me/{ma_yc2}", headers=headers("reader1")).status_code == 400
