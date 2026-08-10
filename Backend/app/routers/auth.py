import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..audit import write_audit_log
from ..database import get_db
from ..models import Reader, User
from ..schemas import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse
from ..security import create_access_token, hash_password, verify_password
from ..validation import (
    ensure_email_unique,
    validate_email,
    validate_ho_ten,
    validate_password,
    validate_phone,
    validate_username,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    username = (body.username or "").strip()
    password = body.password or ""
    if not username:
        raise HTTPException(status_code=400, detail="Vui lòng nhập tên đăng nhập.")
    if not password:
        raise HTTPException(status_code=400, detail="Vui lòng nhập mật khẩu.")

    user = db.query(User).filter(User.username == username).first()
    if user is None or not verify_password(body.password, user.password_hash):
        write_audit_log(
            db,
            None,
            "LOGIN_FAILED",
            "LOGIN",
            details=f"username={body.username}",
        )
        db.commit()
        raise HTTPException(
            status_code=401,
            detail="Tên đăng nhập hoặc mật khẩu không đúng.",
        )
    if not user.is_active:
        write_audit_log(
            db,
            user,
            "LOGIN_LOCKED",
            "LOGIN",
            details=f"username={user.username}",
        )
        db.commit()
        raise HTTPException(status_code=401, detail="Tài khoản đã bị khoá.")
    token = create_access_token(username=user.username, role=user.role, name=user.ho_ten)
    write_audit_log(
        db,
        user,
        "LOGIN_SUCCESS",
        "LOGIN",
        details=f"username={user.username}",
    )
    db.commit()
    return LoginResponse(
        token=token,
        role=user.role,
        role_display=user.role_display,
        name=user.ho_ten,
    )


@router.post("/register", response_model=RegisterResponse)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    username = validate_username(body.username)
    password = validate_password(body.password)
    if db.query(User).filter(User.username == body.username).first() is not None:
        raise HTTPException(status_code=409, detail="Tên đăng nhập đã tồn tại.")
    ho_ten = validate_ho_ten(body.hoTen)
    email = validate_email(body.email)
    so_dien_thoai = validate_phone(body.soDienThoai)
    ensure_email_unique(db, email)

    reader_ma = None
    for _ in range(5):
        candidate = (
            "DG"
            + datetime.now().strftime("%Y%m%d%H%M%S")
            + f"{secrets.randbelow(1000):03d}"
        )
        if db.get(Reader, candidate) is None:
            reader_ma = candidate
            break
    if reader_ma is None:
        raise HTTPException(status_code=500, detail="Không tạo được mã độc giả, vui lòng thử lại.")

    reader = Reader(
        ma=reader_ma,
        hoTen=ho_ten,
        email=email,
        soDienThoai=so_dien_thoai,
        loaiDocGia=body.loaiDocGia,
        trangThaiThe="hoat_dong",
        ngayTao=datetime.now(),
    )
    db.add(reader)
    user = User(
        username=body.username,
        password_hash=hash_password(password),
        ho_ten=ho_ten,
        email=email,
        so_dien_thoai=so_dien_thoai,
        role="reader",
        reader_id=reader_ma,
        is_active=True,
    )
    db.add(user)
    write_audit_log(
        db,
        user,
        "REGISTER_READER",
        "USER",
        entity_id=reader_ma,
        details=f"username={body.username}",
    )
    db.commit()
    token = create_access_token(username=user.username, role=user.role, name=user.ho_ten)
    return RegisterResponse(
        token=token,
        role=user.role,
        role_display=user.role_display,
        name=ho_ten,
        reader_ma=reader_ma,
    )
