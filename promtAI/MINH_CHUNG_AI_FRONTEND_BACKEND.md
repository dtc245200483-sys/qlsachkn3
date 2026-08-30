<!-- Bản sao lưu trong promtAI — nguồn gốc: thuky/MINH_CHUNG_AI_FRONTEND_BACKEND.md (đồng bộ mỗi lần cập nhật) -->
# Minh chứng sử dụng AI — Frontend & Backend

- Dự án: Hệ thống quản lý thư viện có tích hợp AI
- Ngày lập: 2026-08-09 17:08:34 (Thư Ký tổng hợp từ hồ sơ)
- Phạm vi: toàn bộ hoạt động của Frontend Agent và Backend Agent từ đầu tới nay
- Nguồn chính: thuky/changelog_tong.md, thuky/trang_thai_quet.md, LOG_THU_KY.md
  của các agent, file prompt + code hiện tại trong Backend/Frontend.

> Ghi chú độ tin cậy: mục "LOG CHÍNH THỨC" là agent tự báo cáo; mục
> "PHÁT HIỆN TỪ QUÉT" là Thư Ký suy đoán từ code (không phải agent khai báo).
>
> QUY TẮC CẬP NHẬT (2026-08-09 17:13): file này được Thư Ký cập nhật tự động
> MỖI LẦN người dùng yêu cầu "cập nhật thư ký" / "quét lại dự án", vì đây là
> minh chứng sử dụng AI cần nộp. Bản sao trong promtAI được đồng bộ cùng lúc.

## 1. Timeline tổng quan

| Thời gian | Agent | Nội dung chính |
|---|---|---|
| 06:28 | Thư Ký | Quét đầu tiên: Backend/AGENTS.md + AI_Engine/AI.txt (prompt, chưa code) |
| 06:46:46 | Frontend | Log 1: tạo index.html, books.html, css, api.js, auth.js, books.js |
| 07:02:48 | Backend | Log 1: hoàn thiện API chức năng 1, 2 + api_docs v0.1.0 |
| 07:12 | Frontend (quét) | api.js được điền config theo api_docs |
| 07:41:41 | Frontend | Log 2: nối API, test API + UI Chrome headless 12/12 PASS |
| 07:43 | Thư Ký | Tạo 3 tài khoản admin/librarian/reader (theo yêu cầu người dùng) |
| 08:06:16 | Backend | Log 2: YC-002 ranh giới Admin vs Librarian (admin API, bảng mới) |
| 09:49:03 | Backend | Log 3: chức năng 3 — /api/readers, migration 0004, test 9/9 |
| 09:55 | Trợ Lý | Xoá "Quản lý tài khoản thủ thư" (không có trong đề bài); tạo 5 sách mẫu S001-S005 |
| 10:03:12 | Frontend | Log 3: UI Quản lý độc giả (readers.html/readers.js), test API 16/16 |
| 10:27:48 | Backend | Log 4: chức năng 4 — /api/borrows, migration 0005, test 19/19 |
| 10:43:48 | Backend | Log 5: chức năng 5 — tra cứu sách, test 28/28 |
| 16:40–16:47 | Frontend (quét) | Thêm borrow.html/borrow.js, search.html/search.js, nối API (chưa có log) |
| 17:35:06 | Backend | Đợt A Use Case: register, borrows/me, requests, admin accounts/categories/publishers/restore — 38/38 |
| 18:01:49 | Frontend | Yêu cầu mượn: reader nhập so_ngay_muon (requests.html) — 6/6 |
| 18:07:45 | Frontend | Tự sinh mã yêu cầu tránh 409 — 5/5 |
| 18:17:43 | Frontend | Xoá lịch sử mượn (my-borrows) — 5/5; Backend chưa có DELETE |

## 2. Minh chứng Backend

### 2.1 Prompt/vai trò
- File: Backend/AGENTS.md (tạo 06:11, cập nhật 07:54 theo YC-002)
- Bản sao lịch sử đầy đủ: promtAI/BACKEND_AGENT_PROMPT.md
- Nội dung: FastAPI/SQLAlchemy/Alembic, 8 chức năng quản lý, phân quyền 3 vai trò,
  API lọc dữ liệu nhạy cảm cho AI Engine, checklist trước khi báo xong.

