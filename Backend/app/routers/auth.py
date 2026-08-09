import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..audit import write_audit_log
from ..database import get_db
from ..models import Reader, User
from ..schemas import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse
from ..security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    user = db.query(User).filter(User.username == body.username).first()
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
    return LoginResponse(token=token, role=user.role, name=user.ho_ten)


@router.post("/register", response_model=RegisterResponse)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    if db.query(User).filter(User.username == body.username).first() is not None:
        raise HTTPException(status_code=409, detail="Tên đăng nhập đã tồn tại.")
    if db.query(Reader).filter(Reader.email == body.email).first() is not None:
        raise HTTPException(status_code=409, detail="Email đã được sử dụng.")

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
        hoTen=body.hoTen,
        email=body.email,
        soDienThoai=body.soDienThoai,
        loaiDocGia=body.loaiDocGia,
        trangThaiThe="hoat_dong",
        ngayTao=datetime.now(),
    )
    db.add(reader)
    user = User(
        username=body.username,
        password_hash=hash_password(body.password),
        ho_ten=body.hoTen,
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
        name=user.ho_ten,
        reader_ma=reader_ma,
    )
