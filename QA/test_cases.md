# Tổng hợp Test Case — QA

Ngày: 2026-08-09 · Môi trường: Backend QA `LibraryDB_QA` (port 8001) + Backend demo (port 8000) · Không đụng dữ liệu thật.

## 1. Backend — bộ test QA tự viết (`QA/backend`)

Chạy bằng `python -m pytest` (hoặc `run_qa_tests.ps1` để tự reset DB sạch).
Kết quả vòng sạch: **96/96 PASS**.

| Nhóm | Số test | Đúng | Sai | Biên | Ghi chú |
|---|---|---|---|---|---|
| Auth/Đăng ký/Phân quyền | 12 | 3 | 7 | 2 | Login 3 vai trò, sai mật khẩu, trùng username/email, password ngắn, loại độc giả sai, admin không mượn được |
| Quản lý sách + Tra cứu | 18 | 8 | 7 | 3 | CRUD, soLuong=0, namXb biên 1000/2100, tìm theo tên/tác giả/loại/trạng thái, trạng thái sai |
| Quản lý độc giả | 9 | 4 | 4 | 1 | CRUD, trùng mã/email, loại/trạng thái sai, khoá thẻ, xoá chỉ admin |
| Mượn/Trả/Gia hạn/Phạt | 19 | 7 | 9 | 3 | stock=0, thiếu tồn, vượt max 3, trả đúng/trễ, gia hạn 1 lần, gia hạn trễ có phạt, chặn gia hạn khi có đặt trước, thu phạt 2 lần |
| Đặt trước | 10 | 4 | 5 | 1 | Sách hết đặt được, sách còn bị chặn, trùng 409, huỷ, sẵn sàng, phân quyền |
| Yêu cầu reader→thủ thư | 7 | 3 | 4 | 0 | MUON/TRA/GIA_HAN duyệt, từ chối, thiếu items, phiếu người khác, trùng mã |
| Thông báo | 5 | 3 | 2 | 0 | SAP_HET_HAN, QUA_HAN, SACH_SAN_SANG, phiếu đã trả không hiện, phân quyền |
| Thống kê + Xuất CSV | 8 | 4 | 3 | 1 | top-books limit 1–100, top-readers, quá hạn, CSV BOM/header, phân quyền |
| Admin: cấu hình/audit/tài khoản/danh mục/restore | 8 | 4 | 3 | 1 | API key che, khoá tài khoản, CRUD danh mục, restore file sai → 404 |

## 2. Backend — bộ test gốc của dự án (`Backend/tests`)

Chạy trên DB QA (trỏ `DATABASE_URL` về `LibraryDB_QA`): **66/67 PASS, 1 FAIL**.

- FAIL: `test_stats.py::test_top_books_order_and_limit` — test không cô lập dữ liệu: giả định top-10 chỉ có 2 sách TEST; khi DB có nhiều sách khác có lượt mượn, `TESTSTT2` (1 lượt) rơi ngoài top-10 → `KeyError`. Logic API vẫn đúng (xem BUG-007).
- Các test còn lại bao gồm: mượn/trả/phạt, đặt trước, yêu cầu, thông báo, thống kê, xuất CSV, admin — đều pass trên DB QA.

## 3. Frontend

- Kiểm tra tĩnh (`QA/frontend/check_frontend.py`): **PASS** — mọi file HTML tham chiếu CSS/JS đều tồn tại; mọi endpoint trong `js/api.js` đều có trong OpenAPI Backend.
- Kịch bản UI thủ công: `QA/frontend/test_cases_ui.md` — 122 case đúng/sai/biên; nhiều case đã xác nhận bằng code review, một số cần chạy tay trên trình duyệt.
- Bug frontend phát hiện: **BUG-001 → BUG-006, BUG-008** (xem `bug_reports.md`).

## 4. AI Engine — bắt buộc theo mục 4 đề bài

AI-1/2/3 **chưa được triển khai** (AI_Engine chỉ có file prompt `AI.txt`; Backend chưa có `/ai/search`, `/ai/summarize`, `/ai/recommend`; Frontend chưa có màn hình AI). Vì vậy **chưa thể thực thi** 3 tình huống bắt buộc. Test case đã chuẩn bị sẵn để chạy khi có code:

| Mã | Tình huống | Input | Kết quả mong đợi |
|---|---|---|---|
| AI-001 | Câu hỏi mơ hồ | "Tôi muốn tìm sách hay để đọc" | Gợi ý ≤ 5 sách có trong dữ liệu, kèm lý do; không bịa mã sách |
| AI-002 | Sách không tồn tại | "Tìm sách 'Khoa học huyền bí 2099'" | Trả lời không tìm thấy, không bịa ra sách |
| AI-003 | Sách hết | "Tìm sách X đang hết" | Trả về trạng thái hết + gợi ý đặt trước/sách tương tự, không báo sai còn sách |
| AI-004 | Biên | Prompt/dữ liệu đầu vào quá dài | Trả lỗi rõ ràng (422/timeout), không treo |
| AI-005 | Biên | API AI trả response rỗng/sai định dạng | Frontend hiện lỗi thân thiện, không crash |
| AI-006 | Sai | Gọi AI khi chưa cấu hình API key | Hiện lỗi cấu hình rõ ràng |

## 5. Tổng kết

- Tổng test đã chạy tự động: **96 (QA) + 67 (gốc) = 163**, pass **162**, fail **1** (test gốc thiếu cô lập dữ liệu).
- Test case đúng/sai/biên cho mượn/trả/quá hạn/phạt: đầy đủ (19 case backend + UI).
- Test chatbot AI: chưa chạy được vì chưa có code AI (đã chuẩn bị case).
- Bug đã ghi nhận: 8 bug + 1 trạng thái AI chưa triển khai.
