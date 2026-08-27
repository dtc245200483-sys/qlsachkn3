# PROMPT 04 - TRIỂN KHAI

## Vai trò

Bạn là Kỹ sư phần mềm cao cấp triển khai ứng dụng theo plan.

## Bối cảnh

Thư mục gốc: `D:\ung dung tri tue nhan ao\app`

Đây là bước 4 trong quy trình 6 bước.

## Đầu vào

- `docs/03_implementation_plan.md`
- `docs/02_design.md`
- `docs/01_requirements.md`
- `00_project.md`

Chỉ tiếp tục nếu bước 3 có `STATUS: PASS`.

## Skill cần áp dụng

Nếu có skill phù hợp, ưu tiên:

- `tdd` cho test-first;
- `fastapi-expert` cho FastAPI models/routers/schemas/deps;
- `database-design` cho SQLAlchemy models và Alembic migrations;
- `web-design-guidelines` cho CSS custom responsive;
- `diagnosing-bugs` khi lệnh fail;
- `verification-before-completion` trước khi báo xong.

Ghi mục `Bằng chứng áp dụng skill` trong report.

## Workflow bắt buộc

Với từng task:

`REQUIREMENT -> TEST FIRST -> RED -> IMPLEMENT -> GREEN -> REFACTOR -> REVIEW -> VERIFY`

Không sinh toàn bộ ứng dụng trong một lần nếu chưa có verification.

## Quy tắc triển khai bắt buộc

### Backend FastAPI + SQL Server

- Tạo FastAPI app trong `backend/app/main.py`.
- Cấu hình CORS middleware cho phép frontend cross-origin.
- Kết nối SQL Server qua SQLAlchemy (`mssql+pyodbc://...`) trong `backend/app/database.py`.
- Connection string đọc từ `.env` qua `backend/app/config.py`.
- Tạo 10 models SQLAlchemy trong `backend/app/models.py`: `Users`, `Books`, `Categories`, `Readers`, `BorrowRecords`, `FineHistory`, `Reservations`, `Requests`, `Notifications`, `AuditLog`.
- Tạo Pydantic schemas trong `backend/app/schemas.py`.
- JWT: `backend/app/security.py` dùng `python-jose` + `passlib[bcrypt]`.
- Dependency injection: `backend/app/deps.py` cung cấp `get_db()` và `get_current_user()`.
- Business validation: `backend/app/validation.py` kiểm tra giới hạn mượn (5 quyển), sách tồn kho, quá hạn.
- Tạo 13 router files trong `backend/app/routers/`: `auth.py`, `books.py`, `readers.py`, `borrows.py`, `reservations.py`, `requests.py`, `notifications.py`, `stats.py`, `profile.py`, `accounts.py`, `admin.py`, `catalog.py`, `export.py`.
- Migrations bằng Alembic.
- Không biến backend thành một script HTTP tự viết.

### Frontend CSS custom + Vanilla JS

- `frontend/css/style.css` là file CSS duy nhất, tự viết layout responsive.
- Google Fonts Be Vietnam Pro (wght 400–800) nhúng qua CDN link.
- **Tuyệt đối không dùng Bootstrap, Tailwind, React, Vue, Angular, jQuery.**
- `frontend/js/api.js` là module trung tâm: mọi hàm fetch đều qua đây, tự động gắn `Authorization: Bearer <token>` header.
- `frontend/js/auth.js` xử lý login form, lưu `access_token` + `role` vào `localStorage`.
- `frontend/js/layout.js` render sidebar và header động theo role từ `localStorage`.
- Mỗi trang HTML có file `.js` riêng tại `frontend/js/` xử lý logic CRUD/hiển thị.
- Escape dữ liệu người dùng trước khi chèn vào HTML table (tránh XSS).
- Layout responsive: sidebar thu gọn trên mobile.

### AI Engine

- `ai_engine/` chứa module Python gợi ý sách.
- Nhận đầu vào lịch sử mượn của reader, trả về danh sách mã sách gợi ý.

### Tests

Bắt buộc có/cập nhật tests (pytest + httpx TestClient):

- `tests/test_books_search.py`: Tìm kiếm sách theo tên/tác giả.
- `tests/test_books_sort.py`: Sắp xếp danh sách sách.
- `tests/test_borrows.py`: Luồng mượn/trả đầy đủ.
- `tests/test_fines.py`: Phạt quá hạn và thu phạt.
- `tests/test_readers.py`: CRUD độc giả.
- `tests/test_reservations.py`: Đặt trước sách.
- `tests/test_notifications.py`: Thông báo.
- `tests/test_profile.py`: Hồ sơ cá nhân.
- `tests/test_stats.py`: Thống kê.
- `tests/test_export.py`: Xuất báo cáo.
- `tests/test_uc_compat.py`: Kiểm tra tương thích Use Case.

## Verification bắt buộc

Chạy thật:

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Chạy test:

```powershell
cd backend
pytest tests/ -v --tb=short
```

Smoke test:

- `POST /api/auth/login` trả `access_token`;
- `GET /api/books` trả mảng JSON;
- `POST /api/borrows` tạo phiếu mượn thành công;
- `PUT /api/borrows/{ma}/return` trả sách thành công;
- Mở `frontend/index.html` trong browser, đăng nhập thành công;
- `frontend/css/style.css` load thành công (layout không vỡ);
- Sidebar hiển thị đúng menu theo role.

## SELF-REVIEW

Review code để tìm:

- sai requirement;
- API endpoint URL không khớp với `api_docs.md`;
- frontend CSS vỡ layout trên mobile;
- frontend gọi sai URL API;
- JWT token hết hạn không redirect về login;
- validation thiếu (giới hạn mượn, sách hết tồn kho);
- XSS khi render bảng bằng JS;
- SQL Server connection string sai;
- tests thiếu.

## OUTPUT

Cập nhật source code và tests.

Tạo: `docs/04_implementation_report.md`

Report phải có bảng:

`Task ID | Requirement ID | Design ID | Files changed | Tests added | Verification commands | Result | Notes`

Cuối file:

```text
STATUS: PASS | FAIL
NEXT_INPUT: source code, tests, docs/04_implementation_report.md
NEXT_PROMPT: prompts/05_review_testing.md
TRACEABILITY_MATRIX_UPDATED: YES
```
