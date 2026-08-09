# QA — Hệ thống quản lý thư viện tích hợp AI

Thư mục đầu ra của Agent QA. QA **không sửa code** Backend/Frontend/AI Engine, chỉ đọc code và ghi báo cáo.

## Cấu trúc

```
QA/
  README.md
  test_cases.md                 # Tổng hợp test case đúng/sai/biên
  bug_reports.md                # Báo cáo lỗi (kèm bằng chứng)
  backend/
    conftest.py                 # Client HTTP + token cho DB QA
    test_*.py                   # 96 test API (đúng/sai/biên)
    seed_qa_db.py               # Seed dữ liệu QA (LibraryDB_QA)
    run_qa_tests.ps1            # Reset DB QA + migrate + seed + start server + pytest
    qa_server.pid               # PID server QA (tự tạo khi chạy)
  frontend/
    check_frontend.py           # Kiểm tra file tham chiếu + endpoint api.js vs OpenAPI
    test_cases_ui.md            # Kịch bản test UI thủ công
```

## Chạy backend test QA (tự động, DB riêng)

Yêu cầu: SQL Server `localhost\QUANGHUNG`, ODBC Driver 17, quyền tạo DB `LibraryDB_QA`.

```powershell
powershell -ExecutionPolicy Bypass -File "D:\ung dung tri tue nhan ao\app\QA\backend\run_qa_tests.ps1"
```

Script sẽ:
1. Dừng server QA cũ (nếu có).
2. Xóa/tạo lại `LibraryDB_QA` — **không đụng `LibraryDB` thật**.
3. Chạy migration Alembic + seed dữ liệu `QA*`.
4. Khởi động backend QA ở `127.0.0.1:8001`.
5. Chạy `pytest` (96 test).
6. Dừng server QA (thêm `-KeepRunning` nếu muốn giữ).

Hoặc chạy thủ công:

```powershell
cd "D:\ung dung tri tue nhan ao\app\Backend"
$env:DATABASE_URL='mssql+pyodbc://@localhost\QUANGHUNG/LibraryDB_QA?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes'
python -m alembic upgrade head
python ..\QA\backend\seed_qa_db.py
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
# terminal khác:
cd "D:\ung dung tri tue nhan ao\app\QA\backend"
python -m pytest -q
```

## Chạy bộ test gốc của Backend trên DB QA (không đụng DB thật)

```powershell
cd "D:\ung dung tri tue nhan ao\app\Backend"
$env:DATABASE_URL='mssql+pyodbc://@localhost\QUANGHUNG/LibraryDB_QA?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes'
python -m pytest -q
```

Kết quả đã ghi nhận: 66/67 pass, 1 fail do test không cô lập dữ liệu (BUG-007).

## Kiểm tra tĩnh Frontend

```powershell
cd "D:\ung dung tri tue nhan ao\app"
python QA/frontend/check_frontend.py http://localhost:8000
```

## Tài khoản seed QA

- `qa_admin` / `qa_librarian` / `qa_reader1` / `qa_reader2`
- Mật khẩu: `Test@12345`

## Kết quả chốt

- QA backend: **96/96 PASS** (DB sạch).
- Backend gốc: **66/67 PASS** (1 fail test-isolation, BUG-007).
- Frontend static: **PASS**.
- UI manual: xem `frontend/test_cases_ui.md`.
- Bug: `bug_reports.md` — 8 bug + 1 trạng thái AI chưa triển khai.
