# Kịch bản kiểm thử Frontend (thủ công)

> Phạm vi: 15 màn hình HTML/JS trong `Frontend`. Trạng thái:
> - **PASS (review)** — đã đối chiếu code + API, luồng khớp.
> - **FAIL** — có bug, xem `../bug_reports.md`.
> - **PENDING** — cần chạy tay trên trình duyệt để xác nhận hiển thị/responsive.
> - **N/A** — chức năng chưa có (AI).

Tài khoản demo: `qa_admin` / `qa_librarian` / `qa_reader1` (mật khẩu `Test@12345`) — dùng backend QA port 8001 hoặc backend demo port 8000 (thay `baseUrl` trong `js/api.js`).

## Cập nhật 2026-08-10 (Backend 0.25.0)

| Mã | Thay đổi trạng thái |
|---|---|
| UI-012 | Vẫn FAIL (BUG-003) — lọc "Đang mượn" sai |
| UI-032 | Vẫn FAIL (BUG-002) — "Số ngày mượn" ở borrow.html bị bỏ qua |
| UI-037 | ✅ Đã sửa — phạt hiển thị dữ liệu thật, đơn vị điểm |
| UI-050/051 | ✅ Đã sửa — duyệt yêu cầu áp dụng số ngày mượn |
| UI-052 | ✅ Đã sửa — DAT_TRUOC hoạt động (Backend hỗ trợ) |
| UI-060→066 | Cập nhật: admin bị chặn vào trang Đặt trước (đúng thiết kế); librarian có nút Xoá lịch sử nhưng Backend từ chối → FAIL (BUG-013) |
| UI-080 | Vẫn FAIL nhẹ (BUG-005) — chưa dùng /api/notifications |
| UI-100 | Cập nhật: chỉ tạo tài khoản thủ thư; reader tự đăng ký |
| UI-103 | FAIL (BUG-011) — nút AI/backup/restore ở admin-config.html không chạy |
| Mới | Lọc "Hết sách" → FAIL (BUG-009); nút "Gửi yêu cầu" không disable → FAIL (BUG-010); profile còn option "Khác" → FAIL (BUG-012); reservation-mock chưa xoá → FAIL nhẹ (BUG-014) |
| Mới | Hồ sơ cá nhân (profile.html): GET/PUT/đổi mật khẩu/avatar — PASS (review + test API) |

## 1. Đăng nhập / Đăng ký (`index.html`, `register.html`)

| Mã | Loại | Bước | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|
| UI-001 | Đúng | Nhập đúng tài khoản/mật khẩu 3 vai trò | Vào `search.html`, menu theo vai trò | PASS (review) |
| UI-002 | Sai | Nhập sai mật khẩu | Hiện lỗi, không vào hệ thống | PASS (review) |
| UI-003 | Sai | Bỏ trống ô | Chặn submit / hiện lỗi | PASS (review) |
| UI-004 | Sai | Tài khoản bị khoá | 401, hiện "tài khoản bị khoá" | PASS (review) |
| UI-005 | Đúng | Đăng ký reader hợp lệ | Tạo tài khoản + tự đăng nhập | PASS (review) |
| UI-006 | Sai | Username/email trùng, mật khẩu < 6 ký tự | Hiện lỗi API, không tạo | PASS (review) |

## 2. Tra cứu sách (`search.html`)

| Mã | Loại | Bước | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|
| UI-010 | Đúng | Tìm theo tên/tác giả, thể loại, trạng thái | Kết quả khớp backend | PASS (review) |
| UI-011 | Sai | Nhập từ khoá không có | Bảng trống, thông báo "Không tìm thấy" | PASS (review) |
| UI-012 | Sai | Trạng thái "Đang mượn" với sách còn tồn nhưng có phiếu đang mượn | Phải hiển thị sách đó | FAIL (BUG-003) |
| UI-013 | Biên | Nhấn Enter ở ô tìm kiếm | Tìm kiếm chạy | PASS (review) |
| UI-014 | Đúng | Reader nhìn nút "Đặt trước" chỉ khi sách hết | Nút hiện đúng lúc | PASS (review) |

