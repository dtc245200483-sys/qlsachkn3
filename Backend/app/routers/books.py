from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_roles
from ..models import Book, BorrowDetail, BorrowSlip, Nxb, TheLoai
from ..schemas import BookBase
from ..audit import write_audit_log

router = APIRouter(prefix="/api/books", tags=["books"])


@router.get("", response_model=list[BookBase])
def list_books(
    q: str | None = Query(None, max_length=255),
    theLoai: str | None = Query(None, max_length=100),
    trangThai: str | None = Query(None, max_length=20),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> list[BookBase]:
    query = db.query(Book)
    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(
                Book.ten.like(pattern),
                Book.tacGia.like(pattern),
            )
        )
    if theLoai:
        query = query.filter(Book.theLoai == theLoai)
    if trangThai:
        if trangThai == "con":
            query = query.filter(Book.soLuong > 0)
        elif trangThai == "dang_muon":
            borrowed_ma = (
                db.query(BorrowDetail.ma_sach)
                .join(BorrowSlip, BorrowSlip.ma_phieu == BorrowDetail.ma_phieu)
                .filter(
                    BorrowSlip.trang_thai == "dang_muon",
                    BorrowDetail.ngay_tra_chi_tiet.is_(None),
                )
                .distinct()
            )
            query = query.filter(
                or_(
                    Book.soLuong == 0,
                    Book.ma.in_(borrowed_ma),
                )
            )
        else:
            raise HTTPException(
                status_code=422,
                detail="trangThai chỉ nhận 'con' hoặc 'dang_muon'.",
            )
    return query.order_by(Book.ma.asc()).all()


@router.post("", response_model=BookBase)
def create_book(
    body: BookBase,
    db: Session = Depends(get_db),
    user=Depends(require_roles("librarian", "admin")),
) -> BookBase:
    if db.get(Book, body.ma) is not None:
        raise HTTPException(status_code=409, detail="Mã sách đã tồn tại.")
    if body.theLoaiId and db.get(TheLoai, body.theLoaiId) is None:
        raise HTTPException(status_code=422, detail="Thể loại không tồn tại.")
    if body.nxbId and db.get(Nxb, body.nxbId) is None:
        raise HTTPException(status_code=422, detail="NXB không tồn tại.")
    book = Book(**body.model_dump())
    db.add(book)
    write_audit_log(
        db,
        user,
        "CREATE_BOOK",
        "BOOK",
        entity_id=body.ma,
        details=f"ten={body.ten}",
    )
    db.commit()
    db.refresh(book)
    return book


@router.put("/{ma}", response_model=BookBase)
def update_book(
    ma: str,
    body: BookBase,
    db: Session = Depends(get_db),
    user=Depends(require_roles("librarian", "admin")),
) -> BookBase:
    book = db.get(Book, ma)
    if book is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy sách.")
    if body.theLoaiId and db.get(TheLoai, body.theLoaiId) is None:
        raise HTTPException(status_code=422, detail="Thể loại không tồn tại.")
    if body.nxbId and db.get(Nxb, body.nxbId) is None:
        raise HTTPException(status_code=422, detail="NXB không tồn tại.")
    data = body.model_dump()
    data["ma"] = ma
    for field, value in data.items():
        setattr(book, field, value)
    write_audit_log(
        db,
        user,
        "UPDATE_BOOK",
        "BOOK",
        entity_id=ma,
    )
    db.commit()
    db.refresh(book)
    return book


@router.delete("/{ma}")
def delete_book(
    ma: str,
    db: Session = Depends(get_db),
    user=Depends(require_roles("librarian", "admin")),
):
    book = db.get(Book, ma)
    if book is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy sách.")
    write_audit_log(
        db,
        user,
        "DELETE_BOOK",
        "BOOK",
        entity_id=ma,
        details=f"ten={book.ten}",
    )
    db.delete(book)
    db.commit()
    return {"message": "Đã xoá sách."}
