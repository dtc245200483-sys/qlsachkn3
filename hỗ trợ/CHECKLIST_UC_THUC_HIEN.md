# Checklist triển khai theo Use Case (UC01-UC28) — cập nhật 2026-08-09

> Lõi = đúng đề tài (8 chức năng quản lý + 3 chức năng AI). Mở rộng = ngoài đề bài, làm sau khi đủ lõi.

| UC | Use Case | Actor | Backend | Frontend | Trạng thái |
|---|---|---|---|---|---|
| UC01 | Đăng ký / Đăng nhập | Độc giả | Đăng nhập ✅; đăng ký ❌ | Đăng nhập ✅; đăng ký ❌ | ⚠️ Đợt A |
| UC02 | Tra cứu sách thường | Độc giả | ✅ books q/theLoai/trangThai | ✅ search.html | ✅ |
| UC03 | Tra cứu bằng Chatbot AI | Độc giả | ❌ | ❌ | ⏳ Đợt D (lõi AI-1) |
| UC04 | Xem tóm tắt sách AI | Độc giả | ❌ | ❌ | ⏳ Đợt D (lõi AI-2) |
| UC05 | Gợi ý sách liên quan AI | Độc giả | ❌ | ❌ | ⏳ Đợt D (lõi AI-3) |
| UC06 | Đặt mượn trước | Độc giả | ❌ | ❌ | ⏳ Đợt C (lõi chức năng 6) |
| UC07 | Yêu cầu mượn sách | Độc giả | ✅ + xoá lịch sử (20:15) | ✅ requests.html | ✅ |
| UC08 | Yêu cầu trả sách | Độc giả | ✅ + xoá lịch sử (20:15) | ✅ requests.html | ✅ |
| UC09 | Gia hạn mượn | Độc giả | ✅ + xoá lịch sử (20:15) | ✅ requests.html | ✅ |
| UC10 | Xem lịch sử mượn/trả & phạt | Độc giả | ❌ borrows/me | ❌ | ⏳ Đợt A (mở rộng) |
| UC11 | Nhận thông báo | Độc giả | ✅ (19:16:09) | ✅ notifications.html | ✅ |
| UC12 | Đăng nhập quyền thủ thư | Thủ thư | ✅ | ✅ | ✅ |
| UC13 | Quản lý sách CRUD | Thủ thư | ✅ | ✅ books.html | ✅ |
| UC14 | Quản lý độc giả | Thủ thư | ✅ | ✅ readers.html | ✅ |
| UC15 | Xử lý phiếu mượn | Thủ thư | ✅ (chỉ librarian) | ✅ borrow.html | ✅ |
| UC16 | Xử lý phiếu trả | Thủ thư | ✅ | ✅ borrow.html | ✅ |
| UC17 | Xử lý gia hạn | Thủ thư | ✅ (cần thêm: từ chối nếu có đặt trước) | ✅ | ⚠️ bổ sung cùng Đợt C |
| UC18 | Xử lý đặt trước | Thủ thư | ❌ | ❌ | ⏳ Đợt C (lõi chức năng 6) |
| UC19 | Tính & thu phạt quá hạn | Thủ thư | ✅ (20:05:33, collect-fine) | ✅ nút thu; ⚠️ danh sách phạt còn mock | ✅ phần lớn; chờ Frontend nối list thật |
| UC20 | Thống kê & xuất báo cáo | Thủ thư | ✅ (19:34:48) | ✅ stats.html + nút Xuất CSV | ✅ HOÀN THÀNH |
| UC21 | Kiểm duyệt nội dung AI | Thủ thư | ❌ | ❌ | 🟡 tuỳ chọn, Đợt D |
| UC22 | Đăng nhập quyền admin | Admin | ✅ | ✅ | ✅ |
| UC23 | Quản lý tài khoản & phân quyền | Admin | ❌ đã xoá — khôi phục + mở rộng | ❌ | ⏳ Đợt A (mở rộng — đã chốt giữ) |
| UC24 | Cấu hình quy định mượn/trả | Admin | ✅ | ✅ admin-config.html | ✅ |
| UC25 | Quản lý danh mục thể loại/NXB | Admin | ❌ | ❌ | ⏳ Đợt A (mở rộng) |
| UC26 | Cấu hình & giám sát AI | Admin | ✅ config/ai; ❌ giám sát | ✅ admin-config.html (key che) | ✅ cấu hình; ⏳ giám sát (Đợt D) |
| UC27 | Sao lưu & phục hồi | Admin | ✅ backup + restore | ✅ admin-config.html (hiện .bak) | ✅ |
| UC28 | Báo cáo tổng hợp | Admin | ✅ (19:34:48) | ✅ stats.html + nút Xuất CSV | ✅ HOÀN THÀNH |

