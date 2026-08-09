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


def test_cancel_other_reader_forbidden(client, headers):
    # RVQA03 thuộc reader1; reader2 không được hủy
    resp = client.put("/api/reservations/RVQA03/cancel", headers=headers("reader2"))
    assert resp.status_code == 404


def test_cancel_non_pending_fails(client, headers):
    # RVQA03 đã SAN_SANG, không hủy được
    resp = client.put("/api/reservations/RVQA03/cancel", headers=headers("reader1"))
    assert resp.status_code == 400


def test_fulfill_by_librarian(client, headers):
    resp = client.put("/api/reservations/RVQA01/fulfill", headers=headers("librarian"))
    assert resp.status_code == 200, resp.text
    assert resp.json()["trang_thai"] == "SAN_SANG"
    # fulfill lần 2 -> 400
    resp2 = client.put("/api/reservations/RVQA01/fulfill", headers=headers("librarian"))
    assert resp2.status_code == 400


def test_fulfill_permissions(client, headers):
    resp = client.put("/api/reservations/RVQA03/fulfill", headers=headers("reader1"))
    assert resp.status_code == 403
    resp = client.put("/api/reservations/RVQA03/fulfill", headers=headers("admin"))
    assert resp.status_code == 403


def test_list_reader_sees_own_only(client, headers):
    resp = client.get("/api/reservations", headers=headers("reader1"))
    assert resp.status_code == 200
    rows = resp.json()
    assert rows
    assert all(r["ma_doc_gia"] == "QADG01" for r in rows)
    assert not any(r["ma_dat"] == "RVQA01" for r in rows)


def test_list_admin_forbidden(client, headers):
    assert client.get("/api/reservations", headers=headers("admin")).status_code == 403
