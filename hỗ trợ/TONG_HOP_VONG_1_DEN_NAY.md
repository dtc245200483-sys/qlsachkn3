# Tổng hợp Frontend + Backend từ Vòng 1 đến hiện tại (2026-08-09)

## Tổng quan

- Web app: **Frontend HTML/CSS/JS thuần** + **Backend FastAPI + SQL Server** + AI Engine (chưa có code).
- Server chạy: `http://localhost:8000` (uvicorn, cần chạy ngoài sandbox để kết nối SQL Server).
- Nguồn chuẩn: `hỗ trợ/DE_BAI.md`.

## Lịch sử theo vòng

| Vòng | Chức năng | Frontend | Backend | Trạng thái |
|---|---|---|---|---|
| 1 | 1, 2: đăng nhập/phân quyền + quản lý sách | index.html, books.html + api.js nối API | auth.py, books.py, migration 0001 | ✅ Hoàn thiện (test UI 12/12, API login/CRUD sách) |
| 2 | YC-002: ranh giới Admin vs Thủ thư | UI_DESIGN.md + giao diện mới (navy #1E4B8C, WCAG AA+) | admin.py: config thư viện/AI, audit log, backup; migration 0002-0003 | ✅ (đã XOÁ phần "quản lý tài khoản thủ thư" — ngoài đề bài) |
| 3 | 3: quản lý độc giả | readers.html + js/readers.js | readers.py + migration 0004 | ✅ (test 9/9) |
| 4 | 4: mượn/trả/gia hạn/phạt | **chưa thấy file UI mượn/trả trong workspace** | borrows.py + migration 0005 | ⚠️ Backend ✅ (test 10/10, tổng 19/19) — Frontend cần xác nhận |
| 5 | 5: tra cứu sách | search.html + js/search.js | books.py thêm query q/theLoai/trangThai | ✅ (test 9 case, tổng 28/28) |
| 6 | 6: đặt trước sách | chưa làm (prompt Frontend đã đưa) | chưa làm | ⏳ Đang chờ |

## Backend hiện tại

### Routers và endpoint

| Router | Endpoint | Quyền |
|---|---|---|
| auth | POST `/api/auth/login` | Không cần token |
| books | GET `/api/books` (+ `q`, `theLoai`, `trangThai`) | Mọi role |
| books | POST/PUT/DELETE `/api/books` , `/api/books/{ma}` | librarian, admin |
| readers | GET/POST `/api/readers` (+ `q`) | librarian, admin |
| readers | PUT `/api/readers/{ma}` | librarian, admin |
| readers | DELETE `/api/readers/{ma}` | admin |
| borrows | POST `/api/borrows` | librarian, admin |
| borrows | PUT `/api/borrows/{ma}/return` | librarian, admin |
| borrows | PUT `/api/borrows/{ma}/renew` | librarian, admin |
| borrows | GET `/api/borrows` | librarian, admin |
| admin | GET/PUT `/api/admin/config/library` | đọc: admin+librarian; ghi: admin |
| admin | GET/PUT `/api/admin/config/ai` | admin |
| admin | GET `/api/admin/audit-logs` | admin |
| admin | POST `/api/admin/backup` | admin |

### Bảng dữ liệu (migrations 0001-0005)

- Users (tài khoản đăng nhập: admin/librarian/reader, is_active)
- Books (sách)
- Readers (độc giả: loại, trạng thái thẻ)
- BorrowSlips, BorrowDetails, FineHistory (mượn/trả/gia hạn/phạt)
- LibraryConfig (số ngày mượn, phạt/ngày, giới hạn số sách)
- AIConfig (provider, model, api_key, prompt template)
- AuditLog (nhật ký hệ thống)

### Test hiện có: 28/28 PASS

- test_readers.py: 9 case (CRUD, khoá thẻ, phân quyền)
- test_borrows.py: 10 case (mượn khi sách còn 0 → lỗi; trả trễ → phạt đúng công thức; gia hạn quá 1 lần → lỗi)
- test_books_search.py: 9 case (tìm tên/tác giả, lọc thể loại/trạng thái, kết hợp param)

## Frontend hiện tại

| Trang | Chức năng | JS |
|---|---|---|
| index.html | Đăng nhập, phân vai | auth.js |
| books.html | Quản lý sách: danh sách + thêm/sửa/xoá | books.js |
| readers.html | Quản lý độc giả: danh sách + tìm + thêm/sửa/khoá thẻ/xoá | readers.js |
| search.html | Tra cứu sách: tìm tên/tác giả, lọc thể loại/trạng thái | search.js |

- api.js: baseUrl localhost:8000, endpoints login/books/readers + fieldMap + roleMap.
- css/style.css theo UI_DESIGN.md; logo ICTU; menu ẩn/hiện theo role (reader chỉ tra cứu).

## Đối chiếu 8 chức năng quản lý (chưa tính AI)

| # | Chức năng | Backend | Frontend | Kết luận |
|---|---|---|---|---|
| 1 | Đăng nhập, phân quyền 3 vai trò | ✅ | ✅ | ✅ |
| 2 | Quản lý sách | ✅ | ✅ | ✅ |
| 3 | Quản lý độc giả | ✅ | ✅ | ✅ |
| 4 | Mượn/trả/gia hạn/phạt | ✅ | ⚠️ chưa thấy file UI | ⚠️ |
| 5 | Tra cứu sách | ✅ | ✅ | ✅ |
| 6 | Đặt trước sách | ❌ | ❌ | ❌ |
| 7 | Thống kê | ❌ | ❌ | ❌ |
| 8 | Xuất danh sách/báo cáo | ❌ | ❌ | ❌ |

## Dữ liệu demo hiện có

- 5 sách S001-S005 (tiếng Việt chuẩn).
- 3 tài khoản: admin/admin1, librarian/librarian1, reader/reader1.
- Chưa có dữ liệu mẫu: độc giả, phiếu mượn (nên tạo thêm sau khi xong các chức năng để demo).

## Còn thiếu để hoàn thiện phần quản lý

1. Chức năng 4: UI mượn/trả (xác nhận/làm lại nếu chưa có file).
2. Chức năng 6: đặt trước (Frontend + Backend) — đang ở vòng này.
3. Chức năng 7: thống kê.
4. Chức năng 8: xuất danh sách/phiếu mượn/báo cáo.
5. Sau đó: AI-1, AI-2, AI-3 + Thư Ký quét tổng.
