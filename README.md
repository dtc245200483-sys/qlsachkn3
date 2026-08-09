# Hệ thống quản lý thư viện có tích hợp AI

Đồ án học phần **Ứng dụng Trí tuệ nhân tạo** (ICTU) — nhóm 02: Phạm Vũ Quang Hưng, Trần Thị Thu Huyền.

## Cấu trúc

- `Frontend/` — web app HTML/CSS/JS thuần (13 trang: đăng nhập, đăng ký, tra cứu, sách, độc giả, mượn/trả, lịch sử, yêu cầu, đặt trước, thông báo, thống kê, tài khoản, danh mục, cấu hình).
- `Backend/` — FastAPI + SQLAlchemy + Alembic + SQL Server (xem `Backend/README.md`, `Backend/api_docs.md`).
- `AI_Engine/` — prompt + code AI (đang triển khai).
- `thuky/` — log tiến độ, minh chứng AI, yêu cầu đồng bộ.
- `hỗ trợ/` — đề bài, kế hoạch, tiêu chí, quy trình vòng lặp, checklist UC.
- `docs/` — SRS, Use Case, ERD, kiến trúc, thiết kế AI.

## Cài đặt & chạy

```powershell
cd "D:\ung dung tri tue nhan ao\app\Backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # điền thông số thật
python -m alembic upgrade head
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Frontend: mở `Frontend/index.html` trong trình duyệt (hoặc dùng Live Server).

## Tài khoản demo

| Vai trò | Username | Password |
|---|---|---|
| Admin | admin | admin1 |
| Thủ thư | librarian | librarian1 |
| Độc giả | reader | reader1 |
| Độc giả (đã liên kết) | docgia1 | docgia1 |

## Dữ liệu mẫu

```powershell
cd "D:\ung dung tri tue nhan ao\app\Backend"
python scripts/seed_demo.py --verify
```

## Tài liệu

- API: `Backend/api_docs.md`
- Đề bài: `hỗ trợ/DE_BAI.md`
- Tiêu chí chấm: `hỗ trợ/TIEU_CHI_DANH_GIA.md`
- Checklist Use Case: `hỗ trợ/CHECKLIST_UC_THUC_HIEN.md`