### 2.2 Log chính thức (nguyên văn từ LOG_THU_KY.md)

[BACKEND] 2026-08-09 07:02:48 - Thay đổi: Hoàn thiện API chức năng 1, 2 và cung cấp file tài liệu API để giải quyết cảnh báo lệch pha. - Chức năng đề bài liên quan: 1, 2

[BACKEND] 2026-08-09 08:06:16 - Thay đổi: Triển khai ranh giới quyền Admin vs Librarian theo YC-2026-08-09-002 — 4 nhóm quyền admin-only (quản lý tài khoản thủ thư, cấu hình tham số thư viện, cấu hình AI Engine, audit log + backup); giữ nguyên 3 role admin/librarian/reader, không gộp role. Thêm bảng LibraryConfig, AIConfig, AuditLog; thêm cột Users.is_active (khoá tài khoản); thêm API /api/admin/*; ghi audit log tự động cho login, CRUD sách, quản lý tài khoản, cấu hình, backup; cập nhật api_docs.md (bản 0.2.0). Migration: 0002, 0003.

[BACKEND] 2026-08-09 09:49:03 - Thay đổi: Hoàn thiện chức năng 3 (Quản lý độc giả) — migration 0004 tạo bảng Readers; API CRUD /api/readers; ghi audit log CREATE_READER/UPDATE_READER/DELETE_READER; tách biệt Readers với Users; cập nhật api_docs.md bản 0.3.0; test 9/9 PASS.

[BACKEND] 2026-08-09 10:27:48 - Thay đổi: Hoàn thiện chức năng 4 (Mượn/trả/gia hạn/phạt) — migration 0005 tạo bảng BorrowSlips, BorrowDetails, FineHistory; API POST /api/borrows, PUT /api/borrows/{ma}/return, PUT /api/borrows/{ma}/renew, GET /api/borrows; tự tính phạt theo LibraryConfig; test 19/19 PASS.

[BACKEND] 2026-08-09 10:43:48 - Thay đổi: Hoàn thiện chức năng 5 (Tra cứu sách) — GET /api/books hỗ trợ q, theLoai, trangThai; cập nhật api_docs.md bản 0.5.0; test 28/28 PASS.

[BACKEND] 2026-08-09 17:35:06 - Thay đổi: Đợt A Tương thích Use Case — migration 0006 (TheLoai, Nxb, YeuCau; Books.theLoaiId/nxbId; Users.reader_id); API register, /api/borrows/me, /api/requests + approve/reject, /api/admin/accounts, /api/admin/categories, /api/admin/publishers, /api/admin/restore; admin kế thừa quyền thủ thư; api_docs 0.6.0; test 38/38 PASS.

### 2.3 File code hiện tại
- API routers: auth.py, books.py, readers.py, borrows.py, admin.py, requests.py,
  accounts.py, catalog.py
- Core: models.py, schemas.py, audit.py, deps.py, security.py, config.py, main.py
- Migration: 0001 → 0002 → 0003 → 0004 → 0005 → 0006
- Test: test_readers.py, test_borrows.py, test_books_search.py, test_uc_compat.py
- Tài liệu: api_docs.md (0.6.0), README.md

### 2.4 Kết quả test (theo log Backend)
- Chức năng 3: 9/9 PASS
- Chức năng 4: 19/19 PASS
- Chức năng 5: 28/28 PASS
- Đợt A: 38/38 PASS

### 2.5 Ghi chú của Trợ Lý (09:55) liên quan Backend
- Đã xoá 4 API /api/admin/librarians* + 3 schema Librarian (không có trong đề bài)
- Backend cần restart server để /api/readers hoạt động (đã ghi nhận)

## 3. Minh chứng Frontend

### 3.1 Prompt/vai trò + thiết kế
- File: Frontend/AGENTS.md (07:54, cập nhật 09:54), Frontend/UI_DESIGN.md (09:17)
- Bản sao lịch sử đầy đủ: promtAI/FRONTEND_AGENT_PROMPT.md
- Nội dung: giao diện WCAG 2.1 AA+, bảng màu navy #0A2E5C/#1E4B8C, logo ICTU,
  phân quyền 3 vai trò, các màn hình 1-8 + AI, log gửi Thư Ký.

### 3.2 Log chính thức (nguyên văn)

[FRONTEND] 2026-08-09 06:46:46 - Thay đổi: Tạo 2 màn hình HTML thuần — đăng nhập (index.html) và quản lý sách CRUD (books.html), kèm css/style.css, js/api.js, js/auth.js, js/books.js; API chưa có tài liệu nên giữ cấu hình trống trong api.js, UI hiện lỗi thay vì tự đoán endpoint/field. - Chức năng: 1, 2

[FRONTEND] 2026-08-09 07:41:41 - Thay đổi: Đã nối api.js theo Backend/api_docs.md v0.1.0; sửa books.js giữ thông báo thành công; đã kiểm thử API (login 200/401/403, CRUD sách) và UI Chrome headless 12/12 PASS; dữ liệu test tạm đã dọn sạch. - Chức năng: 1, 2

[FRONTEND] 2026-08-09 10:03:12 - Thay đổi: Tạo trang Quản lý độc giả (readers.html + readers.js); thêm endpoints readers/createReader/updateReader/deleteReader + fieldMap readerOut vào api.js; thêm requireStaff vào auth.js; thêm tab Quản lý độc giả ở books.html; đã test API 16/16 + UI 3 vai trò, librarian xoá bị 403, reader bị chặn. - Chức năng: 3

[FRONTEND] 2026-08-09 18:01:49 - Thay đổi: reader nhập so_ngay_muon khi gửi yêu cầu MUON (requests.html), bảng duyệt thủ thư hiện "Số ngày"; Backend 0.6.0 chưa lưu/trả so_ngay_muon → cần bổ sung; test 6/6 PASS. - Chức năng: 4

[FRONTEND] 2026-08-09 18:07:45 - Thay đổi: Tự động sinh mã yêu cầu cho reader (tránh 409); xác minh mượn lại sau khi trả; test 5/5 PASS. - Chức năng: 4

[FRONTEND] 2026-08-09 18:17:43 - Thay đổi: Thêm nút Xoá lịch sử mượn (my-borrows.html); khai báo deleteMyBorrow (DELETE /api/borrows/me/{ma}) + deleteMyBorrows (DELETE /api/borrows/me); Backend chưa có 2 endpoint; test 5/5 PASS. - Chức năng: 4

### 3.3 File hiện tại
- Trang: index, books, readers, borrow, search, register, my-borrows, requests,
  admin-accounts, admin-catalog
- JS: api.js, auth.js, books.js, readers.js, borrow.js, search.js, register.js,
  my-borrows.js, requests.js, admin.js, admin-accounts.js, admin-catalog.js
- Tài nguyên: css/style.css, assets/cropped-logoww.png, UI_DESIGN.md
- API đã nối trong api.js: login, register, books (query), readers, borrows,
  borrows/me (GET + DELETE), requests/approve/reject, admin accounts/
  categories/publishers

### 3.4 Kết quả test (theo log Frontend — KHÔNG có file test lưu trong repo)
- 07:41:41: API login/CRUD sách + UI Chrome headless 12/12 PASS
- 10:03:12: API 16/16 PASS + UI 3 vai trò
- 18:01:49: 6/6 PASS; 18:07:45: 5/5 PASS; 18:17:43: 5/5 PASS

### 3.5 Phát hiện từ quét (chưa có log chính thức)
- 07:12:12: api.js điền config theo api_docs v0.1.0
- 07:41:01: books.js chỉnh giữ thông báo thành công
- 08:47–09:40: UI_DESIGN.md, logo, khung admin.js, requireAdmin, giao diện mới
- 16:40–16:47: borrow.html/borrow.js + search.html/search.js + api.js nối
  /api/borrows và query books (chức năng 4, 5)
- 17:41–18:07: register, my-borrows, admin-accounts, admin-catalog, requests
  + api.js nối đầy đủ (chưa có log riêng cho các trang này)

## 4. Liên kết tài liệu
- Đề bài gốc: hỗ trợ/DE_BAI.md
- Quy trình vòng lặp: hỗ trợ/QUY_TRINH_CHAY_TUAN_TU.md
- Yêu cầu đồng bộ: thuky/yeu_cau_dong_bo.md (YC-001 → YC-006)
- Cảnh báo lệch pha: thuky/canh_bao_dong_bo.md
- Nhật ký đầy đủ: thuky/changelog_tong.md

## 5. Trạng thái hiện tại (18:19)
- Backend: 1-5 + Đợt A Use Case (0.6.0); đang chờ YC-005 (so_ngay_muon) và YC-006
  (DELETE lịch sử mượn)
- Frontend: UI 1-5 + register/my-borrows/requests/admin; các log chính thức mới
  nhất 18:01:49, 18:07:45, 18:17:43; một số trang chưa có log riêng
- AI Engine: chưa có code

### Lưu ý mâu thuẫn cần người dùng xác nhận
- 09:55: xoá "Quản lý tài khoản thủ thư" (không có trong đề bài).
- 17:35 Đợt A: thêm lại /api/admin/accounts + UI admin-accounts.html.
- Thư Ký liệt kê cả 2, không tự quyết định.

## 7. CẬP NHẬT 2026-08-09 19:03

### Backend
- Log 18:21:59 — 2 endpoint DELETE /api/borrows/me/* (reader, chỉ phiếu đã trả;
  xoá BorrowDetails + FineHistory; không đổi soLuong); test 43/43 PASS →
  YC-006 HOÀN THÀNH.
- Log 19:02:38 — chức năng 6 Đặt trước: migration 0007 (DatTruoc), API
  /api/reservations (GET/POST, PUT cancel/fulfill), trả sách → SAN_SANG,
  gia hạn bị chặn khi có đặt trước; admin 403 trên mượn/trả/đặt trước;
  api_docs 0.7.0; test 50/50 PASS.

### Frontend (theo quét, chưa có log riêng)
- reservations.html/js + reservation-mock.js (mock fallback); api.js nối
  reservations/create/cancel/fulfill — chờ xác nhận dùng API thật (YC-007).
- my-borrows.js nối 2 endpoint DELETE; menu phân quyền mới khớp Backend 0.7.0.
- scripts/cleanup_old_data.py — script dọn dữ liệu test.

### Trạng thái
- YC-005 (so_ngay_muon): VẪN CHỜ Backend. YC-006: HOÀN THÀNH. YC-007: CHỜ Frontend.

## 8. CẬP NHẬT 2026-08-09 19:13 — UC11 Thông báo (Frontend)

- Log: [FRONTEND] 19:11:17 — notifications.html + notifications-core.js +
  notif-badge.js + notifications.js: nhắc hạn trả (<=3 ngày/quá hạn từ
  borrows/me) + sách SAN_SANG (reservations API thật, mock fallback); ô đếm
  chưa đọc trên menu (localStorage tạm); đánh dấu đã đọc; chỉ reader; test
  15/15 PASS. Chức năng 4, 6 (UC11).
- api.js đã khai báo /api/notifications nhưng Backend CHƯA có → YC-008
  (không khẩn cấp — UI chạy bằng localStorage).

## 9. CẬP NHẬT 2026-08-09 19:17 — Backend UC11 Thông báo

- Log: [BACKEND] 19:16:09 — GET /api/notifications (reader only, 403 với
  librarian/admin): SAP_HET_HAN (<=3 ngày), QUA_HAN, SACH_SAN_SANG; id dạng
  BORROW:/RES:; da_doc=false; phiếu đã trả không nhắc; api_docs 0.8.0;
  test 54/54 PASS. → YC-008 phần GET HOÀN THÀNH.
- Còn để sau: PUT /api/notifications/{id}/read + migration 0008 (bảng ThongBao)
  khi Frontend cần lưu trạng thái đã đọc (hiện dùng localStorage).

## 10. CẬP NHẬT 2026-08-09 19:22 — Chức năng 7 Thống kê (Frontend)

- Log: [FRONTEND] 19:21:47 — stats.html Dashboard 3 nhóm + biểu đồ CSS thuần;
  api.js khai báo /api/stats/top-books, /top-readers, /overdue-books + fieldMap;
  mock fallback + banner; admin+librarian, reader chặn; test 12/12 PASS.
  → Backend CHƯA có /api/stats/* (YC-009).
- Prompt: Frontend/AGENTS.md đổi 19:21:05 (thêm mục LƯU PROMPT bắt buộc) —
  Thư Ký đã đồng bộ PHIÊN BẢN 3 vào promtAI/FRONTEND_AGENT_PROMPT.md (agent
  khai báo đã lưu nhưng thực tế chưa lưu).

## 11. CẬP NHẬT 2026-08-09 19:27 — Backend chức năng 7 Thống kê

- Log: [BACKEND] 19:25:14 — /api/stats/top-books, /top-readers,
  /overdue-books (đếm BorrowDetails/BorrowSlips, overdue chỉ phiếu dang_muon
  quá hạn); admin+librarian, reader 403; api_docs 0.9.0; test 58/58 PASS.
- YC-009 HOÀN THÀNH. Frontend stats.js gọi API thật (mock chỉ khi 404).
- CHECKLIST_UC_THUC_HIEN.md: UC20/UC28 phần thống kê đã xong; xuất báo cáo
  (chức năng 8) còn chờ.

## 12. CẬP NHẬT 2026-08-09 19:32 — Chức năng 8 Xuất CSV (Frontend)

- Log: [FRONTEND] 19:31:59 — 3 nút Xuất CSV (books/borrow/stats.html) +
  downloadFile (fetch → blob → tải file có ngày giờ); api.js khai báo
  exportBooks/exportBorrows/exportReport (/api/export/*.csv); phân quyền
  librarian+admin; test 9/9 PASS → Backend CHƯA có → YC-010.
- Prompt: Frontend/AGENTS.md không đổi (19:21:05) — P.3 trong promtAI vẫn khớp.

## 13. CẬP NHẬT 2026-08-09 19:37 — Backend chức năng 8 + Tổng kết 8 chức năng

- Log: [BACKEND] 19:34:48 — /api/export/books.csv, /borrows.csv, /report.csv
  (BOM UTF-8, escape CSV, filename ngày giờ; admin+librarian, reader 403;
  api_docs 0.10.0; test 62/62 PASS) → YC-010 HOÀN THÀNH.
- Frontend: books.js/borrow.js/stats.js gọi API.downloadFile — đã nối export.
- **TỔNG KẾT: 8/8 chức năng quản lý (mục 3.1) HOÀN THÀNH** — Backend 62/62
  test, Frontend đủ màn hình + nối API (một số phần chưa có log chính thức).
- Còn lại: AI-1/2/3 (AI Engine chưa có code), YC-005 (so_ngay_muon),
  YC-007 (Frontend xác nhận reservations API thật), UI admin cấu hình/audit/backup.

## 14. CẬP NHẬT 2026-08-09 20:00 — admin-config + Thu phạt + DAT_TRUOC (Frontend)

- Log: [FRONTEND] 20:00:07 — admin-config.html/js (cấu hình thư viện UC24,
  cấu hình AI UC26 key che, backup/restore UC27); api.js thêm aiConfig/
  updateAiConfig/updateLibraryConfig/backup/restore/collectFine; borrow.html
  Thu phạt UC19 (mock); requests.html loại DAT_TRUOC; menu Cấu hình chỉ admin;
  test 19/19 PASS.
- Backend: đã có config/library, config/ai, backup, restore; THIẾU collect-fine
  và loai DAT_TRUOC → YC-011.

## 15. CẬP NHẬT 2026-08-09 20:28 — Demo + Thu phạt + Xoá lịch sử yêu cầu

- Log 19:50:00 — seed_demo.py: docgia1/docgia1, docgia2/docgia2, PM001-PM004,
  RV001/RV002; xác minh qua API; test 62/62.
- Log 20:05:33 — UC19 Thu phạt: migration 0008 (FineHistory.da_thu/ngay_thu),
  POST /api/borrows/{ma}/collect-fine, fines trong GET /api/borrows;
  api_docs 0.11.0; test 67/67.
- Log 20:15 — DELETE /api/requests/me/{ma} + DELETE /api/requests/me (chỉ
  yêu cầu DA_DUYET/TU_CHOI); api_docs 0.12.0.
- Server: đã restart (route mới trả 401 thay vì 405).
- Frontend: nối delete requests (20:12-20:14); VẪN mock: danh sách phạt
  (borrow.js) + reservations (YC-007); Backend chưa có DAT_TRUOC (YC-011).

## 16. CẬP NHẬT 2026-08-09 23:19 — SVNET + role tiếng Việt + Sắp xếp (KT2)

- Log 21:52:51 — phạt = TRỪ ĐIỂM SVNET (1 ngày = 2 điểm; migration 0009
  Readers.diem_svnet mặc định 100); collect-fine trừ điểm; test 67/67.
- Log 21:56:59 — role_display tiếng Việt (login/register/accounts); test 68/68.
- Log 23:16:54 — GET /api/books hỗ trợ sort (ten/tacGia/namXb/soLuong) + order;
  api_docs 0.13.0; test 75/75 → KT2 tiêu chí 4 hoàn thành.
- Frontend: dropdown sort (22:40-22:41) nhưng sortBooksBackend còn FALSE
  (YC-012); role_display đã dùng; git/.env.example/README/docs/QA đã có.
- **KT2: 10/10 tiêu chí ĐẠT.**

## 17. CẬP NHẬT 2026-08-10 02:17 — Hồ sơ cá nhân (Profile)

- Log: [BACKEND] 02:15:52 — /api/profile/me (GET/PUT), password, avatar upload
  (PNG/JPG ≤2MB, static/avatars, mount /static); audit UPDATE_PROFILE/
  CHANGE_PASSWORD/UPDATE_AVATAR; api_docs 0.14.0; test 82/82 PASS.
- Frontend (quét): profile.html + profile.js + default-avatar.svg nối API thật;
  sortBooksBackend=true (đóng cảnh báo 13); borrow.js nối danh sách phạt thật
  (đóng phần Frontend UC19).
- Còn lại: reservations mock (YC-012), DAT_TRUOC (YC-011), AI Engine, đóng gói.

## 18. CẬP NHẬT 2026-08-10 03:01 — Validation + Phạt ĐIỂM (0.16.0)

- Log 02:42:50 — Users.email/so_dien_thoai (migration 0010) + app/validation.py
  (ho_ten ≥2 từ, email @ictu.edu.vn, SĐT VN); api_docs 0.15.0; test 86/86.
- Log 02:48:50 + 02:55:00 — backfill email/SĐT, email theo tên người, restart
  server, xác minh live profile.
- Log 02:56:16 — phạt = ĐIỂM (migration 0011: so_diem, overdue_fine_points_
  per_day); FineOut trả so_diem; collect-fine trả so_diem_da_thu; api_docs
  0.16.0; test 86/86; restart + xác minh PM003 = 4 điểm.
- Lệch pha: Frontend fineOut vẫn map so_tien → hiển thị sai → YC-013.

## 19. CẬP NHẬT 2026-08-10 03:07 — Frontend cập nhật phạt ĐIỂM

- Log: [FRONTEND] 03:07:07 — fineOut soDiem/so_diem, collectFineOut
  so_diem_da_thu/diem_con_lai, borrow.js + my-borrows.js hiển thị điểm.
- YC-013 HOÀN THÀNH; cảnh báo 14 đóng; UC19/UC24 khép kín.

## 20. CẬP NHẬT 2026-08-10 04:01 — Phân quyền độc giả 0.17.0

- Log: [BACKEND] 03:59:25 — POST/PUT/DELETE /api/readers chỉ admin; GET
  admin+librarian; thêm PUT /api/readers/{ma}/lock (admin+librarian); audit
  UPDATE_READER_STATUS; api_docs 0.17.0; test 86/86; restart + xác minh live.
- Frontend (quét): nối lockReader; nút Thêm chỉ admin; menu độc giả chỉ
  librarian → YC-014.

## 21. CẬP NHẬT 2026-08-10 04:53 — DAT_TRUOC + menu admin

- Log: [BACKEND] 04:52:00 — loại yêu cầu DAT_TRUOC (migration 0012; POST
  /api/requests chấp nhận ma_sach; approve tạo DatTruoc thật; api_docs 0.19.0;
  test 90/90; restart + xác minh live S005) → YC-011 HOÀN THÀNH.
- Frontend: menu độc giả admin+librarian (04:31:48) → YC-014 HOÀN THÀNH.
- Còn: so_ngay_muon (YC-005/YC-015), reservations mock (YC-007/YC-012 phần 3).

## 22. CẬP NHẬT 2026-08-10 05:48 — Xoá lịch sử đặt trước + Export reservations

- Log 05:13:10 — DELETE /api/reservations/me + /me/{ma_dat} (chỉ HUY/DA_MUON;
  reader; api_docs 0.20.0; test 94/94).
- Log 05:22:45 — GET /api/export/reservations.csv; /api/admin/accounts chỉ tạo
  thủ thư (role reader → 400); api_docs 0.21.0; test 95/95.
- Frontend (quét): 2 nút "Xoá lịch sử đã xử lý" + deleteMyReservation(s);
  admin-accounts chỉ thủ thư.
- CHƯA: bỏ Xuất CSV books/stats (YC-016), disable Gửi yêu cầu (YC-017),
  so_ngay_muon (YC-015), reservations mock (YC-007).

## 23. CẬP NHẬT 2026-08-10 06:45 — so_ngay_muon + UI (0.25.0)

- Backend 0.25.0 (quét, CHƯA có log): so_ngay_muon (migration 0013, approve
  ưu tiên body > yêu cầu > max_borrow_days); bỏ loại "khac" (0014); validation
  tài khoản; export đặt trước chỉ thủ thư; lỗi đăng nhập tiếng Việt.
- Frontend (log 06:45:01 + quét): stats bỏ Xuất CSV ✅; requests.js disable
  nút Gửi ✅ (YC-017); UI admin sạch UC ✅; books.html CÒN Xuất CSV ❌.
- YC-015, YC-017 đóng theo code; chờ log chính thức (YC-018).

## 24. CẬP NHẬT 2026-08-10 06:54 — Đủ log Backend + bỏ toàn bộ Xuất CSV UI

- Backend logs: 05:59:29 (so_ngay_muon, 0.22.0, 100/100), 06:19:53 (validation
  + bỏ khac + export đặt trước chỉ thủ thư, 0.23.0), 06:26:07 (Email DTC,
  0.24.0), 06:32:15 (login tiếng Việt, 0.25.0, 101/101).
- Frontend log 06:54:40: bỏ toàn bộ nút/hàm Xuất CSV (books/stats/borrow/
  reservations); /api/export/* giữ nguyên; books.html căn chỉnh giao diện.
- Chức năng 8: chỉ còn demo qua API, không nút UI. YC-015/016/017/018 đóng.

## 16. BẢNG MINH CHỨNG CHUẨN (prompt → phản hồi → chỉnh sửa → kiểm chứng)

### Minh chứng 1 — Frontend màn hình quản lý độc giả (UC14)
- **Prompt gốc:** "Frontend Agent — Vòng 3 (chức năng 3 — Quản lý độc giả): tạo readers.html, danh sách + tìm, thêm/sửa/khoá thẻ, xoá chỉ admin; nối /api/readers..."
- **Phản hồi AI:** sinh `readers.html`, `js/readers.js`, cập nhật `api.js` (endpoints + fieldMap).
- **Phần dùng nguyên:** cấu trúc trang, hàm load/search, mapping field.
- **Phần đã chỉnh sửa:** menu thêm role theo data-roles; xử lý thông báo lỗi; thêm query tìm kiếm.
- **Nhận xét kiểm chứng:** đăng nhập admin/librarian/reader, test API 16/16, phân quyền đúng.

### Minh chứng 2 — Backend chức năng 3 (UC14)
- **Prompt gốc:** "Backend Agent — chức năng 3: migration 0004 bảng Readers, CRUD /api/readers, ràng buộc loại/thẻ, audit log, test..."
- **Phản hồi AI:** sinh `readers.py`, `models.Reader`, `schemas.Reader*`, migration 0004, `test_readers.py`.
- **Phần dùng nguyên:** toàn bộ CRUD + constraint (email unique, loai/trangThai).
- **Phần đã chỉnh sửa:** phân quyền DELETE chỉ admin; lọc tìm theo mã/tên.
- **Nhận xét kiểm chứng:** 9/9 PASS, xác minh qua API login + CRUD.

### Minh chứng 3 — Backend chức năng 4 (UC15/16/17/19)
- **Prompt gốc:** "Backend Agent — chức năng 4: migration 0005 BorrowSlips/BorrowDetails/FineHistory; POST /api/borrows; return tự tính phạt; renew tối đa 1 lần; test..."
- **Phản hồi AI:** sinh `borrows.py` (~9 KB), models 3 bảng, schemas, test 10 case.
- **Phần dùng nguyên:** luồng lập phiếu, giảm/tăng số lượng, công thức phạt, giới hạn gia hạn.
- **Phần đã chỉnh sửa:** thêm kiểm tra thẻ khoá; `so_lan_gia_han`; sau này bổ sung thu phạt (migration 0008).
- **Nhận xét kiểm chứng:** 19/19 → 67/67 PASS; mượn khi sách hết → lỗi; trả trễ → phạt đúng; gia hạn quá 1 lần → lỗi.

### Minh chứng 4 — Đợt A tương thích Use Case
- **Prompt gốc:** "Backend Agent — Đợt A: migration 0006 (TheLoai, Nxb, YeuCau, Users.reader_id), register, borrows/me, requests + approve/reject, admin accounts/categories/publishers/restore..."
- **Phản hồi AI:** sinh `auth.register`, `requests.py`, `accounts.py`, `catalog.py`, migration 0006, `test_uc_compat.py`.
- **Phần dùng nguyên:** toàn bộ API mới + liên kết Users↔Readers.
- **Phần đã chỉnh sửa:** theo quyết định người dùng — admin KHÔNG thao tác mượn/trả (403); chỉnh quyền approve/reject về librarian.
- **Nhận xét kiểm chứng:** 38/38 PASS; xác minh qua API admin 403, librarian 200.

### Minh chứng 5 — Frontend + Backend đặt trước (UC06/18)
- **Prompt gốc:** "Frontend — Bước 1 đặt trước: nút Đặt trước khi sách hết, trang reservations, config chờ /api/reservations..." và "Backend — Bước 2: migration 0007 DatTruoc, GET/POST /api/reservations, cancel/fulfill, trả sách → SAN_SANG, gia hạn từ chối nếu có đặt trước..."
- **Phản hồi AI:** Frontend sinh `reservations.html/js/reservation-mock.js`; Backend sinh `reservations.py`, migration 0007, `test_reservations.py`.
- **Phần dùng nguyên:** contract API, trạng thái CHO_XU_LY/SAN_SANG/DA_MUON/HUY, tích hợp trả sách.
- **Phần đã chỉnh sửa:** filtered unique index chống đặt trùng; admin 403.
- **Nhận xét kiểm chứng:** 50/50 PASS; xác minh qua API (đặt khi còn → lỗi, đặt trùng → lỗi, trả → SAN_SANG).

## 28. CẬP NHẬT 2026-08-31 — Hoàn thiện Kiểm thử Unit Test (KTR2)

- Backend: Sửa lỗi logic xóa sách (xóa BookCopies trước khi xóa Book) tránh lỗi IntegrityError.
- Backend: Sửa test _set_book_stock đổi từ xóa sạch sang thêm mới BookCopies để không làm đứt gãy tham chiếu BorrowDetails trong các bài test khác.
- Backend: Sửa lỗi UnboundLocalError trong 
equests.py do import BorrowSlip trùng lặp trong nội bộ hàm.
- Backend: Sửa logic trong endpoint kiểm tra thông báo đặt trước, đổi cách giả lập sang gọi API thật để tự động gắn copy_id.
- Kết quả: Toàn bộ 111/111 unit tests PASS hoàn toàn. Hệ thống đáp ứng mọi yêu cầu vẹn toàn dữ liệu và luồng nghiệp vụ.
