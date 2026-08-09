# Báo cáo lỗi — QA

Ngày: 2026-08-09 · Mức độ: Nhẹ / Vừa / Nghiêm trọng

---

## BUG-001 — "Đặt trước sách" ở trang Yêu cầu luôn thất bại (loại DAT_TRUOC không được Backend hỗ trợ)

- **Mô tả:** `requests.html` có option "Đặt trước sách" (`loai=DAT_TRUOC`) nhưng `POST /api/requests` chỉ nhận `MUON/TRA/GIA_HAN` → mọi yêu cầu đặt trước gửi từ UI trả 422.
- **Bước tái hiện:** Reader đăng nhập → Yêu cầu → chọn "Đặt trước sách" → chọn sách hết → Gửi.
- **Kết quả mong đợi:** Tạo đặt trước thành công (hoặc option bị ẩn/chuyển sang `/api/reservations`).
- **Kết quả thực tế:** `422 {"detail":[{"type":"literal_error","loc":["body","loai"],...}]}` — đã kiểm chứng bằng HTTP với `loai=DAT_TRUOC`.
- **Mức độ:** Vừa.
- **Agent cần sửa:** Frontend (ẩn option hoặc gọi `/api/reservations`); Backend nếu muốn mở rộng `loai` thêm `DAT_TRUOC`.
- **File liên quan:** `Frontend/requests.html`, `Frontend/js/requests.js`, `Backend/app/schemas.py` (`RequestCreate`), `Backend/app/routers/requests.py`.

---

## BUG-002 — "Số ngày mượn" nhập ở UI bị Backend bỏ qua, hạn trả luôn = cấu hình mặc định (14 ngày)

- **Mô tả:** `borrow.html` và `requests.html` cho nhập/đề xuất số ngày mượn (`so_ngay_muon`), nhưng schema Backend không có field này → hạn trả luôn là `max_borrow_days`.
- **Bước tái hiện:** Librarian lập phiếu mượn với `so_ngay_muon=3` → xem `han_tra`.
- **Kết quả mong đợi:** `han_tra = ngay_muon + 3 ngày` (hoặc UI không cho nhập nếu chưa hỗ trợ).
- **Kết quả thực tế:** `han_tra - ngay_muon = 14 ngày` — đã kiểm chứng bằng HTTP.
- **Mức độ:** Vừa.
- **Agent cần sửa:** Backend (nhận `so_ngay_muon` trong `BorrowCreate`/`RequestCreate` + duyệt) hoặc Frontend (bỏ field gây hiểu nhầm).
- **File liên quan:** `Frontend/js/borrow.js`, `Frontend/js/requests.js`, `Backend/app/schemas.py`, `Backend/app/routers/borrows.py`, `Backend/app/routers/requests.py`.

---

## BUG-003 — Lọc "Đang mượn" ở trang Tra cứu bỏ sót sách còn tồn kho nhưng đang được mượn dở

- **Mô tả:** `search.js` lọc client-side `trangThai=dang_muon` với điều kiện `soLuong <= 0`, trong khi Backend định nghĩa "đang mượn" gồm cả sách còn tồn nhưng đang có phiếu mượn chưa trả.
- **Bước tái hiện:** Có sách stock=4 đang mượn 1 bản → Tra cứu → chọn "Đang mượn".
- **Kết quả mong đợi:** Sách xuất hiện trong danh sách.
- **Kết quả thực tế:** Bị lọc mất. Backend trả đúng (`GET /api/books?trangThai=dang_muon` có `QAS005 stock=4`), nhưng `clientFilter` loại bỏ.
- **Mức độ:** Vừa.
- **Agent cần sửa:** Frontend (`search.js` — bỏ lọc trùng hoặc sửa điều kiện; Backend đã lọc đúng).

---

## BUG-004 — Trang Mượn/Trả hiển thị danh sách phạt giả (mock), nút "Đã thu" luôn thất bại

- **Mô tả:** `borrow.js` dùng `MOCK_FINES` (`PMFINE1`, `PMFINE2`, `DGREADER`) thay vì dữ liệu phạt thật từ `GET /api/borrows`. Bấm "Đã thu" gọi `POST /api/borrows/PMFINE1/collect-fine` → 404 và hiện thông báo sai "Backend chưa hỗ trợ thu phạt" (thực tế Backend đã có API).
- **Bước tái hiện:** Librarian mở `borrow.html` → xem bảng phạt → bấm "Đã thu".
- **Kết quả mong đợi:** Chỉ hiện phạt thật chưa thu; bấm "Đã thu" cập nhật thành công.
- **Kết quả thực tế:** Dữ liệu giả; thao tác trả 404.
- **Mức độ:** Vừa.
- **Agent cần sửa:** Frontend (`borrow.js` — lấy `fines` từ `GET /api/borrows`, bỏ mock).

