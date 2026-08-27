# PROMPT 06 - BÀN GIAO CUỐI

## Vai trò

Bạn là người phụ trách final verification và bàn giao.

## Bối cảnh

Thư mục gốc: `D:\ung dung tri tue nhan ao\app`

Đây là bước 6 trong quy trình 6 bước.

## Đầu vào

- `docs/01_requirements.md`
- `docs/02_design.md`
- `docs/03_implementation_plan.md`
- `docs/04_implementation_report.md`
- `docs/05_review_testing.md`
- source code và tests;
- `00_project.md`.

Chỉ tiếp tục nếu bước 5 có `STATUS: PASS`.

## Skill cần áp dụng

Nếu có skill phù hợp, ưu tiên:

- `verification-before-completion` cho final gate;
- `finishing-a-development-branch` cho repo cleanliness;
- `code-review` và `qa` để đối chiếu kết quả;
- `webapp-testing` cho smoke web app.

Ghi mục `Bằng chứng áp dụng skill` trong `docs/06_final_review.md` và `FINAL_REPORT.md`.

## Workflow bắt buộc

`INPUT -> FINAL REVIEW -> CRITIQUE -> FIX OR BACKTRACK -> RE-VERIFY -> QUALITY GATE -> FINAL OUTPUT`

## Final checklist

Kiểm tra:

- 5 bước trước đều `STATUS: PASS`;
- requirements trace được tới design, code, test;
- backend là FastAPI trong `backend/`;
- 13 router files trong `backend/app/routers/`;
- `backend/app/models.py` có 10 SQLAlchemy models;
- `backend/app/security.py` có JWT + Bcrypt;
- API CRUD chạy đúng theo `api_docs.md`;
- frontend là HTML tĩnh trong `frontend/`;
- frontend dùng CSS custom (`css/style.css`) + Google Fonts Be Vietnam Pro;
- frontend JS dùng Vanilla Fetch API qua `js/api.js`;
- frontend layout responsive (sidebar thu gọn trên mobile);
- SQL Server đúng connection string từ `.env`;
- Alembic migrations khớp với models;
- tests pass (pytest);
- README có hướng dẫn chạy đúng;
- không có secret thật;
- không có file tạm/cache/log/build artifact thừa trong bàn giao (`__pycache__`, `.pytest_cache`);
- Thư mục không có ký tự tiếng Việt có dấu (đã đổi `hỗ trợ` → `support`).

## Verification bắt buộc

Chạy hoặc đối chiếu bằng chứng đã chạy:

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
pytest tests/ -v --tb=short
```

Smoke:

- Login: `POST /api/auth/login` trả `access_token`;
- Books: `GET /api/books` trả mảng JSON;
- Borrow: `POST /api/borrows` tạo phiếu;
- Return: `PUT /api/borrows/{ma}/return`;
- Fine: `POST /api/borrows/{ma}/collect-fine`;
- Frontend: mở `frontend/index.html`, đăng nhập thành công;
- CSS: `frontend/css/style.css` load (không vỡ layout);
- Responsive: resize 360px, sidebar thu gọn.

## Quality gate

Đạt:

```text
STATUS: PASS
PROJECT_STATUS: READY
```

chỉ khi:

- verification pass;
- no BLOCKER/CRITICAL;
- app run được;
- CSS custom responsive được xác minh;
- JWT authentication hoạt động;
- Business rules hoạt động (phạt, giới hạn mượn);
- tài liệu bàn giao đủ để người khác chạy lại.

Nếu không, đặt:

```text
STATUS: FAIL
PROJECT_STATUS: NOT_READY
```

và ghi rõ lý do.

## OUTPUT

Tạo hoặc cập nhật:

- `docs/06_final_review.md`
- `FINAL_REPORT.md`
- `README.md` nếu hướng dẫn chạy chưa đúng

`FINAL_REPORT.md` phải có:

- tóm tắt dự án;
- công nghệ sử dụng: FastAPI, SQL Server, SQLAlchemy, Alembic, JWT, Bcrypt, Vanilla HTML/CSS/JS, Google Fonts Be Vietnam Pro;
- kiến trúc Multi-Agent (Backend Agent, Frontend Agent, Thư ký Agent, QA Agent, AI Agent, Trợ lý Agent);
- tính năng đã triển khai (15 trang HTML, 13 routers, 10 models);
- database/API summary;
- hướng dẫn install/run/test;
- kết quả review;
- kết quả test;
- known issues;
- bằng chứng verification.

Cuối file:

```text
STATUS: PASS | FAIL
PROJECT_STATUS: READY | NOT_READY
NEXT_PROMPT: NONE
```
