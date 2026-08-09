def test_reader_gets_near_due_notification(client, headers):
    resp = client.get("/api/notifications", headers=headers("reader1"))
    assert resp.status_code == 200
    ids = [n["id"] for n in resp.json()]
    assert "BORROW:QAPM01" in ids
    item = next(n for n in resp.json() if n["id"] == "BORROW:QAPM01")
    assert item["loai"] == "SAP_HET_HAN"
    assert item["da_doc"] is False


def test_reader_gets_overdue_notification(client, headers):
    resp = client.get("/api/notifications", headers=headers("reader2"))
    assert resp.status_code == 200
    items = resp.json()
    assert any(n["id"] == "BORROW:QAPM02" and n["loai"] == "QUA_HAN" for n in items)


def test_san_sang_reservation_notification(client, headers):
    resp = client.get("/api/notifications", headers=headers("reader1"))
    items = resp.json()
    assert any(n["id"] == "RES:RVQA03" and n["loai"] == "SACH_SAN_SANG" for n in items)


def test_returned_slips_not_in_notifications(client, headers):
    reader1_ids = [n["id"] for n in client.get("/api/notifications", headers=headers("reader1")).json()]
    reader2_ids = [n["id"] for n in client.get("/api/notifications", headers=headers("reader2")).json()]
    assert "BORROW:QAPM04" not in reader1_ids
    assert "BORROW:QAPM03" not in reader2_ids


def test_notifications_permissions(client, headers):
    assert client.get("/api/notifications", headers=headers("librarian")).status_code == 403
    assert client.get("/api/notifications", headers=headers("admin")).status_code == 403
