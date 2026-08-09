from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..audit import write_audit_log
from ..database import get_db
from ..deps import require_roles
from ..models import Book, Nxb, TheLoai
from ..schemas import CategoryCreate, CategoryOut, CategoryUpdate, NxbCreate, NxbOut, NxbUpdate

router = APIRouter(prefix="/api/admin", tags=["admin-catalog"])


def _category_out(item: TheLoai) -> CategoryOut:
    return CategoryOut(ma=item.ma, ten=item.ten)


def _nxb_out(item: Nxb) -> NxbOut:
    return NxbOut(ma=item.ma, ten=item.ten)


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> list[CategoryOut]:
    return [_category_out(item) for item in db.query(TheLoai).order_by(TheLoai.ma.asc()).all()]


@router.post("/categories", response_model=CategoryOut)
def create_category(
    body: CategoryCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> CategoryOut:
    if db.get(TheLoai, body.ma) is not None:
        raise HTTPException(status_code=409, detail="Mã thể loại đã tồn tại.")
    item = TheLoai(ma=body.ma, ten=body.ten)
    db.add(item)
    write_audit_log(db, user, "CREATE_CATEGORY", "CATEGORY", entity_id=body.ma)
    db.commit()
    db.refresh(item)
    return _category_out(item)


@router.put("/categories/{ma}", response_model=CategoryOut)
def update_category(
    ma: str,
    body: CategoryUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> CategoryOut:
    item = db.get(TheLoai, ma)
    if item is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy thể loại.")
    item.ten = body.ten
    write_audit_log(db, user, "UPDATE_CATEGORY", "CATEGORY", entity_id=ma)
    db.commit()
    db.refresh(item)
    return _category_out(item)


@router.delete("/categories/{ma}")
def delete_category(
    ma: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
):
    item = db.get(TheLoai, ma)
    if item is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy thể loại.")
    in_use = db.query(Book).filter(Book.theLoaiId == ma).first()
    if in_use is not None:
        raise HTTPException(status_code=400, detail="Thể loại đang được sử dụng bởi sách.")
    write_audit_log(db, user, "DELETE_CATEGORY", "CATEGORY", entity_id=ma)
    db.delete(item)
    db.commit()
    return {"message": "Đã xoá thể loại."}


@router.get("/publishers", response_model=list[NxbOut])
def list_publishers(
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> list[NxbOut]:
    return [_nxb_out(item) for item in db.query(Nxb).order_by(Nxb.ma.asc()).all()]


@router.post("/publishers", response_model=NxbOut)
def create_publisher(
    body: NxbCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> NxbOut:
    if db.get(Nxb, body.ma) is not None:
        raise HTTPException(status_code=409, detail="Mã NXB đã tồn tại.")
    item = Nxb(ma=body.ma, ten=body.ten)
    db.add(item)
    write_audit_log(db, user, "CREATE_PUBLISHER", "PUBLISHER", entity_id=body.ma)
    db.commit()
    db.refresh(item)
    return _nxb_out(item)


@router.put("/publishers/{ma}", response_model=NxbOut)
def update_publisher(
    ma: str,
    body: NxbUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> NxbOut:
    item = db.get(Nxb, ma)
    if item is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy NXB.")
    item.ten = body.ten
    write_audit_log(db, user, "UPDATE_PUBLISHER", "PUBLISHER", entity_id=ma)
    db.commit()
    db.refresh(item)
    return _nxb_out(item)


@router.delete("/publishers/{ma}")
def delete_publisher(
    ma: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
):
    item = db.get(Nxb, ma)
    if item is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy NXB.")
    in_use = db.query(Book).filter(Book.nxbId == ma).first()
    if in_use is not None:
        raise HTTPException(status_code=400, detail="NXB đang được sử dụng bởi sách.")
    write_audit_log(db, user, "DELETE_PUBLISHER", "PUBLISHER", entity_id=ma)
    db.delete(item)
    db.commit()
    return {"message": "Đã xoá NXB."}