---

## BUG-005 — Trang Thông báo chưa dùng `GET /api/notifications` dù Backend đã có

- **Mô tả:** `notifications-core.js` tự tổng hợp từ `GET /api/borrows/me` + `GET /api/reservations`; endpoint `/api/notifications` đã có trong `api.js` nhưng không được gọi.
- **Kết quả mong đợi:** Dùng API chính thức để không lệch logic khi Backend bổ sung loại thông báo.
- **Kết quả thực tế:** Chức năng chạy được nhưng nợ kỹ thuật; có thể lệch dữ liệu với Backend.
- **Mức độ:** Nhẹ.
- **Agent cần sửa:** Frontend (`notifications-core.js`).

---

## BUG-006 — Comment/ghi chú trong Frontend lỗi thời: nói Backend chưa có API thống kê/xuất/thông báo/thu phạt

- **Mô tả:** `api.js`, `search.js`, `stats.js`, `borrow.js` còn comment "Backend chưa có API" cho các chức năng Backend đã triển khai (stats, export, notifications, collect-fine, q/theLoai/trangThai).
- **Ảnh hưởng:** Gây hiểu nhầm khi bảo trì; các trang vẫn hoạt động vì có fallback mock.
- **Mức độ:** Nhẹ.
- **Agent cần sửa:** Frontend (cập nhật comment; cân nhắc bỏ fallback mock sau khi Backend ổn định).

---

## BUG-007 — Test gốc `Backend/tests/test_stats.py::test_top_books_order_and_limit` không cô lập dữ liệu

- **Mô tả:** Test giả định top-10 chỉ chứa 2 sách `TESTSTT1`/`TESTSTT2`; khi DB có ≥10 sách khác có lượt mượn, `TESTSTT2` (1 lượt) không vào top-10 → `KeyError: 'TESTSTT2'`.
- **Bước tái hiện:** Chạy `Backend/tests` trên DB có sẵn nhiều dữ liệu (đã chạy trên `LibraryDB_QA` có seed QA).
- **Kết quả mong đợi:** Test pass độc lập với dữ liệu có sẵn.
- **Kết quả thực tế:** 66/67 pass; 1 fail do `KeyError`. Logic API top-books không sai (thứ tự/giới hạn đúng).
- **Mức độ:** Nhẹ–Vừa (chất lượng test, không phải lỗi runtime).
- **Agent cần sửa:** Backend (test — lọc theo prefix TEST hoặc dùng DB sạch/transaction).

---

## BUG-008 — Admin không thấy menu "Quản lý sách"/"Quản lý độc giả" dù được phép CRUD theo Backend và USE_CASE

- **Mô tả:** Nav trong các HTML đặt `data-roles="librarian"` cho `books.html`/`readers.html`; admin bị ẩn link, dù Backend cho admin CRUD sách/độc giả và USE_CASE ghi admin kế thừa quyền thủ thư (trừ mượn/trả/gia hạn/đặt trước).
- **Kết quả mong đợi:** Admin thấy menu Quản lý sách/Độc giả.
- **Kết quả thực tế:** Menu ẩn; admin vẫn vào được bằng URL trực tiếp (books.js chỉ `requireAuth`).
- **Mức độ:** Nhẹ.
- **Agent cần sửa:** Frontend (đổi `data-roles="librarian"` → `"librarian,admin"` cho 2 link này).

---

## TRẠNG THÁI — AI-1/2/3 chưa triển khai (không phải bug chạy sai, nhưng không đạt yêu cầu đề bài mục 3.2/4)

- **Mô tả:** `AI_Engine` chỉ có `AI.txt` (prompt); Backend không có router `/ai/*`; Frontend không có màn hình chatbot/tóm tắt/gợi ý.
- **Ảnh hưởng:** Không thể thực thi 3 test bắt buộc (câu hỏi mơ hồ / sách không tồn tại / sách hết) và không có khả năng xử lý timeout/rate-limit/response sai định dạng (KT3-7).
- **Mức độ:** Nghiêm trọng đối với yêu cầu đề bài (theo phạm vi QA: chỉ test phần đã hoàn thành nên không xem là lỗi chạy sai).
- **Agent cần sửa:** AI Engine (implement 3 chức năng + prompt riêng) + Backend (endpoint `/ai/*` gọi AI Engine) + Frontend (màn hình AI).
