# 02 - THIẾT KẾ HỆ THỐNG CHI TIẾT (SYSTEM DESIGN)

## 1. Bằng chứng áp dụng skill

| Skill | Vai trò | Bằng chứng |
|---|---|---|
| `software-architecture` | PRIMARY | Kiến trúc 3 tầng: Frontend (HTML/CSS/JS) → Backend (FastAPI) → DB (SQL Server). Bảo mật vòng ngoài CORS, vòng trong JWT. |
| `database-design` | PRIMARY | Schema SQL Server chi tiết: 10 bảng, PK, FK, Indexes, Constraints. |
| `fastapi-expert` | PRIMARY | Cấu trúc thư mục FastAPI chuẩn: routers, models, schemas, deps, security. Dependency injection. |
| `domain-modeling` | PRIMARY | 10 entities chuẩn hóa với states, invariants, business rules. |
| `web-design-guidelines` | SUPPORTING | CSS custom responsive + Google Fonts Be Vietnam Pro. |

## 2. Input và điều kiện tiếp tục

| Input | Kết quả kiểm tra |
|---|---|
| `docs/01_requirements.md` | Có `STATUS: PASS`. |
| `00_project.md` | Cung cấp bối cảnh nghiệp vụ thư viện. |

## 3. Source trace

| Source ID | Nguồn | Nội dung |
|---|---|---|
| SRC-001 | `docs/01_requirements.md` | Backend FastAPI trong `backend/`, frontend HTML trong `frontend/`, SQL Server. |
| SRC-002 | `docs/01_requirements.md` | CRUD sách, độc giả, mượn/trả, phạt, đặt trước, yêu cầu, thông báo, thống kê, admin. |
| SRC-003 | `00_project.md` | Nghiệp vụ thư viện, phân quyền RBAC, AI gợi ý sách. |
| SRC-004 | `prompts/02_design.md` | Bắt buộc CSS custom, Vanilla JS Fetch, FastAPI, JWT, SQL Server. |

## 4. Architecture

Root project gồm các thư mục chính:

```text
app/
  backend/         # FastAPI REST API
  frontend/        # HTML tĩnh + CSS custom + Vanilla JS
  ai_engine/       # Module AI gợi ý sách
  qa/              # Kiểm thử
  thuky/           # Thư ký Agent (changelog, báo cáo)
  support/         # Trợ lý Agent (tài liệu hỗ trợ)
  docs/            # Tài liệu phân tích thiết kế
  prompts/         # Kịch bản 6 bước
  scripts/         # Scripts tự động
```

`backend/` là FastAPI project cung cấp REST API JSON. Frontend gọi API qua HTTP Fetch. Hai phần tách rời hoàn toàn, giao tiếp qua REST.

`frontend/` là tập hợp 15 file HTML tĩnh, mỗi trang có file JS riêng tại `js/`. CSS custom duy nhất tại `css/style.css`. Không dùng Bootstrap, Tailwind, React, Vue.

Luồng chạy chính:

```text
Browser
  -> frontend/index.html (Login page)
  -> frontend/js/auth.js (POST /api/auth/login)
  -> Lưu JWT token vào localStorage
  -> Redirect sang frontend/books.html
  -> frontend/js/layout.js (Render sidebar theo role)
  -> frontend/js/books.js (GET /api/books)
  -> backend/app/routers/books.py
  -> backend/app/deps.py (verify JWT)
  -> backend/app/models.py (SQLAlchemy query)
  -> SQL Server
```

## 5. Backend structure

