# 03 - KẾ HOẠCH TRIỂN KHAI (IMPLEMENTATION PLAN)

## 1. Bằng chứng áp dụng skill

| Skill | Vai trò | Bằng chứng |
|---|---|---|
| `writing-plans` | PRIMARY | Chia 24 tasks có dependency, task format chuẩn. |
| `tdd` | PRIMARY | Mỗi task gắn test-first path. |
| `fastapi-expert` | SUPPORTING | Lập thứ tự: config → models → schemas → security → deps → routers → tests. |
| `web-design-guidelines` | SUPPORTING | Task riêng cho CSS custom responsive. |

## 2. Phân chia Tasks

### Giai đoạn 1: Backend Core (Backend Agent)

| Task ID | Mục tiêu | Files | Dependencies | Agent |
|---|---|---|---|---|
| T-01 | Khởi tạo FastAPI app, CORS | `app/main.py`, `app/config.py` | — | Backend |
| T-02 | Cấu hình SQLAlchemy + SQL Server | `app/database.py`, `.env` | T-01 | Backend |
| T-03 | Tạo 10 SQLAlchemy models | `app/models.py` | T-02 | Backend |
| T-04 | Tạo Pydantic schemas | `app/schemas.py` | T-03 | Backend |
| T-05 | JWT + Bcrypt | `app/security.py` | T-01 | Backend |
| T-06 | Dependency injection | `app/deps.py` | T-05 | Backend |
| T-07 | Business validation | `app/validation.py` | T-03 | Backend |
| T-08 | Alembic migrations | `alembic/` | T-03 | Backend |

### Giai đoạn 2: API Routers (Backend Agent)

| Task ID | Mục tiêu | Files | Dependencies | Agent |
|---|---|---|---|---|
| T-09 | Router auth (login/register) | `routers/auth.py` | T-06 | Backend |
| T-10 | Router books (CRUD) | `routers/books.py` | T-06, T-07 | Backend |
| T-11 | Router readers (CRUD) | `routers/readers.py` | T-06 | Backend |
| T-12 | Router borrows (mượn/trả/phạt) | `routers/borrows.py` | T-06, T-07 | Backend |
| T-13 | Router reservations | `routers/reservations.py` | T-06 | Backend |
| T-14 | Router requests | `routers/requests.py` | T-06 | Backend |
| T-15 | Router notifications | `routers/notifications.py` | T-06 | Backend |
| T-16 | Router stats, profile, admin | `routers/stats.py`, `profile.py`, `admin.py`, `accounts.py`, `catalog.py` | T-06 | Backend |
| T-17 | Router export | `routers/export.py` | T-06 | Backend |

### Giai đoạn 3: Frontend (Frontend Agent)

| Task ID | Mục tiêu | Files | Dependencies | Agent |
|---|---|---|---|---|
| T-18 | CSS custom responsive | `css/style.css` | — | Frontend |
| T-19 | Login page + auth.js | `index.html`, `js/auth.js`, `js/api.js` | T-09 | Frontend |
| T-20 | Layout sidebar (layout.js) | `js/layout.js` | T-19 | Frontend |
| T-21 | 15 trang HTML + JS | Tất cả `.html` + `js/*.js` | T-20 | Frontend |

### Giai đoạn 4: AI & QA

| Task ID | Mục tiêu | Files | Dependencies | Agent |
|---|---|---|---|---|
| T-22 | AI Engine gợi ý sách | `ai_engine/` | T-12 | AI Agent |
| T-23 | Viết tests (pytest) | `tests/*.py` | T-09 đến T-17 | QA Agent |
| T-24 | README + Báo cáo | `README.md`, `docs/` | T-23 | Thư ký |

## 3. Bảng Dependency

| Task ID | Depends on | Agent | Parallel? | Risk |
|---|---|---|---|---|
| T-01 | — | Backend | Yes | Low |
| T-03 | T-02 | Backend | No | Medium (schema phức tạp) |
| T-09 | T-06 | Backend | No | Low |
| T-19 | T-09 | Frontend | No (cần API login) | Medium |
| T-23 | T-09–T-17 | QA | After backend done | Low |

## 4. Verification Plan

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
pytest tests/ -v --tb=short
```

Smoke: POST login → GET books → POST borrow → PUT return → Mở frontend/index.html.

STATUS: PASS
NEXT_INPUT: docs/03_implementation_plan.md
NEXT_PROMPT: prompts/04_implementation.md
TRACEABILITY_MATRIX_UPDATED: YES