## 3. Quản lý sách (`books.html`)

| Mã | Loại | Bước | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|
| UI-020 | Đúng | Thêm sách hợp lệ | Lưu + xuất hiện trong bảng | PASS (review) |
| UI-021 | Sai | Mã trùng / số lượng âm / năm ngoài 1000–2100 | Hiện lỗi API | PASS (review) |
| UI-022 | Biên | soLuong = 0 | Tạo được, hiện "Hết sách" | PASS (review) |
| UI-023 | Đúng | Sửa / xoá sách | Cập nhật bảng | PASS (review) |
| UI-024 | Sai | Reader mở trang | Không hiện nút Thêm/Sửa/Xoá | PASS (review) |
| UI-025 | N/A | Admin mở trang | Backend cho phép, nhưng menu ẩn với admin | FAIL (BUG-008, nhẹ) |
| UI-026 | Đúng | Nút "Xuất CSV" | Tải file có BOM, đúng header | PASS (review) |

## 4. Mượn / Trả / Gia hạn / Phạt (`borrow.html`)

| Mã | Loại | Bước | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|
| UI-030 | Đúng | Lập phiếu mượn hợp lệ | Tạo phiếu, giảm số lượng | PASS (review) |
| UI-031 | Sai | Sách hết / thẻ khoá / quá giới hạn | Hiện lỗi API rõ ràng | PASS (review) |
| UI-032 | Sai | Nhập "Số ngày mượn" = 3 | Hạn trả phải ~3 ngày | FAIL (BUG-002) |
| UI-033 | Đúng | Trả sách đúng hạn | Không phạt, tăng số lượng | PASS (review) |
| UI-034 | Đúng | Trả sách quá hạn | Hiện số ngày + tiền phạt | PASS (review) |
| UI-035 | Đúng | Gia hạn lần 1 | Hạn mới +14 ngày | PASS (review) |
| UI-036 | Sai | Gia hạn lần 2 / có đặt trước | Chặn, hiện lý do | PASS (review) |
| UI-037 | Sai | Danh sách phạt chưa thu | Phải là dữ liệu thật từ API | FAIL (BUG-004) |
| UI-038 | Sai | Admin mở trang | Bị chuyển về search | PASS (review) |

## 5. Độc giả (`readers.html`)

| Mã | Loại | Bước | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|
| UI-040 | Đúng | Thêm/sửa độc giả | Lưu thành công | PASS (review) |
| UI-041 | Sai | Trùng mã/email, loại sai | Hiện lỗi | PASS (review) |
| UI-042 | Đúng | Khoá/mở thẻ | Cập nhật trạng thái | PASS (review) |
| UI-043 | Sai | Librarian xoá độc giả | Bị chặn (chỉ admin) | PASS (review) |

## 6. Yêu cầu (`requests.html`)

| Mã | Loại | Bước | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|
| UI-050 | Đúng | Reader gửi yêu cầu MUON → librarian duyệt | Tạo phiếu PM..., trạng thái DA_DUYET | PASS (review) |
| UI-051 | Đúng | Gửi TRA / GIA_HAN → duyệt | Trả/gia hạn đúng | PASS (review) |
| UI-052 | Sai | Chọn "Đặt trước sách" → Gửi | Phải tạo đặt trước hoặc ẩn option | FAIL (BUG-001) |
| UI-053 | Sai | Nhập "Số ngày mượn" khi duyệt | Phải áp dụng số ngày | FAIL (BUG-002) |
| UI-054 | Sai | Duyệt yêu cầu đã xử lý | Hiện lỗi "không ở trạng thái chờ" | PASS (review) |
| UI-055 | Đúng | Reader xoá yêu cầu đã xử lý | Xoá khỏi lịch sử | PASS (review) |

## 7. Đặt trước (`reservations.html`)

