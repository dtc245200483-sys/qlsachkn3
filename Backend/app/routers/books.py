import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..config import COVERS_DIR
from ..database import get_db
from ..deps import get_current_user, require_roles
from ..models import Book, BookCopy, BorrowDetail, BorrowSlip, Nxb, TheLoai
from ..schemas import BookBase, CoverUploadOut
from ..audit import write_audit_log

router = APIRouter(prefix="/api/books", tags=["books"])


@router.get("", response_model=list[BookBase])
def list_books(
    q: str | None = Query(None, max_length=255),
    theLoai: str | None = Query(None, max_length=100),
    trangThai: str | None = Query(None, max_length=20),
    sort: str | None = Query(None, max_length=20),
    order: str | None = Query(None, max_length=10),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> list[BookBase]:
    query = db.query(Book)
    if q:
        pattern = f"%{q}%"
        query = query.filter(
            or_(
                Book.ma.like(pattern),
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

    sort_map = {
        "ten": Book.ten,
        "tacGia": Book.tacGia,
        "namXb": Book.namXb,
        "soLuong": Book.soLuong,
    }
    sort_key = sort or "ten"
    if sort_key not in sort_map:
        raise HTTPException(
            status_code=422,
            detail="sort chỉ nhận ten, tacGia, namXb hoặc soLuong.",
        )
    order_key = (order or "asc").lower()
    if order_key not in ("asc", "desc"):
        raise HTTPException(status_code=422, detail="order chỉ nhận asc hoặc desc.")

    column = sort_map[sort_key]
    if order_key == "desc":
        query = query.order_by(column.desc(), Book.ma.asc())
    else:
        query = query.order_by(column.asc(), Book.ma.asc())
    return query.all()


@router.post("/upload-cover", response_model=CoverUploadOut)
async def upload_cover(
    file: UploadFile = File(...),
    user=Depends(require_roles("librarian", "admin")),
) -> CoverUploadOut:
    ext = ".jpg"
    if file.content_type == "image/png":
        ext = ".png"
    elif file.content_type == "image/jpeg":
        ext = ".jpg"
    elif file.content_type == "image/webp":
        ext = ".webp"
    else:
        raise HTTPException(status_code=400, detail="Chỉ chấp nhận ảnh JPG, PNG hoặc WEBP.")
    
    data = await file.read()
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Ảnh bìa tối đa 5MB.")

    os.makedirs(COVERS_DIR, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(COVERS_DIR, filename)
    with open(path, "wb") as f:
        f.write(data)

    return CoverUploadOut(url=f"/static/covers/{filename}")


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
    
    # Generate BookCopy items
    the_loai = book.theLoaiId.replace("TL_", "") if book.theLoaiId else "UNCAT"
    rand_id = uuid.uuid4().hex[:6].upper()
    for i in range(1, book.soLuong + 1):
        copy = BookCopy(
            copy_id=f"{the_loai}-{rand_id}-{i}",
            book_id=book.ma
        )
        db.add(copy)
        
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
    old_qty = book.soLuong

    for field, value in data.items():
        setattr(book, field, value)
        
    if book.soLuong > old_qty:
        existing_copies = db.query(BookCopy).filter(BookCopy.book_id == ma).all()
        diff = book.soLuong - len(existing_copies)
        if diff > 0:
            max_idx = 0
            for c in existing_copies:
                try:
                    idx = int(c.copy_id.split("-")[-1])
                    if idx >= max_idx:
                        max_idx = idx
                except:
                    pass
            max_idx += 1
            
            the_loai = book.theLoaiId.replace("TL_", "") if book.theLoaiId else "UNCAT"
            rand_id = None
            if existing_copies:
                parts = existing_copies[0].copy_id.split("-")
                if len(parts) >= 3:
                    rand_id = parts[-2]
            if not rand_id:
                rand_id = uuid.uuid4().hex[:6].upper()
                
            for i in range(max_idx, max_idx + diff):
                copy = BookCopy(
                    copy_id=f"{the_loai}-{rand_id}-{i}",
                    book_id=ma,
                    status="Có sẵn"
                )
                db.add(copy)

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
