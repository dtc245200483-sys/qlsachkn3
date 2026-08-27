# PROMPT 02 - THIẾT KẾ HỆ THỐNG

## Vai trò

Bạn là Kiến trúc sư phần mềm, FastAPI engineer và UI/UX designer.

## Bối cảnh

Thư mục gốc: `D:\ung dung tri tue nhan ao\app`

Đây là bước 2 trong quy trình 6 bước. Không viết source code trong bước này.

## Đầu vào

- `docs/01_requirements.md`
- `00_project.md`

Chỉ tiếp tục nếu `docs/01_requirements.md` kết thúc bằng `STATUS: PASS`.

## Mục tiêu thiết kế

Thiết kế ứng dụng đúng với kiến trúc hiện tại:

- Backend là FastAPI project chuyên nghiệp, cung cấp REST API JSON;
- Frontend là tập hợp file HTML tĩnh gọi API bằng Vanilla JS Fetch;
- Frontend dùng CSS custom (`css/style.css`) + Google Fonts (Be Vietnam Pro), không dùng Bootstrap;
- Database là SQL Server, kết nối qua SQLAlchemy + pyodbc;
- Xác thực JWT, phân quyền RBAC 3 vai trò;
- AI Engine là module Python độc lập gợi ý sách.

## Skill cần áp dụng

Nếu có skill phù hợp, ưu tiên:

- `software-architecture` cho kiến trúc 3 tầng (Frontend → FastAPI → SQL Server);
- `database-design` cho SQL Server schema (Tables, PK, FK, Indexes, Constraints);
- `fastapi-expert` cho FastAPI project structure, dependency injection, Pydantic schemas;
- `domain-modeling` cho entity/state/rule nghiệp vụ thư viện;
- `web-design-guidelines` cho CSS custom responsive design.

Ghi mục `Bằng chứng áp dụng skill` trong `docs/02_design.md`.

## Workflow bắt buộc

`INPUT -> CREATE -> REVIEW -> CRITIQUE -> FIX -> VERIFY -> QUALITY GATE -> OUTPUT`

## CREATE

Tạo `docs/02_design.md` gồm các phần sau.

### Architecture

Mô tả rõ:

- root project có `backend/`, `frontend/`, `ai_engine/`, `qa/`, `thuky/`, `support/`, `docs/`, `prompts/`, `scripts/`;
- `backend/` là FastAPI project cung cấp REST API JSON;
- `frontend/` là tập hợp HTML tĩnh gọi API qua Fetch;
- frontend và backend tách rời hoàn toàn, giao tiếp qua HTTP REST;
- luồng chạy: Browser → `frontend/*.html` → `frontend/js/*.js` → Fetch API → `backend/app/routers/*.py` → services/validation → SQLAlchemy ORM → SQL Server.

### Backend structure

Thiết kế cấu trúc chuẩn FastAPI:

```text
backend/
  .env
  .env.example
  alembic.ini
  requirements.txt
  requirements-dev.txt
  reset_db.py
  api_docs.md
  AGENTS.md
  alembic/
    env.py
    script.py.mako
    versions/
  app/
    __init__.py
    main.py          # FastAPI app, CORS, include routers
    config.py         # Settings from .env
    database.py       # SQLAlchemy engine + SessionLocal
    models.py         # SQLAlchemy models (Users, Books, Categories, BorrowRecords, FineHistory, Reservations, Requests, Notifications, AuditLog)
    schemas.py        # Pydantic schemas (request/response)
    security.py       # JWT encode/decode, password hashing (Bcrypt)
    deps.py           # Dependency injection (get_db, get_current_user)
    audit.py          # Audit logging helper
    validation.py     # Business rule validation
    routers/
      __init__.py
      auth.py         # POST /api/auth/login
      books.py        # GET|POST /api/books, GET|PUT|DELETE /api/books/<id>
      readers.py      # GET|POST /api/readers, GET|PUT|DELETE /api/readers/<id>
      borrows.py      # GET|POST /api/borrows, PUT return/renew, POST collect-fine
      reservations.py # GET|POST /api/reservations
      requests.py     # GET|POST /api/requests
      notifications.py# GET /api/notifications
      stats.py        # GET /api/stats
      profile.py      # GET|PUT /api/profile
      accounts.py     # GET /api/admin/accounts
      admin.py        # GET|PUT /api/admin/config
      catalog.py      # GET /api/catalog/categories
      export.py       # GET /api/export/*
  tests/
    conftest.py
    helpers.py
    test_books_search.py
    test_books_sort.py
    test_borrows.py
    test_fines.py
    test_readers.py
    test_reservations.py
    test_notifications.py
    test_profile.py
    test_stats.py
    test_export.py
    test_uc_compat.py
```

