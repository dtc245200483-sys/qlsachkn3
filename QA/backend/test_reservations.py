from conftest import unique


def test_list_invalid_status(client, headers):
    resp = client.get(
        "/api/reservations",
        params={"trangThai": "sai"},
        headers=headers("reader1"),
    )
    assert resp.status_code == 422


def test_reserve_available_book_fails(client, headers):
    resp = client.post(
        "/api/reservations",
        json={"ma_sach": "QAS004"},
        headers=headers("reader1"),
    )
    assert resp.status_code == 400


def test_reserve_unknown_book(client, headers):
    resp = client.post(
        "/api/reservations",
        json={"ma_sach": "QAS999"},
        headers=headers("reader1"),
    )
    assert resp.status_code == 404


def test_reserve_duplicate_fails(client, headers):
    # QAS001 đã có RVQA01 (reader2, CHO_XU_LY)
    resp = client.post(
        "/api/reservations",
        json={"ma_sach": "QAS001"},
        headers=headers("reader2"),
    )
    assert resp.status_code == 409


def test_cancel_other_reader_forbidden(client, headers):
    # RVQA03 thuộc reader1; reader2 không được hủy
    resp = client.put("/api/reservations/RVQA03/cancel", headers=headers("reader2"))
    assert resp.status_code == 404


def test_reader_cancel_san_sang_fails(client, headers):
    # RVQA03 đã SAN_SANG, reader không huỷ được
    resp = client.put("/api/reservations/RVQA03/cancel", headers=headers("reader1"))
    assert resp.status_code == 400


def test_librarian_cancel_san_sang(client, headers):
    resp = client.put("/api/reservations/RVQA03/cancel", headers=headers("librarian"))
    assert resp.status_code == 200
    assert resp.json()["trang_thai"] == "HUY"


def test_reserve_success_and_duplicate(client, headers):
    # Hủy RVQA02 trước, rồi đặt lại QAS003
    resp = client.put("/api/reservations/RVQA02/cancel", headers=headers("reader1"))
    assert resp.status_code == 200
    assert resp.json()["trang_thai"] == "HUY"
    resp = client.post(
        "/api/reservations",
        json={"ma_sach": "QAS003"},
        headers=headers("reader1"),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["trang_thai"] == "CHO_XU_LY"
    assert resp.json()["ten_sach"]
    assert resp.json()["ma_doc_gia"] == "QADG01"
    resp2 = client.post(
        "/api/reservations",
        json={"ma_sach": "QAS003"},
        headers=headers("reader1"),
    )
    assert resp2.status_code == 409


def test_delete_reservation_history(client, headers):
    # RVQA02 đã HUY -> reader xoá được
    assert client.delete("/api/reservations/me/RVQA02", headers=headers("reader1")).status_code == 200
    # Đặt trước đang chờ (mới tạo ở test trước) -> không xoá được
    active = [r for r in client.get("/api/reservations", headers=headers("reader1")).json() if r["trang_thai"] == "CHO_XU_LY"]
    assert active
    assert client.delete(f"/api/reservations/me/{active[0]['ma_dat']}", headers=headers("reader1")).status_code == 400
    # Phiếu của reader2 -> reader1 không xoá được
    assert client.delete("/api/reservations/me/RVQA01", headers=headers("reader1")).status_code == 404


def test_fulfill_and_confirm_borrow_flow(client, headers):
    # Tìm đặt trước CHO_XU_LY của reader1 (QAS003)
    active = [r for r in client.get("/api/reservations", headers=headers("reader1")).json() if r["trang_thai"] == "CHO_XU_LY" and r["ma_sach"] == "QAS003"]
    assert active
    ma_dat = active[0]["ma_dat"]
    # Chưa có sách -> fulfill phải báo lỗi
    assert client.put(f"/api/reservations/{ma_dat}/fulfill", headers=headers("librarian")).status_code == 400
    # Admin bổ sung tồn kho
    book = client.get("/api/books", headers=headers("librarian")).json()
    book = next(b for b in book if b["ma"] == "QAS003")
    book["soLuong"] = 2
    assert client.put("/api/books/QAS003", json=book, headers=headers("admin")).status_code == 200
    # Fulfill -> SAN_SANG
    resp = client.put(f"/api/reservations/{ma_dat}/fulfill", headers=headers("librarian"))
    assert resp.status_code == 200, resp.text
    assert resp.json()["trang_thai"] == "SAN_SANG"
    # Fulfill lần 2 -> 400
    assert client.put(f"/api/reservations/{ma_dat}/fulfill", headers=headers("librarian")).status_code == 400
    # Xác nhận đã lấy -> DA_MUON + tạo phiếu mượn
    resp = client.put(f"/api/reservations/{ma_dat}/borrow", headers=headers("librarian"))
    assert resp.status_code == 200, resp.text
    assert resp.json()["trang_thai"] == "DA_MUON"
    books = client.get("/api/books", headers=headers("librarian")).json()
    assert next(b["soLuong"] for b in books if b["ma"] == "QAS003") == 1


def test_fulfill_permissions(client, headers):
    assert client.put("/api/reservations/RVQA01/fulfill", headers=headers("reader1")).status_code == 403
    assert client.put("/api/reservations/RVQA01/fulfill", headers=headers("admin")).status_code == 403


def test_list_reader_sees_own_only(client, headers):
    resp = client.get("/api/reservations", headers=headers("reader1"))
    assert resp.status_code == 200
    rows = resp.json()
    assert rows
    assert all(r["ma_doc_gia"] == "QADG01" for r in rows)
    assert not any(r["ma_dat"] == "RVQA01" for r in rows)


def test_delete_all_processed_history(client, headers):
    resp = client.delete("/api/reservations/me", headers=headers("reader1"))
    assert resp.status_code == 200
    assert resp.json()["so_phieu_da_xoa"] >= 1


def test_librarian_delete_processed_history(client, headers):
    # Tạo tình huống HUY cho reader2, librarian xoá được
    resp = client.put("/api/reservations/RVQA01/cancel", headers=headers("librarian"))
    assert resp.status_code == 200
    assert resp.json()["trang_thai"] == "HUY"
    resp = client.delete("/api/reservations/me/RVQA01", headers=headers("librarian"))
    assert resp.status_code == 200
    # Xoá toàn bộ theo quyền librarian cũng chạy (không lỗi)
    resp = client.delete("/api/reservations/me", headers=headers("librarian"))
    assert resp.status_code == 200
    assert resp.json()["so_phieu_da_xoa"] >= 0


def test_list_admin_forbidden(client, headers):
    assert client.get("/api/reservations", headers=headers("admin")).status_code == 403