```text
backend/
  .env                    # Connection string, JWT secret (không commit)
  .env.example            # Mẫu .env
  alembic.ini             # Cấu hình Alembic
  requirements.txt        # Dependencies production
  requirements-dev.txt    # Dependencies test (pytest, httpx)
  reset_db.py             # Script reset database
  api_docs.md             # API documentation chi tiết
  AGENTS.md               # Vai trò Backend Agent
  alembic/
    env.py
    script.py.mako
    versions/              # Migration files
  app/
    __init__.py
    main.py                # FastAPI(), CORS, include_router()
    config.py              # Settings: DB_URL, JWT_SECRET, JWT_EXPIRE
    database.py            # engine, SessionLocal, Base
    models.py              # 10 SQLAlchemy models
    schemas.py             # Pydantic request/response schemas
    security.py            # jwt_encode(), jwt_decode(), hash_password(), verify_password()
    deps.py                # get_db(), get_current_user(), require_role()
    audit.py               # log_audit()
    validation.py          # check_borrow_limit(), check_book_available()
    routers/
      __init__.py
      auth.py              # POST /api/auth/login, /register
      books.py             # GET|POST /api/books, GET|PUT|DELETE /api/books/{id}
      readers.py           # GET|POST /api/readers, GET|PUT|DELETE /api/readers/{id}
      borrows.py           # GET|POST /api/borrows, PUT return/renew, POST collect-fine, GET /me
      reservations.py      # GET|POST /api/reservations, PUT approve/reject
      requests.py          # GET|POST /api/requests, PUT approve/reject
      notifications.py     # GET /api/notifications, PUT mark-read
      stats.py             # GET /api/stats
      profile.py           # GET|PUT /api/profile, PUT change-password
      accounts.py          # GET /api/admin/accounts, POST create, PUT toggle
      admin.py             # GET|PUT /api/admin/config
      catalog.py           # GET /api/catalog/categories
      export.py            # GET /api/export/books, /readers, /borrows
  tests/
    conftest.py            # Fixtures: test client, test DB, test users
    helpers.py             # Helper functions
    test_books_search.py   # 7 test cases tìm kiếm sách
    test_books_sort.py     # 5 test cases sắp xếp sách
    test_borrows.py        # 10 test cases mượn/trả
    test_fines.py          # 6 test cases phạt/thu phạt
    test_readers.py        # 5 test cases CRUD độc giả
    test_reservations.py   # 12 test cases đặt trước
    test_notifications.py  # 8 test cases thông báo
    test_profile.py        # 6 test cases hồ sơ
    test_stats.py          # 4 test cases thống kê
    test_export.py         # 5 test cases xuất báo cáo
    test_uc_compat.py      # 15 test cases tương thích Use Case
```

## 6. Frontend structure

```text
frontend/
  AGENTS.md                # Vai trò Frontend Agent
  UI_DESIGN.md             # Tài liệu thiết kế UI
  index.html               # Login (trang chủ)
  books.html               # Danh sách sách
  borrow.html              # Quản lý mượn/trả
  readers.html             # Quản lý độc giả
  profile.html             # Hồ sơ cá nhân
  stats.html               # Thống kê
  reservations.html        # Đặt trước
  requests.html            # Yêu cầu bổ sung
  notifications.html       # Thông báo
  my-borrows.html          # Lịch sử mượn (reader)
  register.html            # Đăng ký
  search.html              # Tìm kiếm nâng cao
  admin-accounts.html      # Quản lý tài khoản (admin)
  admin-catalog.html       # Quản lý danh mục (admin)
  admin-config.html        # Cấu hình hệ thống (admin)
  css/
    style.css              # CSS custom duy nhất (23KB). Google Fonts Be Vietnam Pro. Responsive.
  js/
    api.js                 # Module trung tâm (19KB): wrapper fetch(), gắn JWT header tự động.
    auth.js                # Login logic, lưu token + role vào localStorage.
    layout.js              # Render sidebar/header theo role. Thu gọn sidebar mobile.
    books.js               # Load sách, tìm kiếm, sắp xếp, thêm/sửa/xóa.
    borrow.js              # Tạo phiếu mượn, trả sách, gia hạn, thu phạt.
    readers.js             # CRUD độc giả, tìm kiếm.
    profile.js             # Xem/sửa hồ sơ, đổi mật khẩu.
    stats.js               # Hiển thị thống kê.
    reservations.js        # Đặt trước, duyệt/từ chối.
    requests.js            # Yêu cầu bổ sung, duyệt/từ chối.
    notifications.js       # Danh sách thông báo.
    my-borrows.js          # Lịch sử mượn của reader.
    register.js            # Đăng ký tài khoản.
    search.js              # Tìm kiếm nâng cao.
    admin-accounts.js      # Quản lý tài khoản admin.
    admin-catalog.js       # Quản lý danh mục admin.
    admin-config.js        # Cấu hình hệ thống admin.
    admin.js               # Logic chung admin.
    notif-badge.js         # Badge số thông báo chưa đọc.
    notifications-core.js  # Core thông báo.
  assets/
    cropped-logoww.png     # Logo trường ICTU
```

## 7. Domain model (SQL Server)

### Bảng Users
| Cột | Kiểu | Ràng buộc |
|---|---|---|
| id | INT | PK, IDENTITY |
| username | NVARCHAR(50) | UNIQUE, NOT NULL |
| password_hash | NVARCHAR(255) | NOT NULL |
| role | NVARCHAR(20) | NOT NULL, CHECK IN ('admin','librarian','reader') |
| reader_id | INT | FK → Readers.ma_doc_gia, NULLABLE |