## Kết luận

- Nếu hoàn thành đủ bảng trên: Frontend + Backend khớp 100% tài liệu Actor & Use Case.
- Nếu chỉ tính "đúng đề tài": phần LÕI (8 + 3) đủ là ăn điểm — các ô "mở rộng" làm sau.
- Đang ở: Backend Đợt A (UC01, UC07-10, UC23, UC25, UC27) → Frontend Đợt B → Đợt C → Đợt D (AI).

## CẬP NHẬT 2026-08-09 18:30 — Sau khi hoàn thành Đợt A + Đợt B

### ĐÃ CÓ

- Frontend (12 trang): index (login), register, search, books, readers, borrow, my-borrows (xem + xoá lịch sử), requests (gửi yêu cầu + duyệt), admin-accounts, admin-catalog.
- Backend (8 router): auth (login/register), books (CRUD + tìm/lọc), readers, borrows (mượn/trả/gia hạn/list + me + xoá lịch sử), requests (gửi/duyệt/từ chối), accounts (admin), catalog (thể loại/NXB), admin (config/audit/backup/restore).
- Migration 0001-0006; test 43/43 PASS; api_docs 0.6.0; README.
- Phân quyền đúng: mượn/trả CHỈ librarian; admin không thấy menu Mượn/Trả, bị 403 API; reader chỉ thấy dữ liệu của mình.

### CÒN THIẾU (theo thứ tự làm tiếp)

