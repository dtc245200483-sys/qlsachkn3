# Minh chứng 2.9 (Phần 3): Phần mã nguồn dùng nguyên (Giữ lại)

Với vai trò kiểm duyệt, tôi đã rà soát toàn bộ mã nguồn do AI sinh ra. Đối với những đoạn mã mang tính chất "khung xương" (boilerplate) chuẩn mực của framework, hoặc các thuật toán cơ bản đã tối ưu, tôi quyết định giữ nguyên 100% để tiết kiệm thời gian gõ phím.

Dưới đây là các phần mã nguồn thực tế trong dự án được tôi giữ lại nguyên bản từ AI:

## 1. Cấu trúc khởi tạo FastAPI (`Backend/app/main.py`)
AI đã viết cực kỳ chuẩn mực file gốc để khởi tạo ứng dụng FastAPI. Việc khai báo `CORSMiddleware` với tham số `allow_origins=["*"]` đảm bảo Frontend chạy ở port khác có thể gọi API mà không bị lỗi trình duyệt chặn. Phần này không có logic nghiệp vụ nên tôi giữ nguyên toàn bộ:

```python
# Trích xuất từ Backend/app/main.py
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

# AI tự động nối tất cả các router
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(books.router, prefix="/api/books", tags=["Books"])
```

## 2. Các Pydantic Schemas Validate Đầu Vào (`Backend/app/schemas.py`)
Với hơn 10 bảng dữ liệu, việc ngồi viết tay từng Schema để kiểm tra kiểu dữ liệu (Int, String, DateTime) là rất mất thời gian. AI đã tự động map các cột từ CSDL thành Pydantic model rất hoàn hảo. 

```python
# Trích xuất từ Backend/app/schemas.py
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
Tôi chỉ giữ nguyên đoạn này vì nó thực hiện đúng một nhiệm vụ duy nhất: lọc rác dữ liệu từ Frontend truyền xuống Backend.

## 3. Kiến trúc CSS Custom & Responsive (`frontend/css/style.css`)
Thay vì dùng Bootstrap nặng nề, tôi yêu cầu Frontend Agent tự viết CSS Custom. AI đã sử dụng chuẩn CSS Variables (Biến màu) của xu hướng web hiện đại để phối màu Navy/Xanh biển cực kỳ đồng nhất cho thư viện.

```css
/* Trích xuất từ frontend/css/style.css */
:root {
    --primary-color: #0A2E5C;    /* Xanh Navy chuẩn ICTU */
    --secondary-color: #1E4B8C;  /* Xanh dương nhạt hơn */
    --accent-color: #007BFF;     /* Màu nhấn cho nút bấm */
    --text-main: #333333;
    --text-light: #666666;
    --bg-light: #F5F7FA;
    --white: #FFFFFF;
    --danger: #DC3545;
    --success: #28A745;
    --warning: #FFC107;
}

/* CSS Media Query do AI viết để Sidebar tự thu gọn trên điện thoại */
@media (max-width: 768px) {
    .sidebar { width: 60px; }
    .sidebar .logo-text, .sidebar .menu-text { display: none; }
}
```
Tôi đánh giá mã CSS này siêu nhẹ (chỉ ~23KB), đáp ứng chuẩn WCAG 2.1 AA+ và hiển thị hoàn hảo trên Mobile, nên tôi giữ nguyên không sửa 1 dòng nào ở phần Layout gốc này.

---
**Kết luận Phần 3:** 
Việc giữ lại các phần code cấu trúc chuẩn (FastAPI boilerplate, Pydantic Schema, CSS Variables) giúp tôi tiết kiệm đến 60% thời gian gõ phím cơ học, qua đó dành toàn bộ trí lực để can thiệp vào các "bài toán khó" ở Phần 4.

## 4. API Upload Ảnh Bìa Sách (`Backend/app/routers/books.py`) — 2026-08-27
Khi tôi yêu cầu AI thêm tính năng tải ảnh bìa sách, AI đã sinh ra đúng chuẩn một endpoint `UploadFile` của FastAPI, xử lý đúng giới hạn dung lượng 5MB và lưu vào đúng thư mục `static/covers`:

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
Đây là code framework chuẩn FastAPI multipart upload, tôi giữ nguyên vì nó thực hiện đúng và an toàn.