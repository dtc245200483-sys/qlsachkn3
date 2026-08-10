# Báo cáo lỗi — QA

Cập nhật: 2026-08-10 (đợt rà soát lại sau Backend 0.25.0 + Frontend cập nhật).
Mức độ: Nhẹ / Vừa / Nghiêm trọng.

## Tổng quan trạng thái

| Mã | Mô tả ngắn | Trạng thái 2026-08-10 |
|---|---|---|
| BUG-001 | Yêu cầu "Đặt trước sách" (DAT_TRUOC) 422 | ✅ ĐÃ SỬA (Backend hỗ trợ DAT_TRUOC); còn comment cũ trong `requests.js` |
| BUG-002 | "Số ngày mượn" bị bỏ qua | ⚠️ SỬA MỘT PHẦN: đã fix cho luồng Yêu cầu (`so_ngay_muon`); **vẫn lỗi ở trang Mượn/Trả trực tiếp `borrow.html`** |
| BUG-003 | Lọc "Đang mượn" bỏ sót sách còn tồn nhưng đang mượn | ❌ CHƯA SỬA (`search.js` vẫn lọc client-side sai) |
| BUG-004 | Danh sách phạt mock ở `borrow.html` | ✅ ĐÃ SỬA (lấy phạt thật từ `GET /api/borrows`) |
| BUG-005 | Thông báo không dùng `GET /api/notifications` | ❌ CHƯA SỬA (`notifications-core.js` vẫn tự tổng hợp) |
| BUG-006 | Comment/ghi chú Frontend lỗi thời | ❌ CHƯA SỬA (api.js/search.js/requests.js/borrow.js...) |
| BUG-007 | Test gốc `test_stats.py` không cô lập dữ liệu | ❌ CHƯA SỬA (DB sạch 101/101; DB có dữ liệu 100/101) |
| BUG-008 | Menu admin thiếu "Quản lý sách" | ⚠️ SỬA MỘT PHẦN: "Quản lý độc giả" đã cho admin; **menu "Quản lý sách" vẫn ẩn với admin** |
| BUG-009 | Lọc "Hết sách" gửi `trangThai=het` → Backend 422 | ❌ MỚI, CHƯA SỬA |
| BUG-010 | Nút "Gửi yêu cầu" không disable dù chưa chọn sách | ❌ MỚI, CHƯA SỬA (YC-017 chưa hoạt động) |
| BUG-011 | `admin-config.js` chỉ gắn listener form thư viện; AI config + Sao lưu + Phục hồi bấm không chạy | ❌ MỚI, CHƯA SỬA |
| BUG-012 | `profile.html` còn option loại "Khác" (Backend chỉ nhận sinh_vien/giang_vien) | ❌ MỚI, CHƯA SỬA |
| BUG-013 | Librarian thấy nút "Xoá" lịch sử đặt trước nhưng Backend chỉ cho reader | ❌ MỚI, CHƯA SỬA |
| BUG-014 | `reservation-mock.js` chưa xoá, vẫn load ở 6 trang dù log YC-007 nói đã xoá | ❌ MỚI, CHƯA SỬA |
| BUG-015 | `conftest.py` Backend xoá Readers theo `DTC100%` trước Users → vỡ FK khi DB có seed dùng dải này | ❌ MỚI, CHƯA SỬA (test không cô lập) |
| BUG-016 | Tài liệu README còn đoạn cũ: phạt tiền, loại "khac", "chưa có API đăng ký", export reservations cho admin | ❌ MỚI, CHƯA SỬA (chỉ tài liệu) |
| AI-1/2/3 | Chatbot/tóm tắt/gợi ý AI chưa triển khai (AI_Engine chỉ có prompt) | ❌ CHƯA TRIỂN KHAI (không phải bug chạy sai) |

---

## Chi tiết các lỗi còn mở (2026-08-10)

### BUG-002 (một phần) — `borrow.html` vẫn gửi `so_ngay_muon` nhưng Backend bỏ qua

- **Mô tả:** `js/borrow.js` vẫn đưa `so_ngay_muon` vào `POST /api/borrows`, nhưng schema `BorrowCreate` không có field này → hạn trả luôn = `max_borrow_days` (14). Luồng Yêu cầu (`requests`) đã được Backend hỗ trợ `so_ngay_muon`.
- **Bằng chứng:** Test QA `test_borrow_extra_so_ngay_muon_ignored` — gửi `so_ngay_muon=3`, hạn trả thực tế 14 ngày.
- **Bước tái hiện:** Librarian mở `borrow.html` → nhập "Số ngày mượn = 3" → lập phiếu → xem hạn trả.
- **Kết quả mong đợi:** Hạn trả = ngày mượn + 3 (hoặc ẩn ô nhập nếu chưa hỗ trợ).
- **Kết quả thực tế:** Hạn trả luôn 14 ngày.
- **Mức độ:** Vừa. **Agent cần sửa:** Backend (`BorrowCreate` + `create_borrow`) hoặc Frontend (`borrow.js`).

