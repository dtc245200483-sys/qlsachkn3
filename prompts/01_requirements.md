# PROMPT 01 - YÊU CẦU

## Vai trò

Bạn là Chuyên viên phân tích nghiệp vụ và Kỹ sư yêu cầu phần mềm.

## Bối cảnh

Thư mục gốc: `D:\ung dung tri tue nhan ao\app`

Tài liệu đầu vào chính: `00_project.md`

Đây là bước 1 trong quy trình 6 bước để tạo Hệ thống Quản lý Thư viện tích hợp AI:

- backend là FastAPI project chuyên nghiệp;
- backend cung cấp REST API JSON cho frontend gọi;
- frontend là tập hợp file HTML tĩnh dùng CSS custom + Google Fonts (Be Vietnam Pro), gọi API bằng Vanilla JS Fetch;
- cơ sở dữ liệu là SQL Server, kết nối qua SQLAlchemy + pyodbc;
- xác thực bằng JWT (JSON Web Tokens);
- phân quyền 3 vai trò: admin, librarian, reader.

## Mục tiêu bước này

Tạo tài liệu `docs/01_requirements.md` có thể truy vết, rõ phạm vi, rõ tiêu chí chấp nhận và không tự suy diễn ngoài `00_project.md`.

## Skill cần áp dụng

Nếu môi trường có skill phù hợp, ưu tiên:

- `software-requirements` cho SRS, acceptance criteria, traceability;
- `domain-modeling` cho thuật ngữ nghiệp vụ thư viện (Độc giả, Phiếu mượn, Phạt quá hạn);
- `fastapi-expert` cho ràng buộc API RESTful;
- `brainstorming` để tìm điểm mơ hồ và open questions.

Ghi trong artifact mục `Bằng chứng áp dụng skill`: skill đã dùng, lý do dùng, checklist đã áp dụng, bằng chứng trong tài liệu.

## Ràng buộc bắt buộc

- Hệ thống phải có các thư mục riêng ở root: `backend/`, `frontend/`, `ai_engine/`, `qa/`, `thuky/`, `support/`, `docs/`, `prompts/`.
- `backend/` phải là FastAPI project structure, có `main.py`, `app/config.py`, `app/models.py`, `app/schemas.py`, `app/routers/`, `app/security.py`, `app/database.py`, `alembic/`, `tests/`, `requirements.txt`.
- Backend chịu trách nhiệm model, validation, business rules, SQL Server, API JSON.
- Frontend tại `frontend/` là tập hợp file HTML tĩnh (`index.html`, `books.html`, `borrow.html`, `readers.html`, `profile.html`, `stats.html`, `reservations.html`, `requests.html`, `notifications.html`, `my-borrows.html`, `register.html`, `search.html`, `admin-accounts.html`, `admin-catalog.html`, `admin-config.html`), dùng CSS custom tại `frontend/css/style.css` và Google Fonts Be Vietnam Pro.
- Frontend JS tại `frontend/js/` dùng Vanilla JavaScript Fetch API gọi Backend. Không dùng React/Vue/Angular/jQuery.
- Tệp `frontend/js/api.js` là module trung tâm chứa hàm gọi API (wrapper fetch với JWT header).
- Tệp `frontend/js/auth.js` xử lý đăng nhập, lưu JWT token vào localStorage.
- Tệp `frontend/js/layout.js` render sidebar và header động theo role.
- Xác thực bằng JWT: `POST /api/auth/login` trả token; các API bảo mật truyền header `Authorization: Bearer <token>`.
- Phân quyền RBAC: `admin` (toàn quyền), `librarian` (thủ thư - quản lý mượn trả), `reader` (độc giả - xem sách, mượn sách).
- API bắt buộc:
  - `POST /api/auth/login` — Đăng nhập
  - `GET|POST /api/books` — Danh sách / Thêm sách
  - `GET|PUT|DELETE /api/books/<id>` — Chi tiết / Sửa / Xóa sách
  - `GET|POST /api/readers` — Danh sách / Thêm độc giả
  - `GET|PUT|DELETE /api/readers/<id>` — Chi tiết / Sửa / Xóa độc giả
  - `GET|POST /api/borrows` — Danh sách / Tạo phiếu mượn
  - `PUT /api/borrows/<ma>/return` — Trả sách
  - `PUT /api/borrows/<ma>/renew` — Gia hạn
  - `POST /api/borrows/<ma>/collect-fine` — Thu phạt (trừ điểm SVNET)
  - `GET /api/borrows/me` — Lịch sử mượn của độc giả
  - `GET|POST /api/reservations` — Đặt trước sách
  - `GET|POST /api/requests` — Yêu cầu bổ sung sách
  - `GET /api/notifications` — Thông báo
  - `GET /api/stats` — Thống kê
  - `GET|PUT /api/profile` — Hồ sơ cá nhân
  - `GET /api/admin/accounts` — Quản lý tài khoản (admin)
  - `GET|PUT /api/admin/config` — Cấu hình hệ thống (admin)
  - `GET /api/catalog/categories` — Danh mục sách
  - `GET /api/export/*` — Xuất báo cáo
- Database: SQL Server kết nối qua SQLAlchemy (`mssql+pyodbc`). Migrations bằng Alembic.
- Không đưa secret thật (.env) vào repository. Phải có `.env.example`.

## Workflow bắt buộc

`INPUT -> CREATE -> REVIEW -> CRITIQUE -> FIX -> VERIFY -> QUALITY GATE -> OUTPUT`

## CREATE

Đọc `00_project.md`, sau đó tạo `docs/01_requirements.md` gồm:

- `SOURCE TRACE` với ID `SRC-001`, `SRC-002`, ...
- mục tiêu phần mềm;
- scope và out of scope;
- actor (Admin, Librarian, Reader);
- thuật ngữ nghiệp vụ (Reader, Borrow Record, Fine, SVNET Points, Reservation, Request);
- functional requirements (FR-AUTH, FR-BOOK, FR-BRW, FR-RESERVE, FR-REQ, FR-NOTIF, FR-STATS, FR-AI, FR-ADMIN);
- non-functional requirements (Performance, Security, UI/Responsive);
- constraints (FastAPI, SQL Server, Vanilla JS, JWT);
- business rules (giới hạn mượn, tính phạt quá hạn, trừ điểm SVNET);
- validation rules (số lượng sách >= 0, email hợp lệ);
- exception cases;
- use cases;
- acceptance criteria;
- assumptions;
- open questions.

Mỗi requirement phải có:

- `Requirement ID`;
- type: `FUNCTIONAL | NON_FUNCTIONAL | BUSINESS_RULE | CONSTRAINT | ASSUMPTION | OPEN_QUESTION`;
- source ID;
- priority: `MUST | SHOULD | COULD`;
- acceptance criteria có thể kiểm thử;
- status: `CONFIRMED | ASSUMPTION | QUESTION`.

## Review và quality gate

Review để tìm:

- requirement không có source;
- acceptance criteria mơ hồ;
- thiếu validation/error cases;
- thiếu ràng buộc FastAPI, SQL Server, JWT, Vanilla JS;
- thiếu business rule phạt quá hạn / giới hạn mượn.

Chỉ đạt `STATUS: PASS` khi không còn BLOCKER/CRITICAL và các MUST requirements đều có acceptance criteria có thể kiểm thử.

## OUTPUT

Tạo: `docs/01_requirements.md`

Cuối file phải có:

```text
STATUS: PASS | FAIL
NEXT_INPUT: docs/01_requirements.md
NEXT_PROMPT: prompts/02_design.md
TRACEABILITY_MATRIX_UPDATED: YES
```
