# PROMPT 03 - KẾ HOẠCH TRIỂN KHAI

## Vai trò

Bạn là Trưởng nhóm kỹ thuật lập kế hoạch triển khai có thể thực thi.

## Bối cảnh

Thư mục gốc: `D:\ung dung tri tue nhan ao\app`

Đây là bước 3 trong quy trình 6 bước. Không viết source code trong bước này.

## Đầu vào

- `docs/02_design.md`
- `docs/01_requirements.md`
- `00_project.md`

Chỉ tiếp tục nếu bước 2 có `STATUS: PASS`.

## Skill cần áp dụng

Nếu có skill phù hợp, ưu tiên:

- `writing-plans` để chia task;
- `tdd` để gắn test-first path;
- `fastapi-expert` để lập thứ tự migration/API/routers;
- `web-design-guidelines` cho task CSS custom responsive;
- `domain-modeling` cho thứ tự tạo models/relationships.

Ghi mục `Bằng chứng áp dụng skill`.

## Workflow bắt buộc

`INPUT -> CREATE -> REVIEW -> CRITIQUE -> FIX -> VERIFY -> QUALITY GATE -> OUTPUT`

## CREATE

Tạo `docs/03_implementation_plan.md`.

Chia thành các module/task theo thứ tự có thể thực thi:

1. Khởi tạo FastAPI backend và config (`main.py`, `config.py`, `database.py`).
2. Cấu hình SQL Server connection string, Alembic migrations.
3. Tạo models SQLAlchemy (`Users`, `Books`, `Categories`, `Readers`, `BorrowRecords`, `FineHistory`, `Reservations`, `Requests`, `Notifications`, `AuditLog`).
4. Tạo Pydantic schemas (`schemas.py`).
5. Tạo module bảo mật (`security.py`: JWT encode/decode, Bcrypt hashing).
6. Tạo dependency injection (`deps.py`: get_db, get_current_user).
7. Tạo business validation (`validation.py`: kiểm tra giới hạn mượn, sách còn tồn kho).
8. Tạo routers CRUD sách (`routers/books.py`).
9. Tạo routers CRUD độc giả (`routers/readers.py`).
10. Tạo routers mượn/trả/gia hạn/thu phạt (`routers/borrows.py`).
11. Tạo routers đặt trước (`routers/reservations.py`).
12. Tạo routers yêu cầu bổ sung sách (`routers/requests.py`).
13. Tạo routers thông báo (`routers/notifications.py`).
14. Tạo routers thống kê (`routers/stats.py`).
15. Tạo routers hồ sơ (`routers/profile.py`).
16. Tạo routers admin (`routers/accounts.py`, `routers/admin.py`, `routers/catalog.py`).
17. Tạo routers xuất báo cáo (`routers/export.py`).
18. Tạo trang đăng nhập (`frontend/index.html` + `frontend/js/auth.js`).
19. Tạo layout chung (`frontend/js/layout.js`: sidebar động theo role).
20. Tạo CSS custom (`frontend/css/style.css`: responsive, Google Fonts Be Vietnam Pro).
21. Tạo các trang CRUD frontend (books, readers, borrow, reservations, requests, notifications, profile, stats, search, my-borrows, admin-*).
22. Tạo module AI Engine gợi ý sách (`ai_engine/`).
23. Viết tests Backend (pytest + httpx).
24. Viết báo cáo và README.

## Cấu trúc source code dự kiến

Kế hoạch phải mô tả rõ cây thư mục:

```text
backend/
frontend/
ai_engine/
qa/
thuky/
support/
docs/
prompts/
scripts/
```

Và chi tiết các file cần tạo/sửa:

- `backend/app/main.py`: FastAPI app, CORS middleware, include routers.
- `backend/app/config.py`: Settings từ .env (DB_URL, JWT_SECRET, JWT_EXPIRE).
- `backend/app/database.py`: SQLAlchemy engine, SessionLocal.
- `backend/app/models.py`: 10 models SQLAlchemy.
- `backend/app/schemas.py`: Pydantic schemas.
- `backend/app/security.py`: JWT + Bcrypt.
- `backend/app/deps.py`: Dependency injection.
- `backend/app/validation.py`: Business rules.
- `backend/app/routers/*.py`: 13 router files.
- `frontend/index.html`: Login page với CSS custom.
- `frontend/css/style.css`: CSS custom responsive + Google Fonts.
- `frontend/js/api.js`: Wrapper fetch() với JWT header.
- `frontend/js/auth.js`: Login logic + localStorage token.
- `frontend/js/layout.js`: Sidebar/header render theo role.
- `frontend/js/*.js`: Logic riêng cho từng trang HTML.

## Task format bắt buộc

Mỗi task phải có:

- Task ID;
- Requirement ID;
- Design ID;
- mục tiêu;
- dependencies;
- module/phạm vi;
- Agent thực thi (Backend Agent / Frontend Agent / AI Agent / QA Agent);
- files to create/update;
- test cần viết;
- lệnh verification;
- Definition of Done.

Tạo bảng dependency:

`Task ID | Depends on | Reason | Agent | Can run in parallel | Blocking risk`

## Verification bắt buộc trong plan

Mỗi task phải gắn tới ít nhất một lệnh:

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Chạy test
cd backend
pytest tests/ -v

# Smoke test
curl http://127.0.0.1:8000/api/books
curl http://127.0.0.1:8000/api/auth/login -X POST -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin\"}"
```

Smoke test cần có:

- `POST http://127.0.0.1:8000/api/auth/login` trả JSON có `access_token`;
- `GET http://127.0.0.1:8000/api/books` trả JSON mảng sách;
- Mở `frontend/index.html` trong browser, đăng nhập thành công redirect sang `books.html`;
- `frontend/css/style.css` load thành công (không vỡ layout).

## Quality gate

Chỉ `STATUS: PASS` khi:

- task bao phủ toàn bộ requirements;
- task có thứ tự và dependency rõ;
- có task riêng cho CSS custom responsive;
- có task riêng cho JWT authentication;
- có task riêng cho business rules (phạt, giới hạn mượn);
- có test/smoke/verification cụ thể;
- không tạo source code trong bước này.

## OUTPUT

Tạo: `docs/03_implementation_plan.md`

Cuối file:

```text
STATUS: PASS | FAIL
NEXT_INPUT: docs/03_implementation_plan.md
NEXT_PROMPT: prompts/04_implementation.md
TRACEABILITY_MATRIX_UPDATED: YES
```
