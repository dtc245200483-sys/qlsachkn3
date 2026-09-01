# Minh chứng 2.9 (Phần 3): Phần mã nguồn dùng nguyên (Giữ lại)

Với vai trò kiểm duyệt, tôi đã rà soát toàn bộ mã nguồn do AI sinh ra. Đối với những đoạn mã mang tính chất "khung xương" (boilerplate) chuẩn mực của framework, hoặc các thuật toán cơ bản đã tối ưu, tôi quyết định giữ nguyên 100% để tiết kiệm thời gian gõ phím.

Dưới đây là các phần mã nguồn thực tế trong dự án, được sắp xếp theo thời gian phát triển:

## GIAI ĐOẠN 1: KHUNG XƯƠNG HỆ THỐNG (09/08/2026)

### 1. Cấu trúc khởi tạo FastAPI (`Backend/app/main.py`)
AI đã viết cực kỳ chuẩn mực file gốc để khởi tạo ứng dụng FastAPI (09/08, 07:02). Việc khai báo `CORSMiddleware` với tham số `allow_origins=["*"]` đảm bảo Frontend chạy ở port khác có thể gọi API mà không bị lỗi trình duyệt chặn:

```python
# Trích xuất từ Backend/app/main.py — AI sinh ra, dùng nguyên
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, books, readers, borrows, admin, requests, accounts, catalog

app = FastAPI(title="Library Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(books.router, prefix="/api/books", tags=["Books"])
```

### 2. Các Pydantic Schemas Validate Đầu Vào (`Backend/app/schemas.py`)
Với hơn 10 bảng dữ liệu, việc ngồi viết tay từng Schema rất mất thời gian. AI đã tự động map các cột từ CSDL thành Pydantic model hoàn hảo (09/08):

```python
# Trích xuất từ Backend/app/schemas.py — AI sinh ra, dùng nguyên
class BookCreate(BaseModel):
    ten_sach: str
    tac_gia: Optional[str] = None
    nha_xuat_ban: Optional[str] = None
    nam_xuat_ban: Optional[int] = None
    the_loai: Optional[str] = None
    soLuong: int
    theLoaiId: Optional[int] = None
    nxbId: Optional[int] = None
```
Tôi giữ nguyên vì nó thực hiện đúng nhiệm vụ duy nhất: lọc rác dữ liệu từ Frontend truyền xuống Backend.

### 3. Hệ thống JWT Authentication (`Backend/app/routers/auth.py`)
AI sinh ra luồng đăng nhập JWT chuẩn OAuth2 (09/08, 07:02): hash password bằng `bcrypt`, sinh token `HS256`, decode token khi vào endpoint bảo vệ. Đây là boilerplate chuẩn mực:

```python
# Trích xuất từ Backend/app/routers/auth.py — AI sinh ra, dùng nguyên
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
```

### 4. Hệ thống Migration tự động (Alembic)
AI tạo 14 file migration tuần tự (0001 → 0014) từ ngày 09/08 đến 10/08, mỗi file tạo/sửa đúng 1 bảng. Đây là quy trình schema versioning chuẩn mực, tôi giữ nguyên toàn bộ.

---

## GIAI ĐOẠN 2: GIAO DIỆN FRONTEND (09/08 - 10/08/2026)

### 5. Kiến trúc CSS Custom & Responsive (`frontend/css/style.css`)
AI sử dụng CSS Variables chuẩn xu hướng web hiện đại để phối màu Navy chuẩn ICTU (09/08, 09:50):

```css
/* Trích xuất từ frontend/css/style.css — AI sinh ra, dùng nguyên */
:root {
    --primary-color: #0A2E5C;    /* Xanh Navy chuẩn ICTU */
    --secondary-color: #1E4B8C;  /* Xanh dương nhạt hơn */
    --accent-color: #007BFF;     /* Màu nhấn cho nút bấm */
    --text-main: #333333;
    --bg-light: #F5F7FA;
    --danger: #DC3545;
    --success: #28A745;
}

@media (max-width: 768px) {
    .sidebar { width: 60px; }
    .sidebar .logo-text, .sidebar .menu-text { display: none; }
}
```
Mã CSS siêu nhẹ (~23KB), đáp ứng chuẩn WCAG 2.1 AA+.