### Bảng Books
| Cột | Kiểu | Ràng buộc |
|---|---|---|
| ma_sach | INT | PK, IDENTITY |
| ten_sach | NVARCHAR(255) | NOT NULL |
| tac_gia | NVARCHAR(255) | |
| nha_xuat_ban | NVARCHAR(255) | |
| nam_xuat_ban | INT | |
| the_loai | NVARCHAR(100) | |
| soLuong | INT | NOT NULL, >= 0 |
| soLuongKhaDung | INT | NOT NULL, >= 0 |
| trang_thai | NVARCHAR(20) | DEFAULT 'active' |

### Bảng Readers
| Cột | Kiểu | Ràng buộc |
|---|---|---|
| ma_doc_gia | INT | PK, IDENTITY |
| ho_ten | NVARCHAR(255) | NOT NULL |
| email | NVARCHAR(255) | UNIQUE |
| so_dien_thoai | NVARCHAR(20) | |
| dia_chi | NVARCHAR(500) | |
| diem_svnet | INT | DEFAULT 100, >= 0 |
| gioi_tinh | NVARCHAR(10) | |

### Bảng BorrowRecords
| Cột | Kiểu | Ràng buộc |
|---|---|---|
| ma_phieu | INT | PK, IDENTITY |
| reader_id | INT | FK → Readers, NOT NULL |
| book_id | INT | FK → Books, NOT NULL |
| ngay_muon | DATETIME | NOT NULL |
| han_tra | DATETIME | NOT NULL |
| ngay_tra | DATETIME | NULLABLE |
| da_tra | BIT | DEFAULT 0 |

### Bảng FineHistory
| Cột | Kiểu | Ràng buộc |
|---|---|---|
| id | INT | PK, IDENTITY |
| borrow_id | INT | FK → BorrowRecords, NOT NULL |
| so_ngay_qua_han | INT | NOT NULL |
| so_diem | INT | NOT NULL |
| da_thu | BIT | DEFAULT 0 |
| ngay_thu | DATETIME | NULLABLE |

### Bảng Reservations, Requests, Notifications, AuditLog
(Cấu trúc tương tự, có FK tương ứng)

## 8. API Contract

### 8.1 Authentication
- `POST /api/auth/login`: Body `{username, password}` → `{access_token, token_type, role}` | 401.

### 8.2 Books
- `GET /api/books?search=&the_loai=&sort=`: → `[{ma_sach, ten_sach, tac_gia, soLuong, soLuongKhaDung, ...}]`.
- `POST /api/books`: Auth admin/librarian → 201.
- `PUT /api/books/{id}`: Auth admin/librarian → 200.
- `DELETE /api/books/{id}`: Auth admin → 200 | 400 nếu đang có phiếu mượn.

### 8.3 Borrows
- `POST /api/borrows`: Auth → 201 | 400 "Hết sách" | 400 "Đã mượn tối đa".
- `PUT /api/borrows/{ma}/return`: → `{message, ngay_tra, fine: {so_ngay_qua_han, so_diem} | null}`.
- `PUT /api/borrows/{ma}/renew`: Tối đa 1 lần.
- `POST /api/borrows/{ma}/collect-fine`: Role librarian → `{message, so_diem_da_thu, diem_con_lai, ngay_thu}` | 403.
- `GET /api/borrows/me`: Role reader → phiếu của chính mình.

### 8.4 Các API còn lại
(Reservations, Requests, Notifications, Stats, Profile, Admin — chi tiết tại `backend/api_docs.md`)

## 9. UI/UX Design

- CSS custom (`css/style.css`, 23KB) + Google Fonts Be Vietnam Pro (wght 400–800);
- Không dùng Bootstrap, Tailwind, framework CSS;
- Trang login: card đăng nhập gradient, logo trường ICTU;
- Layout: sidebar trái (render bởi `js/layout.js`), header trên, content phải;
- Sidebar ẩn/hiện menu theo role (admin thấy tất cả, reader không thấy mục quản trị);
- Responsive: sidebar thu gọn trên mobile (breakpoint);
- Bảng dữ liệu: scroll ngang trên mobile;
- Form: modal hoặc inline;
- Google Fonts nhúng qua CDN link trong HTML head.

## 10. Bảo mật & Cấu hình

- CORS: `CORSMiddleware` cho phép frontend gọi API cross-origin.
- JWT Secret: trong `.env` (không commit).
- Password Hashing: Passlib Bcrypt.
- SQL Server: connection string `mssql+pyodbc://...` trong `.env`.
- Alembic: migrations tại `backend/alembic/versions/`.

STATUS: PASS
NEXT_INPUT: docs/02_design.md
NEXT_PROMPT: prompts/03_implementation_plan.md
TRACEABILITY_MATRIX_UPDATED: YES