### BUG-003 — Lọc "Đang mượn" ở `search.html` sai

- **Mô tả:** `search.js` vẫn chạy `clientFilter` với điều kiện `trangThai=dang_muon → soLuong <= 0`, loại bỏ sách còn tồn nhưng đang có phiếu mượn dở (Backend trả đúng).
- **Bằng chứng:** `GET /api/books?trangThai=dang_muon` trả sách stock>0; `clientFilter` sẽ lọc mất.
- **Mức độ:** Vừa. **Agent cần sửa:** Frontend (`search.js` — bỏ lọc trùng hoặc sửa điều kiện).

### BUG-005 — Thông báo chưa dùng `GET /api/notifications`

- **Mô tả:** `notifications-core.js` tự tính từ `myBorrows` + `reservations`; endpoint chính thức đã có.
- **Mức độ:** Nhẹ. **Agent cần sửa:** Frontend (`notifications-core.js`, `notifications.js`, `notif-badge.js`).

### BUG-006 — Comment lỗi thời

- **Mô tả:** `api.js` (header "0.6.0", lockReader "Backend chưa có", deleteMyReservation "config chờ", notifications/stats/export/collectFine/deleteMyRequest/profile "chưa có API"), `search.js` (Backend chưa hỗ trợ q/theLoai/trangThai), `requests.js` (Backend chưa lưu so_ngay_muon/chưa hỗ trợ DAT_TRUOC), `borrow.js` (Backend 0.6.0 chưa hỗ trợ so_ngay_muon), `readers.js`/`profile.js` (LOAI_LABEL còn "khac").
- **Mức độ:** Nhẹ. **Agent cần sửa:** Frontend.

### BUG-007 — `Backend/tests/test_stats.py` không cô lập dữ liệu

- **Mô tả:** `test_top_books_order_and_limit` giả định `TESTSTT2` nằm trong top-10. Chạy trên DB có ≥10 sách có lượt mượn → `KeyError`.
- **Bằng chứng:** DB sạch: **101/101 PASS**; DB đã có dữ liệu QA: **100/101**, fail đúng `KeyError: 'TESTSTT2'`.
- **Mức độ:** Vừa (chất lượng test). **Agent cần sửa:** Backend (test — lọc theo prefix hoặc dùng DB riêng/transaction).

### BUG-008 (một phần) — Admin không thấy menu "Quản lý sách"

- **Mô tả:** Tất cả nav đặt `books.html` với `data-roles="librarian"`; admin phải gõ URL. Nút "+ Thêm sách" trong trang lại cho `librarian,admin` → không nhất quán.
- **Mức độ:** Nhẹ. **Agent cần sửa:** Frontend (đổi nav `data-roles="librarian,admin"`).

### BUG-009 — Lọc "Hết sách" hỏng

- **Mô tả:** `search.html` có `<option value="het">Hết sách</option>`; `search.js` gửi `trangThai=het` nhưng Backend chỉ nhận `con`/`dang_muon` → 422 và hiện lỗi, không có kết quả.
- **Bằng chứng:** Test QA `test_filter_invalid_status` (trangThai=het → 422).
- **Mức độ:** Vừa. **Agent cần sửa:** Frontend (`search.html`/`search.js` — đổi value thành `dang_muon` hoặc lọc client-side cho "hết sách").

### BUG-010 — Nút "Gửi yêu cầu" luôn bật

- **Mô tả:** `requests.js` `updateSubmitState()` tính `valid` nhưng cuối hàm vẫn `btn.disabled = false` → YC-017 (disable tới khi có ≥1 dòng sách hợp lệ) không hoạt động.
- **Mức độ:** Nhẹ–Vừa. **Agent cần sửa:** Frontend (`requests.js` — `btn.disabled = !valid`).

### BUG-011 — Trang Cấu hình: nút AI / Sao lưu / Phục hồi chết

- **Mô tả:** `admin-config.js` định nghĩa `loadAiConfig`, `saveAiConfig`, `backupDatabase`, `restoreDatabase` nhưng `init()` chỉ gắn `library-config-form`; các nút còn lại không có listener → bấm không phản hồi.
- **Bước tái hiện:** Admin vào `admin-config.html` → sửa model AI → Lưu → không có gì xảy ra; bấm "Sao lưu CSDL"/"Phục hồi CSDL" cũng không chạy.
- **Mức độ:** Vừa. **Agent cần sửa:** Frontend (`admin-config.js`).