### Frontend structure

Thiết kế frontend thuần tĩnh:

```text
frontend/
  AGENTS.md
  UI_DESIGN.md
  index.html          # Trang đăng nhập (login)
  books.html           # Danh sách sách, tìm kiếm
  borrow.html          # Quản lý mượn/trả
  readers.html         # Quản lý độc giả
  profile.html         # Hồ sơ cá nhân
  stats.html           # Thống kê
  reservations.html    # Đặt trước sách
  requests.html        # Yêu cầu bổ sung sách
  notifications.html   # Thông báo
  my-borrows.html      # Lịch sử mượn (reader)
  register.html        # Đăng ký tài khoản
  search.html          # Tìm kiếm nâng cao
  admin-accounts.html  # Quản lý tài khoản (admin)
  admin-catalog.html   # Quản lý danh mục (admin)
  admin-config.html    # Cấu hình hệ thống (admin)
  css/
    style.css           # CSS custom + Google Fonts Be Vietnam Pro
  js/
    api.js              # Module trung tâm: wrapper fetch() với JWT header
    auth.js             # Xử lý đăng nhập, lưu token localStorage
    layout.js           # Render sidebar/header động theo role
    books.js            # Logic trang sách
    borrow.js           # Logic trang mượn/trả
    readers.js          # Logic trang độc giả
    profile.js          # Logic trang hồ sơ
    stats.js            # Logic trang thống kê
    reservations.js     # Logic trang đặt trước
    requests.js         # Logic trang yêu cầu
    notifications.js    # Logic trang thông báo
    my-borrows.js       # Logic trang lịch sử mượn
    register.js         # Logic trang đăng ký
    search.js           # Logic trang tìm kiếm
    admin-accounts.js   # Logic trang quản lý tài khoản
    admin-catalog.js    # Logic trang quản lý danh mục
    admin-config.js     # Logic trang cấu hình
    admin.js            # Logic chung trang admin
    notif-badge.js      # Badge thông báo
    notifications-core.js # Core thông báo
  assets/
    cropped-logoww.png  # Logo trường
```

### Domain model

Bắt buộc có:

- `Users`: `id`, `username`, `password_hash`, `role` (admin/librarian/reader), `reader_id` (nullable FK), timestamps.
- `Books`: `ma_sach` (PK), `ten_sach`, `tac_gia`, `nha_xuat_ban`, `nam_xuat_ban`, `the_loai`, `soLuong`, `soLuongKhaDung`, `trang_thai`, timestamps.
- `Categories`: `id`, `ten_danh_muc`, `mo_ta`.
- `Readers`: `ma_doc_gia` (PK), `ho_ten`, `email`, `so_dien_thoai`, `dia_chi`, `diem_svnet` (default 100), `gioi_tinh`, timestamps.
- `BorrowRecords`: `ma_phieu` (PK), `reader_id` (FK), `book_id` (FK), `ngay_muon`, `han_tra`, `ngay_tra`, `da_tra`, `trang_thai`, timestamps.
- `FineHistory`: `id`, `borrow_id` (FK), `so_ngay_qua_han`, `so_diem`, `da_thu`, `ngay_thu`.
- `Reservations`: `id`, `reader_id` (FK), `book_id` (FK), `trang_thai`, timestamps.
- `Requests`: `id`, `reader_id` (FK), `ten_sach_yeu_cau`, `trang_thai`, `ghi_chu`, timestamps.
- `Notifications`: `id`, `user_id` (FK), `noi_dung`, `da_doc`, timestamps.
- `AuditLog`: `id`, `user_id`, `action`, `detail`, timestamps.
- `soLuongKhaDung` phải >= 0.
- Mượn sách trừ 1 `soLuongKhaDung`; trả cộng 1.
- Phạt quá hạn: `so_diem = so_ngay_qua_han × overdue_fine_points_per_day` (mặc định 2 điểm/ngày).
- Thu phạt trừ điểm `diem_svnet` của độc giả (không âm).
- Xóa sách đang có phiếu mượn chưa trả phải bị chặn hoặc báo lỗi rõ.

