from datetime import datetime

from conftest import unique


def _create_book(client, headers, ma: str, so_luong: int = 2) -> dict:
    body = {
        "ma": ma,
        "ten": f"Sách mượn {ma}",
        "tacGia": "Tác giả QA",
        "theLoai": "Công nghệ QA",
        "nxb": "NXB QA Test",
        "namXb": 2024,
        "soLuong": so_luong,
        "theLoaiId": "QATL1",
        "nxbId": "QANX1",
    }
    resp = client.post("/api/books", json=body, headers=headers("librarian"))
    assert resp.status_code == 200, resp.text
    return body


def _borrow(client, headers, ma_phieu: str, ma_doc_gia: str, items: list[dict], extra=None) -> object:
    payload = {"ma_phieu": ma_phieu, "ma_doc_gia": ma_doc_gia, "items": items}
    if extra:
        payload.update(extra)
    return client.post(
        "/api/borrows",
        json=payload,
        headers=headers("librarian"),
    )


def test_borrow_success_decreases_stock(client, headers):
    ma_book = unique("QBOR")
    _create_book(client, headers, ma_book, so_luong=2)
    ma_phieu = unique("QAPMB")
    resp = _borrow(
        client,
        headers,
        ma_phieu,
        "QADG01",
        [{"ma_sach": ma_book, "so_luong": 1}],
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["trang_thai"] == "dang_muon"
    assert data["so_lan_gia_han"] == 0
    assert data["details"][0]["so_luong"] == 1
    books = client.get("/api/books", headers=headers("reader1")).json()
    stock = next(b["soLuong"] for b in books if b["ma"] == ma_book)
    assert stock == 1


def test_borrow_duplicate_slip(client, headers):
    ma_book = _create_book(client, headers, unique("QBDU"), so_luong=1)["ma"]
    ma_phieu = unique("QAPMBD")
    assert _borrow(client, headers, ma_phieu, "QADG01", [{"ma_sach": ma_book, "so_luong": 1}]).status_code == 200
    resp = _borrow(client, headers, ma_phieu, "QADG01", [{"ma_sach": ma_book, "so_luong": 1}])
    assert resp.status_code == 409


def test_borrow_unknown_reader(client, headers):
    resp = _borrow(
        client,
        headers,
        unique("QAPMUR"),
        "QADG99",
        [{"ma_sach": "QAS002", "so_luong": 1}],
    )
    assert resp.status_code == 404


def test_borrow_locked_card(client, headers):
    resp = _borrow(
        client,
        headers,
        unique("QAPMLK"),
        "QADG03",
        [{"ma_sach": "QAS002", "so_luong": 1}],
    )
    assert resp.status_code == 400


def test_borrow_out_of_stock(client, headers):
    resp = _borrow(
        client,
        headers,
        unique("QAPMOS"),
        "QADG01",
        [{"ma_sach": "QAS003", "so_luong": 1}],
    )
    assert resp.status_code == 400


def test_borrow_insufficient_quantity(client, headers):
    ma_book = _create_book(client, headers, unique("QBIN"), so_luong=1)["ma"]
    resp = _borrow(
        client,
        headers,
        unique("QAPMIN"),
        "QADG01",
        [{"ma_sach": ma_book, "so_luong": 2}],
    )
    assert resp.status_code == 400


def test_borrow_exceeds_limit(client, headers):
    ma_book = _create_book(client, headers, unique("QBEX"), so_luong=10)["ma"]
    resp = _borrow(
        client,
        headers,
        unique("QAPMEX"),
        "QADG01",
        [{"ma_sach": ma_book, "so_luong": 4}],
    )
    assert resp.status_code == 400


def test_borrow_zero_and_empty_items(client, headers):
    resp = _borrow(
        client,
        headers,
        unique("QAPMZ1"),
        "QADG01",
        [{"ma_sach": "QAS002", "so_luong": 0}],
    )
    assert resp.status_code == 422
    resp = _borrow(client, headers, unique("QAPMZ2"), "QADG01", [])
    assert resp.status_code == 422


def test_borrow_unknown_book(client, headers):
    resp = _borrow(
        client,
        headers,
        unique("QAPMUB"),
        "QADG01",
        [{"ma_sach": "QBKHOONG", "so_luong": 1}],
    )
    assert resp.status_code == 404


def test_borrow_role_permissions(client, headers):
    body = {
        "ma_phieu": unique("QAPMRO"),
        "ma_doc_gia": "QADG01",
        "items": [{"ma_sach": "QAS002", "so_luong": 1}],
    }
    assert client.post("/api/borrows", json=body, headers=headers("reader1")).status_code == 403
    assert client.post("/api/borrows", json=body, headers=headers("admin")).status_code == 403


def test_borrow_extra_so_ngay_muon_ignored(client, headers):
    # BUG-002: trang Mượn/Trả vẫn gửi so_ngay_muon nhưng Backend bỏ qua
    ma_book = _create_book(client, headers, unique("QBSO"), so_luong=2)["ma"]
    ma_phieu = unique("QAPMSO")
    resp = _borrow(
        client,
        headers,
        ma_phieu,
        "QADG01",
        [{"ma_sach": ma_book, "so_luong": 1}],
        extra={"so_ngay_muon": 3},
    )
    assert resp.status_code == 200
    days = (datetime.fromisoformat(resp.json()["han_tra"].replace("Z", "+00:00")) - datetime.fromisoformat(resp.json()["ngay_muon"].replace("Z", "+00:00"))).days
    assert days == 14, f"so_ngay_muon=3 bị bỏ qua, thực tế {days} ngày (BUG-002)"


def test_return_on_time_no_fine(client, headers):
    ma_book = _create_book(client, headers, unique("QBRT"), so_luong=1)["ma"]
    ma_phieu = unique("QAPMRT")
    assert _borrow(client, headers, ma_phieu, "QADG01", [{"ma_sach": ma_book, "so_luong": 1}]).status_code == 200
    resp = client.put(f"/api/borrows/{ma_phieu}/return", headers=headers("librarian"))
    assert resp.status_code == 200, resp.text
    assert resp.json()["fine"] is None
    books = client.get("/api/books", headers=headers("reader1")).json()
    assert next(b["soLuong"] for b in books if b["ma"] == ma_book) == 1


def test_return_late_creates_fine_points(client, headers):
    # QAPM07: đang mượn quá hạn (seed)
    resp = client.put("/api/borrows/QAPM07/return", headers=headers("librarian"))
    assert resp.status_code == 200, resp.text
    fine = resp.json()["fine"]
    assert fine is not None
    assert fine["so_ngay_qua_han"] >= 2
    assert fine["so_diem"] == fine["so_ngay_qua_han"] * 2


def test_return_already_returned(client, headers):
    resp = client.put("/api/borrows/QAPM03/return", headers=headers("librarian"))
    assert resp.status_code == 400


def test_return_unknown_slip(client, headers):
    resp = client.put(f"/api/borrows/{unique('QAPMNF')}/return", headers=headers("librarian"))
    assert resp.status_code == 404


def test_renew_success_once_twice_fails(client, headers):
    ma_book = _create_book(client, headers, unique("QBRN"), so_luong=1)["ma"]
    ma_phieu = unique("QAPMRN")
    assert _borrow(client, headers, ma_phieu, "QADG01", [{"ma_sach": ma_book, "so_luong": 1}]).status_code == 200
    resp = client.put(f"/api/borrows/{ma_phieu}/renew", headers=headers("librarian"))
    assert resp.status_code == 200, resp.text
    assert resp.json()["so_lan_gia_han"] == 1
    assert resp.json()["fine"] is None
    resp2 = client.put(f"/api/borrows/{ma_phieu}/renew", headers=headers("librarian"))
    assert resp2.status_code == 400


def test_renew_late_adds_fine_points(client, headers):
    # QAPM06: đang mượn quá hạn (seed)
    resp = client.put("/api/borrows/QAPM06/renew", headers=headers("librarian"))
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["fine"] is not None
    assert data["fine"]["so_ngay_qua_han"] >= 2
    assert data["fine"]["so_diem"] == data["fine"]["so_ngay_qua_han"] * 2
    assert data["so_lan_gia_han"] == 1


def test_renew_with_reservation_fails(client, headers):
    # QAPM02 mượn QAS001, QAS001 có RVQA01 đang chờ -> không gia hạn được
    resp = client.put("/api/borrows/QAPM02/renew", headers=headers("librarian"))
    assert resp.status_code == 400


def test_collect_fine_points_success_twice_fails(client, headers):
    # QAPM04 đã trả trễ 2 ngày = 4 điểm, chưa thu
    resp = client.post("/api/borrows/QAPM04/collect-fine", headers=headers("librarian"))
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["so_diem_da_thu"] == 4
    assert data["diem_con_lai"] == 96
    resp2 = client.post("/api/borrows/QAPM04/collect-fine", headers=headers("librarian"))
    assert resp2.status_code == 400


def test_collect_fine_not_returned(client, headers):
    resp = client.post("/api/borrows/QAPM01/collect-fine", headers=headers("librarian"))
    assert resp.status_code == 400


def test_borrow_list_filters_and_permissions(client, headers):
    resp = client.get(
        "/api/borrows",
        params={"docGia": "QADG01", "trangThai": "dang_muon"},
        headers=headers("librarian"),
    )
    assert resp.status_code == 200
    assert all(s["ma_doc_gia"] == "QADG01" and s["trang_thai"] == "dang_muon" for s in resp.json())
    resp = client.get("/api/borrows", params={"trangThai": "sai"}, headers=headers("librarian"))
    assert resp.status_code == 422
    assert client.get("/api/borrows", headers=headers("reader1")).status_code == 403
    assert client.get("/api/borrows", headers=headers("admin")).status_code == 403
