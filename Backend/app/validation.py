import re

from fastapi import HTTPException
from sqlalchemy.orm import Session

from .models import Reader, User

NAME_PART_RE = re.compile(r"^[^\W\d_]+$")
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@ictu\.edu\.vn$")
PHONE_RE = re.compile(r"^(0|\+84)(3|5|7|8|9)\d{8}$")


def validate_ho_ten(value: str) -> str:
    value = (value or "").strip()
    if not value:
        raise HTTPException(status_code=422, detail="Họ tên là bắt buộc.")
    parts = value.split()
    if len(parts) < 2:
        raise HTTPException(
            status_code=422,
            detail="Họ tên phải có ít nhất 2 từ (VD: Nguyễn Văn An).",
        )
    for part in parts:
        if len(part) < 2:
            raise HTTPException(
                status_code=422,
                detail="Mỗi từ trong họ tên phải có ít nhất 2 ký tự.",
            )
        if not NAME_PART_RE.match(part):
            raise HTTPException(
                status_code=422,
                detail="Họ tên không được chứa số hoặc ký tự đặc biệt.",
            )
    return value


def validate_email(value: str) -> str:
    value = (value or "").strip().lower()
    if not value:
        raise HTTPException(status_code=422, detail="Email là bắt buộc.")
    if not EMAIL_RE.match(value):
        raise HTTPException(
            status_code=422,
            detail="Email phải đúng định dạng ICTU (VD: DTC245200483@ictu.edu.vn).",
        )
    return value


def validate_phone(value: str) -> str:
    value = (value or "").strip()
    if not value:
        raise HTTPException(status_code=422, detail="Số điện thoại là bắt buộc.")
    if not PHONE_RE.match(value):
        raise HTTPException(
            status_code=422,
            detail="Số điện thoại Việt Nam không hợp lệ (VD: 0912345001).",
        )
    return value


def ensure_email_unique(
    db: Session,
    email: str,
    exclude_user_id: int | None = None,
    exclude_reader_ma: str | None = None,
) -> None:
    q_user = db.query(User).filter(User.email == email)
    if exclude_user_id is not None:
        q_user = q_user.filter(User.id != exclude_user_id)
    if q_user.first() is not None:
        raise HTTPException(status_code=409, detail="Email đã được sử dụng.")

    q_reader = db.query(Reader).filter(Reader.email == email)
    if exclude_reader_ma is not None:
        q_reader = q_reader.filter(Reader.ma != exclude_reader_ma)
    if q_reader.first() is not None:
        raise HTTPException(status_code=409, detail="Email đã được sử dụng.")
