from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models import BorrowSlip
from tests.helpers import next_test_email


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _register(client, username: str):
    return client.post(
        "/api/auth/register",
        json={
            "username": username,
            "password": "Pass@123",
            "hoTen": "Độc giả Xuất dữ liệu",
            "email": next_test_email(),
            "soDienThoai": "0911111111",
            "loaiDocGia": "sinh_vien",
        },
    )


def _make_book(client, token: str, ma: str) -> None:
    existing = client.get("/api/books", headers=_headers(token)).json()
    if any(b["ma"] == ma for b in existing):
        return
    response = client.post(
        "/api/books",
        json={
            "anhBia": "https://example.com/cover.jpg", "ma": ma,
            "ten": f"Sách tiếng Việt {ma}",
            "tacGia": "Nguyễn Văn A",
            "theLoai": "Công nghệ",
            "nxb": "NXB Giáo dục",
            "namXb": 2024,
            "soLuong": 5,
        },
        headers=_headers(token),
    )
    assert response.status_code == 200, response.text


def _borrow(client, token: str, ma_phieu: str, reader_ma: str, book_ma: str) -> None:
    response = client.post(
        "/api/borrows",
        json={
            "ma_phieu": ma_phieu,
            "ma_doc_gia": reader_ma,
            "items": [{"ma_sach": book_ma, "so_luong": 1}],
        },
        headers=_headers(token),
    )
    assert response.status_code == 200, response.text


def _set_han_tra(ma_phieu: str, days_offset: int) -> None:
    db = SessionLocal()
    try:
        slip = db.get(BorrowSlip, ma_phieu)
        assert slip is not None
        slip.han_tra = datetime.now() + timedelta(days=days_offset)
        db.commit()
    finally:
        db.close()


def test_export_books_csv(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    admin = tokens["admin"]
    _make_book(client, staff, "TESTEXP1")

    response = client.get("/api/export/books.csv", headers=_headers(admin))
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment" in response.headers["content-disposition"]
    assert "danh_sach_sach_" in response.headers["content-disposition"]
    assert response.headers["content-disposition"].endswith(".csv\"")

    raw = response.content
    assert raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    lines = text.split("\r\n")
    assert lines[0] == "Mã,Tên,Tác giả,Thể loại,NXB,Năm,Số lượng"
    assert any(
        line.startswith("TESTEXP1,") and "Sách tiếng Việt TESTEXP1" in line
        for line in lines
    )


def test_export_borrows_csv(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_exp1").json()
    _make_book(client, staff, "TESTEXP2")
    _borrow(client, staff, "PMEXP1", reader["reader_ma"], "TESTEXP2")
    _borrow(client, staff, "PMEXP2", reader["reader_ma"], "TESTEXP2")
    _set_han_tra("PMEXP2", days_offset=-3)
    client.put("/api/borrows/PMEXP2/return", headers=_headers(staff))

    response = client.get("/api/export/borrows.csv", headers=_headers(staff))
    assert response.status_code == 200
    assert response.content.startswith(b"\xef\xbb\xbf")
    text = response.content.decode("utf-8-sig")
    lines = text.split("\r\n")
    assert (
        lines[0]
        == "Mã phiếu,Mã độc giả,Ngày mượn,Hạn trả,Ngày trả,Trạng thái,Số ngày quá hạn,Điểm phạt"
    )
    active = next(line for line in lines if line.startswith("PMEXP1,"))
    assert "Đang mượn" in active
    returned = next(line for line in lines if line.startswith("PMEXP2,"))
    assert "Đã trả" in returned
    assert ",3,6" in returned


def test_export_report_csv(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    reader = _register(client, "tmp_backend_test_exp2").json()
    _make_book(client, staff, "TESTEXP3")
    _borrow(client, staff, "PMEXP3", reader["reader_ma"], "TESTEXP3")
    _set_han_tra("PMEXP3", days_offset=-2)

    response = client.get("/api/export/report.csv", headers=_headers(staff))
    assert response.status_code == 200
    assert response.content.startswith(b"\xef\xbb\xbf")
    text = response.content.decode("utf-8-sig")
    assert "SÁCH MƯỢN NHIỀU" in text
    assert "Mã sách,Tên sách,Số lần mượn" in text
    assert "ĐỘC GIẢ HOẠT ĐỘNG" in text
    assert "Mã độc giả,Họ tên,Số phiếu mượn" in text
    assert "SÁCH QUÁ HẠN" in text
    assert "Mã phiếu,Mã sách,Tên sách,Mã độc giả,Họ tên,Số ngày quá hạn" in text
    assert "PMEXP3,TESTEXP3,Sách tiếng Việt TESTEXP3" in text


def test_export_permissions(client_and_tokens):
    client, tokens = client_and_tokens
    reader = tokens["reader"]
    for endpoint in ("books.csv", "borrows.csv", "report.csv"):
        assert (
            client.get(f"/api/export/{endpoint}", headers=_headers(reader)).status_code
            == 403
        )
    assert client.get(
        "/api/export/books.csv", headers=_headers(tokens["librarian"])
    ).status_code == 200
    assert client.get(
        "/api/export/books.csv", headers=_headers(tokens["admin"])
    ).status_code == 200


def test_export_reservations_csv(client_and_tokens):
    client, tokens = client_and_tokens
    staff = tokens["librarian"]
    admin = tokens["admin"]

    book = client.post(
        "/api/books",
        json={
            "anhBia": "https://example.com/cover.jpg",
            "ma": "TESTEXPRV1",
            "ten": "Sách Đặt Trước",
            "tacGia": "Tác giả",
            "theLoai": "Test",
            "nxb": "NXB Test",
            "namXb": 2024,
            "soLuong": 1,
        },
        headers=_headers(staff),
    )
    assert book.status_code == 200, book.text

    borrower = _register(client, "tmp_backend_test_exprvbor").json()
    _borrow(client, staff, "PMEXPRV1", borrower["reader_ma"], "TESTEXPRV1")

    reader = _register(client, "tmp_backend_test_exprv").json()
    reservation = client.post(
        "/api/reservations",
        json={"ma_sach": "TESTEXPRV1"},
        headers=_headers(reader["token"]),
    )
    assert reservation.status_code == 200, reservation.text

    response = client.get("/api/export/reservations.csv", headers=_headers(staff))
    assert response.status_code == 200
    assert response.content.startswith(b"\xef\xbb\xbf")
    text = response.content.decode("utf-8-sig")
    lines = text.split("\r\n")
    assert lines[0] == "Mã đặt,Mã sách,Tên sách,Độc giả,Ngày đặt,Trạng thái"
    assert any(
        line.startswith("RV") and "TESTEXPRV1" in line and "Sách Đặt Trước" in line
        for line in lines
    )

    assert client.get(
        "/api/export/reservations.csv",
        headers=_headers(admin),
    ).status_code == 403

    assert client.get(
        "/api/export/reservations.csv",
        headers=_headers(tokens["reader"]),
    ).status_code == 403