| Mã | Loại | Bước | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|
| UI-060 | Đúng | Đặt trước sách hết từ `search.html` | Tạo RV..., trạng thái CHO_XU_LY | PASS (review) |
| UI-061 | Sai | Đặt trước sách còn | Hiện lỗi "sách còn" | PASS (review) |
| UI-062 | Sai | Đặt trùng | Hiện lỗi 409 | PASS (review) |
| UI-063 | Đúng | Reader huỷ đặt trước của mình | HUY | PASS (review) |
| UI-064 | Sai | Reader huỷ đặt trước người khác | Không thấy/404 | PASS (review) |
| UI-065 | Đúng | Librarian đánh dấu sẵn sàng | SAN_SANG | PASS (review) |
| UI-066 | Sai | Admin vào trang | Bị chuyển về search | PASS (review) |

## 8. Lịch sử mượn (`my-borrows.html`)

| Mã | Loại | Bước | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|
| UI-070 | Đúng | Reader xem lịch sử | Chỉ thấy phiếu của mình, kèm phạt | PASS (review) |
| UI-071 | Sai | Xoá phiếu đang mượn | Bị chặn (chỉ xoá phiếu đã trả) | PASS (review) |
| UI-072 | Đúng | Xoá 1 / xoá tất cả phiếu đã trả | Xoá khỏi lịch sử | PASS (review) |
| UI-073 | Sai | Librarian mở trang | Bị chuyển về search | PASS (review) |

## 9. Thông báo (`notifications.html`)

| Mã | Loại | Bước | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|
| UI-080 | Đúng | Reader có phiếu sắp/quá hạn, đặt trước sẵn sàng | Hiện thông báo đúng loại | PASS (review) |
| UI-081 | Đúng | Đánh dấu đã đọc / đọc tất cả | Lưu localStorage, badge giảm | PASS (review) |
| UI-082 | N/A | Nguồn dữ liệu thông báo | Nên dùng GET /api/notifications | FAIL (BUG-005, nhẹ) |

## 10. Thống kê (`stats.html`)

| Mã | Loại | Bước | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|
| UI-090 | Đúng | Xem top sách/độc giả/quá hạn | Dữ liệu từ API thật | PASS (review) |
| UI-091 | Đúng | Nút "Xuất CSV" | Tải báo cáo CSV | PASS (review) |
| UI-092 | Sai | Reader mở trang | Bị chuyển về search | PASS (review) |

## 11. Admin: tài khoản / danh mục / cấu hình

| Mã | Loại | Bước | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|
| UI-100 | Đúng | Tạo/sửa/khoá/xoá tài khoản | Thành công, tài khoản khoá không đăng nhập được | PASS (review) |
| UI-101 | Sai | Username trùng, password < 6 | Hiện lỗi | PASS (review) |
| UI-102 | Đúng | CRUD thể loại/NXB | Thành công; không xoá được mục đang dùng | PASS (review) |
| UI-103 | Đúng | Sửa cấu hình thư viện/AI | Lưu, API key bị che | PASS (review) |
| UI-104 | Sai | Librarian/reader mở trang admin | Bị chuyển về search / API 403 | PASS (review) |
| UI-105 | N/A | Sao lưu / phục hồi CSDL | Không test thật (tránh thay đổi dữ liệu); kiểm tra lỗi file sai đã pass | PENDING |

## 12. AI (chưa có màn hình)

| Mã | Loại | Bước | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|
| UI-110 | N/A | Chatbot tra cứu AI | Có màn hình + API /ai/search | N/A (chưa triển khai) |
| UI-111 | N/A | Tóm tắt sách AI | Có màn hình + API /ai/summarize | N/A (chưa triển khai) |
| UI-112 | N/A | Gợi ý sách liên quan | Có màn hình + API /ai/recommend | N/A (chưa triển khai) |

## 13. Responsive / chung

| Mã | Loại | Bước | Kết quả mong đợi | Trạng thái |
|---|---|---|---|---|
| UI-120 | Biên | Mở các trang ở mobile/tablet | Không vỡ layout, bảng cuộn ngang | PENDING (cần chạy tay) |
| UI-121 | Biên | Loading khi gọi API chậm | Hiện spinner, không bấm trùng | PASS (review) |
| UI-122 | Sai | Backend down | Hiện thông báo kết nối thất bại | PASS (review) |
