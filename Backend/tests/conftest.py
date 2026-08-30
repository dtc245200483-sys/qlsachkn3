import glob
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.config import AVATAR_DIR
from app.database import SessionLocal
from app.main import app
from app.models import User
from app.security import hash_password

TEST_PASSWORD = "Test@12345"
TEST_USER_PREFIX = "tmp_backend_test_"


def _create_user(username: str, role: str) -> None:
    db = SessionLocal()
    try:
        db.add(
            User(
                username=username,
                password_hash=hash_password(TEST_PASSWORD),
                ho_ten=username,
                role=role,
                is_active=True,
            )
        )
        db.commit()
    finally:
        db.close()


def _cleanup_test_data() -> None:
    db = SessionLocal()
    try:
        db.execute(
            text(
                "DELETE FROM DatTruoc WHERE ma_dat LIKE 'RV%' "
                "AND (ma_doc_gia LIKE 'TEST%' OR ma_doc_gia IN "
                "(SELECT ma FROM Readers WHERE email LIKE 'DTC700%@ictu.edu.vn'))"
            )
        )
        db.execute(
            text(
                "DELETE FROM DocThongBao WHERE ma_doc_gia LIKE 'TEST%' "
                "OR ma_doc_gia IN (SELECT ma FROM Readers WHERE email LIKE 'DTC700%@ictu.edu.vn')"
            )
        )
        db.execute(
            text(
                "DELETE FROM AnThongBao WHERE ma_doc_gia LIKE 'TEST%' "
                "OR ma_doc_gia IN (SELECT ma FROM Readers WHERE email LIKE 'DTC700%@ictu.edu.vn')"
            )
        )
        db.execute(
            text(
                "DELETE FROM YeuCau WHERE ma_yeu_cau LIKE 'YCTEST%' OR ma_yeu_cau LIKE 'YCRDT%' OR ma_yeu_cau LIKE 'TEST%'"
                " OR ma_yeu_cau LIKE 'YCSO%' OR ma_doc_gia LIKE 'TEST%' OR ma_doc_gia IN (SELECT ma FROM Readers WHERE email LIKE 'DTC700%@ictu.edu.vn')"
            )
        )
        db.execute(
            text(
                "DELETE FROM FineHistory WHERE ma_phieu LIKE 'PMTEST%' OR ma_phieu LIKE 'PMYC%' OR ma_phieu LIKE 'PMHIST%' OR ma_phieu LIKE 'PMRSV%' OR ma_phieu LIKE 'PMNTF%' OR ma_phieu LIKE 'PMSTT%' OR ma_phieu LIKE 'PMEXP%' OR ma_phieu LIKE 'PMFINE%' OR ma_phieu LIKE 'TEST%'"
            )
        )
        db.execute(
            text(
                "DELETE FROM BorrowDetails WHERE copy_id LIKE 'TEST%' OR copy_id IN (SELECT copy_id FROM BookCopies WHERE book_id LIKE 'TEST%') OR ma_phieu LIKE 'PMTEST%' OR ma_phieu LIKE 'PMYC%' OR ma_phieu LIKE 'PMHIST%' OR ma_phieu LIKE 'PMRSV%' OR ma_phieu LIKE 'PMNTF%' OR ma_phieu LIKE 'PMSTT%' OR ma_phieu LIKE 'PMEXP%' OR ma_phieu LIKE 'PMFINE%' OR ma_phieu LIKE 'TEST%'"
            )
        )
        db.execute(
            text(
                "DELETE FROM BorrowSlips WHERE ma_phieu LIKE 'PMTEST%' OR ma_phieu LIKE 'PMYC%' OR ma_phieu LIKE 'PMHIST%' OR ma_phieu LIKE 'PMRSV%' OR ma_phieu LIKE 'PMNTF%' OR ma_phieu LIKE 'PMSTT%' OR ma_phieu LIKE 'PMEXP%' OR ma_phieu LIKE 'PMFINE%' OR ma_phieu LIKE 'TEST%'"
            )
        )
        db.execute(text("DELETE FROM BookCopies WHERE book_id LIKE 'TEST%' OR copy_id LIKE 'TEST%'"))
        db.execute(text("DELETE FROM Books WHERE ma LIKE 'TEST%'"))
        db.execute(
            text(
                "DELETE FROM Users WHERE username LIKE 'tmp_backend_test_%' "
                "OR reader_id IN (SELECT ma FROM Readers WHERE ma LIKE 'TEST%' "
                "OR email LIKE 'DTC700%@ictu.edu.vn')"
            )
        )
        db.execute(
            text(
                "DELETE FROM Readers WHERE ma LIKE 'TEST%' "
                "OR email LIKE 'DTC700%@ictu.edu.vn'"
            )
        )
        db.execute(text("DELETE FROM TheLoai WHERE ma LIKE 'TEST%'"))
        db.execute(text("DELETE FROM Nxb WHERE ma LIKE 'TEST%'"))
        db.execute(text("DELETE FROM AuditLog WHERE username LIKE 'tmp_backend_test_%'"))
        db.commit()
    finally:
        db.close()

    for path in glob.glob(os.path.join(AVATAR_DIR, "tmp_backend_test_*.*")):
        try:
            os.remove(path)
        except OSError:
            pass


@pytest.fixture(scope="module")
def client_and_tokens():
    _cleanup_test_data()
    _create_user(f"{TEST_USER_PREFIX}admin", "admin")
    _create_user(f"{TEST_USER_PREFIX}librarian", "librarian")
    _create_user(f"{TEST_USER_PREFIX}reader", "reader")

    client = TestClient(app)

    def login(username: str) -> str:
        response = client.post(
            "/api/auth/login",
            json={"username": username, "password": TEST_PASSWORD},
        )
        assert response.status_code == 200, response.text
        return response.json()["token"]

    tokens = {
        "admin": login(f"{TEST_USER_PREFIX}admin"),
        "librarian": login(f"{TEST_USER_PREFIX}librarian"),
        "reader": login(f"{TEST_USER_PREFIX}reader"),
    }
    yield client, tokens
    _cleanup_test_data()