### BUG-012 — `profile.html` còn option loại "Khác"

- **Mô tả:** Backend sau migration 0014 chỉ chấp nhận `sinh_vien`/`giang_vien`; `profile.html` vẫn có `<option value="khac">Khác</option>` → reader chọn sẽ nhận 422. `readers.js`/`profile.js` còn nhãn hiển thị "Khác".
- **Mức độ:** Nhẹ. **Agent cần sửa:** Frontend (`profile.html`, label trong `readers.js`/`profile.js`).

### BUG-013 — Librarian thấy nút Xoá lịch sử đặt trước nhưng Backend từ chối

- **Mô tả:** `reservations.js` render nút "Xoá"/"Xoá lịch sử" cho librarian, gọi `DELETE /api/reservations/me/{id}` và `/me` — Backend chỉ cho role `reader` → librarian nhận 403.
- **Bước tái hiện:** Librarian mở `reservations.html` → có phiếu HUY/DA_MUON → bấm Xoá → lỗi 403.
- **Mức độ:** Vừa. **Agent cần sửa:** Frontend (ẩn nút với librarian) hoặc Backend (mở quyền cho librarian nếu yêu cầu).

### BUG-014 — `reservation-mock.js` chưa xoá

- **Mô tả:** Log Frontend YC-007 ghi "xoá file js/reservation-mock.js" nhưng file vẫn tồn tại và 6 trang (`search`, `requests`, `reservations`, `notifications`, `profile`, `my-borrows`) vẫn include. Không gây lỗi chạy (code đã chuyển sang API trực tiếp) nhưng là code chết + sai lệch log.
- **Mức độ:** Nhẹ. **Agent cần sửa:** Frontend (xoá file + bỏ thẻ script).

### BUG-015 — `Backend/tests/conftest.py` dọn dữ liệu không an toàn với DB có sẵn

- **Mô tả:** Cleanup xoá `Readers WHERE ma LIKE 'TEST%' OR email LIKE 'DTC100%@ictu.edu.vn'` trước khi xoá `Users` → vỡ FK `fk_users_reader` nếu DB có reader seed dùng email `DTC100...` và có tài khoản liên kết. Helper `next_test_email()` cũng dùng dải `DTC100000001+`, dễ đụng dữ liệu khác.
- **Bằng chứng:** Chạy `test_stats.py` sau khi seed QA dùng email `DTC100...` → 4 lỗi setup `IntegrityError` (sau khi QA đổi sang `DTC90x` thì hết).
- **Mức độ:** Vừa (chất lượng test). **Agent cần sửa:** Backend (`tests/conftest.py`/`tests/helpers.py` — đổi namespace email hiếm, xoá Users trước Readers).

### BUG-016 — README còn nội dung cũ

- **Mô tả:** README vẫn có đoạn "Phạt: so_tien = ...", "loại độc giả .../khac", "chỉ có API đăng nhập, chưa có API đăng ký", "export reservations cho librarian/admin" (code/api_docs: chỉ librarian). api_docs/README mâu thuẫn về quyền export đặt trước.
- **Mức độ:** Nhẹ (tài liệu). **Agent cần sửa:** Backend (README).

### AI-1/2/3 — chưa triển khai

- **Mô tả:** `AI_Engine` chỉ có `AI.txt` (prompt); Backend chưa có `/ai/search`, `/ai/summarize`, `/ai/recommend`; Frontend chưa có màn hình AI. Không thể chạy 3 test bắt buộc (câu hỏi mơ hồ / sách không tồn tại / sách hết) và các test giới hạn AI (timeout, rate limit, response sai định dạng).
- **Mức độ:** Nghiêm trọng đối với đề bài mục 3.2/4. **Agent cần sửa:** AI Engine + Backend + Frontend.

---

## Đã xác nhận sửa (đợt này)

- BUG-001: Backend hỗ trợ `loai=DAT_TRUOC` trong `/api/requests` + duyệt tạo đặt trước thật. (Test QA `test_dat_truoc_request_and_approve` pass.)
- BUG-004: `borrow.js` hiển thị phạt thật từ API; thu phạt trừ điểm SVNET.
- BUG-002 (luồng yêu cầu): `so_ngay_muon` được lưu và áp dụng khi duyệt.
- BUG-008 (độc giả): nav `readers.html` cho admin.
