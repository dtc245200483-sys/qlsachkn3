# PROMPT 05 - RÀ SOÁT MÃ NGUỒN VÀ KIỂM THỬ

## Vai trò

Bạn là Code Reviewer và QA Engineer độc lập.

## Bối cảnh

Thư mục gốc: `D:\ung dung tri tue nhan ao\app`

Đây là bước 5 trong quy trình 6 bước.

## Đầu vào

- source code và tests từ bước 4;
- `docs/04_implementation_report.md`;
- `docs/03_implementation_plan.md`;
- `docs/02_design.md`;
- `docs/01_requirements.md`;
- `00_project.md`.

Chỉ tiếp tục nếu bước 4 có `STATUS: PASS`.

## Skill cần áp dụng

Nếu có skill phù hợp, ưu tiên:

- `code-review` cho findings;
- `qa` cho test matrix;
- `fastapi-expert` cho kiểm tra API contract;
- `webapp-testing` cho browser smoke;
- `diagnosing-bugs` nếu test fail;
- `verification-before-completion` cho final gate.

Ghi mục `Bằng chứng áp dụng skill`.

## Workflow bắt buộc

`INPUT -> CODE REVIEW -> TEST PLAN -> RUN TESTS -> CRITIQUE -> FIX LOG -> RETEST -> REGRESSION -> VERIFY -> QUALITY GATE -> OUTPUT`

## Code review checklist

Review các điểm sau:

- FastAPI project structure đúng chuẩn trong `backend/`;
- `backend/app/main.py` khởi tạo app, include routers, cấu hình CORS;
- `backend/app/routers/auth.py` xử lý login, trả JWT token;
- Tất cả API CRUD đúng contract theo `api_docs.md`;
- Business rules và validation đúng (giới hạn mượn 5 quyển, sách tồn kho >= 0, phạt quá hạn);
- SQL Server connection string đọc từ `.env`;
- Alembic migrations khớp với `models.py`;
- `frontend/css/style.css` là CSS custom duy nhất, không có Bootstrap/Tailwind;
- Google Fonts Be Vietnam Pro được nhúng qua CDN link trong HTML head;
- `frontend/js/api.js` gắn JWT header cho mọi request;
- `frontend/js/auth.js` lưu token vào localStorage, redirect khi hết hạn;
- `frontend/js/layout.js` render sidebar/header đúng role;
- JS escape dữ liệu người dùng trước khi chèn vào table;
- Không có secret thật trong repository;
- Tests bao phủ: auth, books, readers, borrows, fines, reservations, notifications, profile, stats, export.

Issue format:

`Severity | File | Line | Evidence | Problem | Impact | Recommendation`

Severity:

`BLOCKER | CRITICAL | MAJOR | MINOR | SUGGESTION`

## Test plan bắt buộc

Chạy:

```powershell
cd backend
pytest tests/ -v --tb=short
```

Nếu cần smoke app:

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Smoke checks:

- `POST /api/auth/login` trả `access_token` (200);
- `GET /api/books` trả mảng JSON (200);
- `POST /api/borrows` với sách có `soLuongKhaDung > 0` → 201;
- `POST /api/borrows` với sách `soLuongKhaDung = 0` → 400 `"Hết sách"`;
- `PUT /api/borrows/{ma}/return` → 200, `soLuongKhaDung` tăng 1;
- `POST /api/borrows/{ma}/collect-fine` bởi `librarian` → 200, `diem_svnet` giảm;
- `POST /api/borrows/{ma}/collect-fine` bởi `reader` → 403;
- Mở `frontend/index.html` trong browser, đăng nhập thành công;
- Layout responsive: resize browser xuống 360px, sidebar không vỡ;
- Click sidebar menu, chuyển trang đúng.

Coverage table bắt buộc:

`Requirement ID | Acceptance Criterion | Test ID | Test type | Evidence | Result`

## Fix và retest

Nếu sửa code trong bước này, ghi:

- issue ID;
- file sửa;
- root cause;
- fix summary;
- retest command;
- retest result;
- regression result.

Không được `PASS` nếu có fix mà chưa retest.

## Quality gate

Chỉ `STATUS: PASS` khi:

- không còn BLOCKER/CRITICAL;
- MAJOR hợp lệ đã sửa hoặc có lý do chấp nhận;
- pytest tests pass;
- CSS custom responsive được xác minh;
- JWT authentication flow hoạt động;
- Business rules (phạt, giới hạn mượn) hoạt động đúng;
- smoke endpoints pass hoặc ghi rõ lý do không chạy được.

## OUTPUT

Tạo: `docs/05_review_testing.md`

Cuối file:

```text
STATUS: PASS | FAIL
NEXT_INPUT: reviewed and tested source code, docs/05_review_testing.md
NEXT_PROMPT: prompts/06_final_delivery.md
TRACEABILITY_MATRIX_UPDATED: YES
```
