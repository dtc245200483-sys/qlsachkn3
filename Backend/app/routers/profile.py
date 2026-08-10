import os
import re

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..audit import write_audit_log
from ..config import AVATAR_DIR
from ..database import get_db
from ..deps import get_current_user
from ..models import Reader, User
from ..schemas import AvatarOut, ChangePasswordRequest, ProfileOut, ProfileUpdate
from ..security import hash_password, verify_password
from ..validation import (
    ensure_email_unique,
    validate_email,
    validate_ho_ten,
    validate_password,
    validate_phone,
)

router = APIRouter(prefix="/api/profile", tags=["profile"])

ALLOWED_AVATAR_TYPES = {"image/png": ".png", "image/jpeg": ".jpg"}
MAX_AVATAR_SIZE = 2 * 1024 * 1024


def _safe_username(username: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", username)


def _avatar_url(username: str) -> str:
    safe = _safe_username(username)
    for ext in (".png", ".jpg"):
        if os.path.isfile(os.path.join(AVATAR_DIR, safe + ext)):
            return f"/static/avatars/{safe}{ext}"
    return ""


def _reader_of(db: Session, user: User) -> Reader | None:
    if user.reader_id:
        return db.get(Reader, user.reader_id)
    return None


def _profile_out(db: Session, user: User) -> ProfileOut:
    reader = _reader_of(db, user)
    return ProfileOut(
        username=user.username,
        ho_ten=user.ho_ten,
        role=user.role,
        email=reader.email if reader is not None else (user.email or ""),
        so_dien_thoai=reader.soDienThoai if reader is not None else (user.so_dien_thoai or ""),
        loai_doc_gia=reader.loaiDocGia if reader is not None else "",
        avatar_url=_avatar_url(user.username),
    )


@router.get("/me", response_model=ProfileOut)
def get_profile(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> ProfileOut:
    return _profile_out(db, user)


@router.put("/me", response_model=ProfileOut)
def update_profile(
    body: ProfileUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> ProfileOut:
    data = body.model_dump(exclude_unset=True)
    if "ho_ten" in data:
        user.ho_ten = validate_ho_ten(data["ho_ten"])

    reader = _reader_of(db, user)
    if "email" in data:
        email = validate_email(data["email"])
        ensure_email_unique(
            db,
            email,
            exclude_user_id=user.id,
            exclude_reader_ma=reader.ma if reader is not None else None,
        )
        user.email = email
        if reader is not None:
            reader.email = email
    if "so_dien_thoai" in data:
        so_dien_thoai = validate_phone(data["so_dien_thoai"])
        user.so_dien_thoai = so_dien_thoai
        if reader is not None:
            reader.soDienThoai = so_dien_thoai
    if "loai_doc_gia" in data and reader is not None:
        reader.loaiDocGia = data["loai_doc_gia"]

    write_audit_log(
        db,
        user,
        "UPDATE_PROFILE",
        "USER",
        entity_id=user.username,
        details=f"changed={','.join(data.keys())}",
    )
    db.commit()
    db.refresh(user)
    return _profile_out(db, user)


@router.put("/me/password")
def change_password(
    body: ChangePasswordRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if not verify_password(body.mat_khau_cu, user.password_hash):
        raise HTTPException(status_code=400, detail="Mật khẩu cũ không đúng.")
    password_moi = validate_password(body.mat_khau_moi)
    if body.xac_nhan is not None and body.xac_nhan != body.mat_khau_moi:
        raise HTTPException(
            status_code=400,
            detail="Xác nhận mật khẩu mới không khớp.",
        )
    user.password_hash = hash_password(password_moi)
    write_audit_log(
        db,
        user,
        "CHANGE_PASSWORD",
        "USER",
        entity_id=user.username,
    )
    db.commit()
    return {"message": "Đã đổi mật khẩu."}


@router.post("/me/avatar", response_model=AvatarOut)
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> AvatarOut:
    ext = ALLOWED_AVATAR_TYPES.get(file.content_type or "")
    if ext is None:
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận ảnh PNG hoặc JPG.")
    data = await file.read()
    if len(data) > MAX_AVATAR_SIZE:
        raise HTTPException(status_code=400, detail="Ảnh đại diện tối đa 2MB.")

    os.makedirs(AVATAR_DIR, exist_ok=True)
    safe = _safe_username(user.username)
    for old_ext in (".png", ".jpg"):
        old_path = os.path.join(AVATAR_DIR, safe + old_ext)
        if os.path.isfile(old_path):
            os.remove(old_path)
    path = os.path.join(AVATAR_DIR, safe + ext)
    with open(path, "wb") as f:
        f.write(data)

    write_audit_log(
        db,
        user,
        "UPDATE_AVATAR",
        "USER",
        entity_id=user.username,
    )
    db.commit()
    return AvatarOut(avatar_url=f"/static/avatars/{safe}{ext}")
