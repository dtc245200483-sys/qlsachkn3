# Báo cáo lỗi — QA

Cập nhật: 2026-08-10 (đã sửa theo yêu cầu người dùng, trừ AI).

## Trạng thái cuối

| Mã | Mô tả | Trạng thái |
|---|---|---|
| BUG-001 | Yêu cầu "Đặt trước sách" (DAT_TRUOC) 422 | ✅ Đã sửa (Backend hỗ trợ DAT_TRUOC) |
| BUG-002 | "Số ngày mượn" bị bỏ qua | ✅ Đã sửa: `BorrowCreate` + `POST /api/borrows` nhận `so_ngay_muon` (1–max, vượt → 400); `borrow.html` áp dụng đúng |
| BUG-003 | Lọc "Đang mượn" bỏ sót sách còn tồn đang mượn | ✅ Đã sửa: `search.js` tin Backend, chỉ lọc client-side cho "het" |
| BUG-004 | Danh sách phạt mock ở borrow.html | ✅ Đã sửa (dữ liệu thật từ API) |
| BUG-005 | Thông báo không dùng `/api/notifications` | ✅ Đã sửa: `notifications-core.js` gọi `GET /api/notifications` |
| BUG-006 | Comment lỗi thời | ✅ Đã sửa: dọn comment trong api.js/search.js/requests.js/borrow.js + nhãn "khac" |
| BUG-007 | `test_stats.py` không cô lập dữ liệu | ✅ Đã sửa: lọc theo prefix TEST, không phụ thuộc DB trống |
| BUG-008 | Admin không thấy menu "Quản lý sách" | ✅ Đã sửa: nav `data-roles="librarian,admin"` ở 15 trang |
| BUG-009 | Lọc "Hết sách" gửi `trangThai=het` → 422 | ✅ Đã sửa: "het" lấy tất cả + lọc client-side |
| BUG-010 | Nút "Gửi yêu cầu" không disable | ✅ Đã sửa: `btn.disabled = !valid` |
| BUG-011 | admin-config: AI/backup/restore không chạy | ✅ Đã sửa: gắn listener + `loadAiConfig()` |
| BUG-012 | profile còn option "Khác" | ✅ Đã sửa: bỏ option + nhãn khac |
| BUG-013 | Librarian không xoá được lịch sử đặt trước | ✅ Đã sửa: Backend cho librarian (reader: của mình; librarian: mọi phiếu) |
| BUG-014 | `reservation-mock.js` chưa xoá | ✅ Đã sửa: xoá file + bỏ thẻ script ở 6 trang |
| BUG-015 | conftest dọn dữ liệu không an toàn | ✅ Đã sửa: email test `DTC700...`, xoá Users trước Readers, pattern đồng bộ |
| BUG-016 | README nội dung cũ | ✅ Đã sửa: phạt điểm, bỏ "khac", đăng ký, export reservations chỉ librarian |
| AI-1/2/3 | Chatbot/tóm tắt/gợi ý AI | ⏸️ Chưa triển khai — người dùng yêu cầu chưa cần sửa |

## Chi tiết thay đổi chính

- **Backend**
  - `app/schemas.py`: `BorrowCreate` thêm `so_ngay_muon` (1–365).
  - `app/routers/borrows.py`: `create_borrow` truyền `so_ngay_muon`; vượt `max_borrow_days` → 400.
  - `app/routers/reservations.py`: `DELETE /api/reservations/me/{ma_dat}` và `/me` cho `reader` (phiếu của mình) + `librarian` (mọi phiếu); guard `reader_id` chỉ áp dụng cho reader.
  - `tests/conftest.py`: email test `DTC700...`, xoá Users trước Readers, pattern `DatTruoc` đồng bộ.
  - `tests/helpers.py`: `next_test_email()` dùng dải `DTC7001000001+`.
  - `tests/test_stats.py`: top-books kiểm tra theo prefix TEST thay vì giả định DB trống.
  - `tests/test_reservations.py`: cập nhật kỳ vọng librarian được xoá lịch sử.
  - `README.md` + `api_docs.md`: cập nhật phạt điểm, `so_ngay_muon`, quyền export/xoá đặt trước.
- **Frontend**
  - `js/api.js`: bỏ comment "Backend chưa có API" cũ; header 0.25.0.
  - `js/search.js`: `het` lọc client-side; `con`/`dang_muon` tin Backend.
  - `js/requests.js`: nút Gửi disable đúng lúc; bỏ thông báo/comment cũ.
  - `js/borrow.js`: bỏ comment cũ (so_ngay_muon đã có hiệu lực).
  - `js/notifications-core.js`: dùng `GET /api/notifications`.
  - `js/admin-config.js`: gắn AI config, Sao lưu, Phục hồi.
  - `profile.html`, `readers.js`, `profile.js`: bỏ loại "Khác".
  - Xoá `js/reservation-mock.js` + bỏ thẻ script ở 6 trang.
  - 15 HTML: nav "Quản lý sách" cho admin.

## Kết quả kiểm chứng sau sửa

- QA suite (`QA/backend`): **118/118 PASS** (DB sạch).
- Bộ test gốc Backend: **101/101 PASS** trên DB sạch và **101/101 PASS** trên DB có dữ liệu QA.
- Kiểm tra tĩnh Frontend: **PASS**; không còn tham chiếu `reservation-mock`, không còn option "khac".
