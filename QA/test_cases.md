# Tổng hợp Test Case — QA

Cập nhật: 2026-08-10 · Backend 0.25.0 (điểm SVNET, DAT_TRUOC, so_ngay_muon, profile, lock reader, validation DTC).
Môi trường: Backend QA `LibraryDB_QA` (port 8001) + Backend demo (port 8000). Không đụng dữ liệu thật.

## 1. Backend — bộ test QA tự viết (`QA/backend`)

Kết quả vòng sạch: **116/116 PASS** (`run_qa_tests.ps1` tự reset DB → migrate → seed → start server → pytest).

| Nhóm | Số test | Ghi chú |
|---|---:|---|
| Auth/Đăng ký/Phân quyền | 15 | Login 3 vai trò, sai mật khẩu, thiếu field → 400, username/email/SĐT/họ tên sai validation, loại độc giả sai, role_display |
| Quản lý sách + Tra cứu + sort | 20 | CRUD, biên số lượng/năm, lọc q/theLoai/trạng thái, sort/order, `trangThai=het` → 422 (BUG-009) |
| Quản lý độc giả | 10 | CRUD admin-only, lock librarian, khoá thẻ chặn login, email trùng, validation |
| Mượn/Trả/Gia hạn/Phạt điểm | 18 | stock=0, vượt max, trả đúng/trễ (so_diem), gia hạn 1 lần/trễ/chặn khi có đặt trước, thu phạt trừ điểm SVNET, `so_ngay_muon` trực tiếp bị bỏ qua (BUG-002) |
| Đặt trước | 11 | Sách hết/còn/trùng, huỷ reader/librarian, xoá lịch sử, fulfill kiểm tồn kho, xác nhận đã lấy → phiếu mượn |
| Yêu cầu (MUON/TRA/GIA_HAN/DAT_TRUOC) | 10 | so_ngay_muon đề xuất + ghi đè khi duyệt, vượt max 400, DAT_TRUOC tạo đặt trước thật, reject, phân quyền |
| Hồ sơ cá nhân | 5 | GET/PUT profile, đổi mật khẩu, upload avatar (PNG hợp lệ + sai loại), cleanup file |
| Thông báo | 5 | SAP_HET_HAN, QUA_HAN, SACH_SAN_SANG, phiếu đã trả không hiện, phân quyền |
| Thống kê + Xuất CSV | 10 | top-books limit, top-readers, quá hạn, CSV BOM/header, reservations.csv chỉ librarian |
| Admin: cấu hình/audit/tài khoản/danh mục/restore | 12 | API key che, cấu hình điểm, tạo tài khoản chỉ librarian, khoá tài khoản, CRUD danh mục, restore file sai |

## 2. Backend — bộ test gốc của dự án (`Backend/tests`)

- Trên DB QA **sạch** (migrate xong, chưa seed): **101/101 PASS**.
- Trên DB QA **đã có dữ liệu** (sau khi QA suite tạo dữ liệu): **100/101 PASS** — fail duy nhất `test_stats.py::test_top_books_order_and_limit` (`KeyError: 'TESTSTT2'`) = BUG-007 (test không cô lập dữ liệu, logic API không sai).
- BUG-015: `conftest.py` dọn `Readers` theo `DTC100%` trước `Users` → vỡ FK khi DB có reader seed dùng dải này (đã né bằng cách QA dùng `DTC90x`; bản thân conftest vẫn chưa an toàn).

## 3. Frontend

- Kiểm tra tĩnh (`QA/frontend/check_frontend.py`): **PASS** — file tham chiếu đủ; mọi endpoint `api.js` đều có trong OpenAPI Backend (bao gồm profile/lock/DAT_TRUOC/export reservations).
- Kịch bản UI: `QA/frontend/test_cases_ui.md`.
- Bug mở (2026-08-10): BUG-002 (mượn trực tiếp), BUG-003, BUG-005, BUG-006, BUG-007, BUG-008 (menu sách), BUG-009 → BUG-016 — xem `bug_reports.md`.

## 4. AI Engine

AI-1/2/3 vẫn **chưa triển khai** (chỉ có `AI_Engine/AI.txt`). Test case chuẩn bị sẵn:

| Mã | Tình huống | Kết quả mong đợi |
|---|---|---|
| AI-001 | Câu hỏi mơ hồ | Gợi ý ≤5 sách có thật, kèm lý do, không bịa |
| AI-002 | Sách không tồn tại | Trả lời không tìm thấy |
| AI-003 | Sách hết | Trả đúng trạng thái hết + gợi ý đặt trước/tương tự |
| AI-004 | Input quá dài / timeout / rate limit | Lỗi rõ ràng, không treo |
| AI-005 | Response rỗng/sai định dạng | Frontend hiện lỗi thân thiện |
| AI-006 | Chưa cấu hình API key | Hiện lỗi cấu hình |

## 5. Tổng kết

- QA suite: **116/116 PASS**.
- Backend gốc: sạch **101/101**; có dữ liệu **100/101** (BUG-007).
- Frontend static: **PASS**; UI manual: xem kịch bản (nhiều case cần chạy tay).
- Bug mở: 16 mã (trong đó 3 mã sửa một phần, 2 mã đã sửa hoàn toàn) + AI chưa triển khai.