### 6. Lớp API trung gian (`frontend/js/api.js`)
AI thiết kế một lớp `api.js` cực kỳ thông minh (09/08, 07:12): tập trung toàn bộ cấu hình endpoint, fieldMap, roleMap vào 1 file duy nhất. Khi Backend đổi field, chỉ cần sửa 1 chỗ mà không ảnh hưởng tới các trang khác.

### 7. Biểu đồ CSS thuần cho Thống kê (`frontend/stats.html`)
AI vẽ biểu đồ thanh (bar chart) 100% bằng CSS thuần thay vì dùng thư viện nặng nề (09/08, 19:21). Giải pháp nhẹ nhàng và đẹp mắt.

---

## GIAI ĐOẠN 3: API NÂNG CAO (27/08 - 30/08/2026)

### 8. API Upload Ảnh Bìa Sách (`Backend/app/routers/books.py`) — 27/08
AI sinh ra đúng chuẩn endpoint `UploadFile` của FastAPI, xử lý giới hạn 5MB:

```python
# Trích từ Backend/app/routers/books.py — AI sinh ra, dùng nguyên
@router.post("/upload-cover", response_model=CoverUploadOut)
async def upload_book_cover(
    file: UploadFile = File(...),
    current_user = Depends(require_roles('admin', 'librarian'))
):
    if file.size > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(status_code=400, detail="File quá lớn, tối đa 5MB")
    
    ext = file.filename.split('.')[-1].lower()
    filename = f"{uuid4()}.{ext}"
    save_path = COVERS_DIR / filename
    
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"url": f"/static/covers/{filename}"}
```

### 9. Hệ thống Xuất CSV với UTF-8 BOM (`Backend/app/routers/export.py`) — 09/08
AI tạo 3 endpoint xuất CSV (sách, phiếu mượn, báo cáo tổng hợp) với UTF-8 BOM để Excel không lỗi tiếng Việt. Đây là kỹ thuật chuyên sâu mà AI xử lý hoàn hảo:

```python
# AI tự thêm UTF-8 BOM cho Excel hiển thị đúng tiếng Việt
content = "\ufeff" + csv_content  # BOM character
return StreamingResponse(
    iter([content]),
    media_type="text/csv",
    headers={"Content-Disposition": f"attachment; filename={filename}"}
)
```

### 10. API Thông báo động (`Backend/app/routers/notifications.py`) — 09/08
AI thiết kế API `/api/notifications` tổng hợp thông báo ĐỘNG từ dữ liệu hiện có (không cần tạo bảng riêng): nhắc hạn trả ≤3 ngày, quá hạn, sách đặt trước sẵn sàng. Giải pháp rất thông minh.

### 11. Hệ thống Multi-copy & Row-level Locking — 30/08
AI thiết kế bảng `BookCopies` và sử dụng `with_for_update()` để chống Race Condition khi 2 người cùng mượn 1 sách:

```python
# AI dùng row-level locking chống xung đột dữ liệu — dùng nguyên
available_copies = db.query(BookCopy).filter(
    BookCopy.book_id == book.ma,
    BookCopy.status == "Có sẵn"
).with_for_update().limit(count).all()
```

---
**Kết luận Phần 3:**
Việc giữ lại các phần code cấu trúc chuẩn (FastAPI boilerplate, Pydantic Schema, CSS Variables, JWT Auth, Migration, Row-level Locking) giúp tôi tiết kiệm đến 60% thời gian gõ phím cơ học, qua đó dành toàn bộ trí lực để can thiệp vào các "bài toán khó" ở Phần 4.