| Bước | Việc | UC / Chức năng | Ghi chú |
|---|---|---|---|
| 1 | Đặt trước sách (Frontend — theo quy trình tuần tự Frontend trước) | UC06/18 — lõi chức năng 6 | Nút Đặt trước khi sách hết; trang reader xem/huỷ; trang thủ thư xử lý (mock + config chờ) |
| 2 | Đặt trước sách (Backend) | UC06/18 | Bảng DatTruoc + API đặt/huỷ/xử lý; trả sách ưu tiên người đặt trước; gia hạn từ chối nếu có đặt trước |
| 3 | Thông báo | UC11 (mở rộng) | Nhắc hạn trả, sách đặt trước đã có (tối giản) |
| 4 | Thống kê (Backend) | UC20 — lõi chức năng 7 | ✅ ĐÃ XONG (19:25:14, /api/stats/*, 58/58) |
| 5 | Dashboard thống kê (Frontend) | UC20/28 | ✅ ĐÃ XONG (19:21:47, stats.html, đã nối API thật) |
| 6 | Xuất danh sách/báo cáo (Backend) | UC20 — lõi chức năng 8 | ✅ ĐÃ XONG (19:34:48, /api/export/*.csv, 62/62) |
| 7 | Nút xuất (Frontend) | UC20/28 | ✅ ĐÃ XONG (19:31:59, books/borrow/stats + downloadFile) |
| 8 | UI thu phạt + UI admin cấu hình thư viện/AI + UI restore + dữ liệu mẫu độc giả/phiếu mượn | UC19/24/26/27 | Hoàn thiện UI quản trị còn thiếu + demo |
| 9 | AI-1/2/3 + kiểm duyệt + giám sát | UC03/04/05/21/26 — lõi 3 chức năng AI | Đợt D |
| 10 | Tài liệu KT1 + .env.example + git + minh chứng AI | Tiêu chí KT1/KT2 | SRS, ERD, kiến trúc, nhật ký prompt |

## Đối chiếu 28 UC với hiện trạng + bước kế hoạch

| UC | Tên | Trạng thái / Bước |
|---|---|---|
| UC01 | Đăng ký / Đăng nhập | ✅ register.html + /api/auth/register |
| UC02 | Tra cứu sách thường | ✅ search.html + books query |
| UC03 | Tra cứu bằng Chatbot AI | ⏳ Bước 9 (Đợt D) |
| UC04 | Xem tóm tắt sách AI | ⏳ Bước 9 (Đợt D) |
| UC05 | Gợi ý sách liên quan AI | ⏳ Bước 9 (Đợt D) |
| UC06 | Đặt mượn trước | ✅ reservations + DAT_TRUOC UI (chờ Backend hỗ trợ DAT_TRUOC) |
| UC07 | Yêu cầu mượn sách | ✅ requests.html + /api/requests + xoá lịch sử (20:15) |
| UC08 | Yêu cầu trả sách | ✅ requests.html + xoá lịch sử (20:15) |
| UC09 | Gia hạn mượn | ✅ requests.html + thủ thư gia hạn + xoá lịch sử (20:15) |
| UC10 | Xem lịch sử mượn/trả & phạt | ✅ my-borrows.html + /api/borrows/me |
| UC11 | Nhận thông báo | ✅ notifications.html + /api/notifications (19:16:09) |
| UC12 | Đăng nhập quyền thủ thư | ✅ |
| UC13 | Quản lý sách CRUD | ✅ books.html |
| UC14 | Quản lý độc giả | ✅ readers.html |
| UC15 | Xử lý phiếu mượn | ✅ borrow.html (chỉ librarian) |
| UC16 | Xử lý phiếu trả | ✅ borrow.html |
| UC17 | Xử lý gia hạn | ✅ borrow.html + requests |
| UC18 | Xử lý đặt trước | ✅ /api/reservations + UI (19:02:38) |
| UC19 | Tính & thu phạt quá hạn | ✅ thu phạt (20:05:33); ⏳ Frontend nối danh sách phạt thật |
| UC20 | Thống kê & xuất báo cáo | ✅ HOÀN THÀNH (stats + /api/export/*) |
| UC21 | Kiểm duyệt nội dung AI | 🟡 tuỳ chọn, Bước 9 |
| UC22 | Đăng nhập quyền admin | ✅ |
| UC23 | Quản lý tài khoản & phân quyền | ✅ admin-accounts.html + /api/admin/accounts |
| UC24 | Cấu hình quy định mượn/trả | ✅ admin-config.html (20:00:07) |
| UC25 | Quản lý danh mục thể loại/NXB | ✅ admin-catalog.html |
| UC26 | Cấu hình & giám sát AI | ✅ admin-config.html key che; ⏳ giám sát Đợt D |
| UC27 | Sao lưu & phục hồi | ✅ admin-config.html + backup/restore |
| UC28 | Báo cáo tổng hợp | ✅ HOÀN THÀNH (stats.html + /api/export/*) |

**Kết luận:** làm xong Bước 1-10 là phủ 100% 28 UC — phần lõi 8+3 nằm trong các bước 1, 2, 4-7, 9; phần mở rộng xen kẽ (UC11, UC21, UC23, UC25, UC28).

## CẬP NHẬT TỐI 2026-08-09 — Sau khi xong 8 chức năng quản lý

### ĐÃ CÓ (code hoạt động, test 62/62)

- Backend 12 router: auth, books, readers, borrows, requests, reservations, notifications, stats, export, accounts, catalog, admin.
- Frontend 13 trang: login, register, search, books, readers, borrow, my-borrows, requests, reservations, notifications, stats, admin-accounts, admin-catalog.
- Migration 0001-0007; api_docs 0.10.0; script seed_demo.py (đã chạy — hiện có 1 độc giả, 1 phiếu, 1 đặt trước; nên chạy lại cho đủ 3/4/2).
- 25/28 UC có code: UC01, 02, 06-20 (trừ UI thu phạt UC19), 22-28 (Backend); AI (UC03/04/05) và UC21 chưa.

### CÒN THIẾU (theo ý 1-4 người dùng chốt)

1. Dữ liệu mẫu đầy đủ: chạy lại `python scripts/seed_demo.py --verify` → 3 độc giả, 4 phiếu (1 trễ có phạt), 2 đặt trước; overdue-books > 0.
2. UI admin còn thiếu: trang cấu hình thư viện (UC24) + cấu hình AI (UC26) + nút backup/restore (UC27) — Backend đã có API.
3. Hồ sơ: .env.example ❌, git repo ❌, tài liệu KT1 (SRS/ERD/kiến trúc/phi chức năng) ❌; minh chứng AI đã có promtAI/MINH_CHUNG_AI_FRONTEND_BACKEND.md ✅.
4. AI-1/2/3 + kiểm duyệt/giám sát (UC03/04/05/21/26): chưa có code AI (chỉ AI.txt).

## CẬP NHẬT 2026-08-09 19:27 — UC20/UC28 phần thống kê ĐÃ XONG

- Backend: log 19:25:14 — /api/stats/top-books, /top-readers, /overdue-books
  (admin+librarian, reader 403; api_docs 0.9.0; test 58/58 PASS).
- Frontend: stats.html + stats.js (log 19:21:47, test 12/12) — gọi API thật,
  mock fallback chỉ khi API 404.
- Còn lại trong UC20/UC28: XUẤT BÁO CÁO (chức năng 8) — Bước 6-7.

## CẬP NHẬT 2026-08-09 19:37 — 8/8 CHỨC NĂNG QUẢN LÝ HOÀN THÀNH

- Backend: log 19:34:48 — /api/export/books.csv, /borrows.csv, /report.csv
  (BOM UTF-8, escape CSV, filename ngày giờ; admin+librarian, reader 403;
  api_docs 0.10.0; test 62/62 PASS).
- Frontend: nút Xuất CSV ở books/borrow/stats.html gọi API.downloadFile
  (log 19:31:59, test 9/9) — đã nối /api/export/*.
- KẾT LUẬN: 8/8 chức năng quản lý (mục 3.1 đề bài) đã HOÀN THÀNH phần
  Backend + Frontend (còn chờ: log chính thức Frontend cho vài phần, AI Engine,
  UI admin cấu hình/audit/backup nếu chưa đủ).

## CẬP NHẬT 2026-08-09 20:28 — Ý 1 + Ý 2 hoàn thành, cập nhật UC

- Ý 1: dữ liệu mẫu DEMO — seed_demo.py (19:50:00): docgia1/docgia1, docgia2/
  docgia2, PM001-PM004, RV001/RV002.
- Ý 2: admin-config (19:53-20:00) + Thu phạt UC19 (20:05:33, migration 0008,
  67/67) + xoá lịch sử yêu cầu (20:15, api_docs 0.12.0).
- UC19/24/26/27 + UC07/08/09/11/18: đã xong (xem bảng trên).
- CÒN LẠI: DAT_TRUOC Backend, Frontend nối danh sách phạt thật + bỏ mock
  reservations (YC-007), AI-1/2/3 + kiểm duyệt/giám sát AI (Đợt D), tài liệu
  KT1/KT2 + git + minh chứng (Bước 10) — tương ứng Ý 3, Ý 4.