### API contract

Thiết kế contract chi tiết cho từng endpoint (Method, URL, Request Body, Response, Error codes, Auth requirement, Role requirement). Ví dụ:

- `POST /api/auth/login`: Body `{username, password}` → Response `{access_token, token_type, role}` | 401 `"Sai thông tin đăng nhập"`.
- `GET /api/books?search=&the_loai=&sort=`: Response `[{ma_sach, ten_sach, tac_gia, soLuong, soLuongKhaDung, ...}]`.
- `POST /api/borrows`: Auth required, Body `{book_id, reader_id}` → 201 | 400 `"Hết sách"` | 400 `"Độc giả đã mượn tối đa"`.
- `PUT /api/borrows/{ma}/return`: Response `{message, ngay_tra, fine: {so_ngay_qua_han, so_diem} | null}`.
- `POST /api/borrows/{ma}/collect-fine`: Role `librarian` only → Response `{message, so_diem_da_thu, diem_con_lai, ngay_thu}`.

Response lỗi dùng format:

```json
{"detail": "Mô tả lỗi rõ ràng"}
```

### UI/UX Design

Thiết kế giao diện:

- Sử dụng CSS custom (`css/style.css`) + Google Fonts Be Vietnam Pro (wght 400–800);
- Không dùng Bootstrap/Tailwind, tự viết layout responsive;
- Sidebar điều hướng bên trái, render động theo role (js/layout.js);
- Header có logo trường, tên hệ thống, avatar/tên người dùng;
- Trang login có card đăng nhập nền gradient;
- Các trang CRUD có: bảng dữ liệu, form thêm/sửa (modal hoặc inline), ô tìm kiếm, bộ lọc;
- Responsive: sidebar thu gọn trên mobile;
- Accessibility: label rõ, focus visible;
- Dark/light theme tùy chọn (nếu có).

### Database và config

- SQL Server kết nối qua `mssql+pyodbc://...` trong `backend/app/config.py`;
- Connection string lưu trong `.env` (không commit);
- Có `.env.example` mẫu;
- Migrations bằng Alembic (thư mục `backend/alembic/`);
- Không đổi sang DB khác (SQLite, PostgreSQL).

### Tests

Thiết kế test (pytest + httpx TestClient):

- test đăng nhập đúng/sai;
- test CRUD sách (thêm, sửa, xóa, tìm kiếm, sắp xếp);
- test CRUD độc giả;
- test luồng mượn/trả (mượn → kiểm tra số lượng giảm → trả → kiểm tra số lượng tăng);
- test phạt quá hạn (mượn → trả muộn → kiểm tra FineHistory);
- test thu phạt (trừ điểm SVNET);
- test đặt trước sách;
- test thông báo;
- test thống kê;
- test xuất báo cáo;
- test phân quyền (reader không được xóa sách, chỉ librarian thu phạt);
- test hồ sơ cá nhân.

## Review và quality gate

Review để đảm bảo:

- mỗi MUST requirement có design ID;
- frontend dùng CSS custom, không dùng Bootstrap;
- frontend gọi API qua Fetch, không dùng framework JS;
- backend là FastAPI với SQL Server;
- xác thực JWT;
- không over-engineering.

## OUTPUT

Tạo: `docs/02_design.md`

Cuối file:

```text
STATUS: PASS | FAIL
NEXT_INPUT: docs/02_design.md
NEXT_PROMPT: prompts/03_implementation_plan.md
TRACEABILITY_MATRIX_UPDATED: YES
```
