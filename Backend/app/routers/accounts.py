from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..audit import write_audit_log
from ..database import get_db
from ..deps import require_roles
from ..models import Reader, User
from ..schemas import AccountCreate, AccountOut, AccountUpdate
from ..security import hash_password

router = APIRouter(prefix="/api/admin/accounts", tags=["admin-accounts"])


@router.post("", response_model=AccountOut)
def create_account(
    body: AccountCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> AccountOut:
    if db.query(User).filter(User.username == body.username).first() is not None:
        raise HTTPException(status_code=409, detail="Tên đăng nhập đã tồn tại.")
    reader_id = None
    if body.role == "reader" and body.reader_id:
        if db.get(Reader, body.reader_id) is None:
            raise HTTPException(status_code=404, detail="Không tìm thấy độc giả.")
        if db.query(User).filter(User.reader_id == body.reader_id).first() is not None:
            raise HTTPException(status_code=409, detail="Độc giả đã có tài khoản.")
        reader_id = body.reader_id

    new_user = User(
        username=body.username,
        password_hash=hash_password(body.password),
        ho_ten=body.ho_ten,
        role=body.role,
        reader_id=reader_id,
        is_active=True,
    )
    db.add(new_user)
    db.flush()
    write_audit_log(
        db,
        user,
        "CREATE_ACCOUNT",
        "USER",
        entity_id=str(new_user.id),
        details=f"username={body.username}; role={body.role}",
    )
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("", response_model=list[AccountOut])
def list_accounts(
    role: str | None = Query(None, max_length=20),
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> list[AccountOut]:
    query = db.query(User).filter(User.role.in_(["librarian", "reader"]))
    if role:
        if role not in ("librarian", "reader"):
            raise HTTPException(status_code=422, detail="role chỉ nhận librarian hoặc reader.")
        query = query.filter(User.role == role)
    return query.order_by(User.id.asc()).all()


@router.put("/{user_id}", response_model=AccountOut)
def update_account(
    user_id: int,
    body: AccountUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> AccountOut:
    target = db.get(User, user_id)
    if target is None or target.role not in ("librarian", "reader"):
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản.")
    data = body.model_dump(exclude_unset=True)

    if "reader_id" in data:
        new_reader_id = data["reader_id"]
        if new_reader_id:
            if db.get(Reader, new_reader_id) is None:
                raise HTTPException(status_code=404, detail="Không tìm thấy độc giả.")
            linked = (
                db.query(User)
                .filter(User.reader_id == new_reader_id, User.id != target.id)
                .first()
            )
            if linked is not None:
                raise HTTPException(status_code=409, detail="Độc giả đã có tài khoản.")
        target.reader_id = new_reader_id
    if "role" in data:
        target.role = data["role"]
    if "ho_ten" in data:
        target.ho_ten = data["ho_ten"]
    if "password" in data:
        target.password_hash = hash_password(data["password"])
    if "is_active" in data:
        target.is_active = data["is_active"]

    write_audit_log(
        db,
        user,
        "UPDATE_ACCOUNT",
        "USER",
        entity_id=str(target.id),
        details=f"username={target.username}; changed={','.join(data.keys())}",
    )
    db.commit()
    db.refresh(target)
    return target


@router.delete("/{user_id}")
def delete_account(
    user_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
):
    target = db.get(User, user_id)
    if target is None or target.role not in ("librarian", "reader"):
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản.")
    write_audit_log(
        db,
        user,
        "DELETE_ACCOUNT",
        "USER",
        entity_id=str(target.id),
        details=f"username={target.username}; role={target.role}",
    )
    db.delete(target)
    db.commit()
    return {"message": "Đã xoá tài khoản."}
