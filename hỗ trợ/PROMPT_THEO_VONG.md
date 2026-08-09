# Bộ prompt theo vòng — hoàn thiện 8 chức năng quản lý trước, AI sau cùng

Thứ tự mỗi vòng: **Frontend → Backend → Thư Ký quét** (Backend đã xong chức năng 3 nên vòng 3 chỉ còn Frontend + Thư Ký). Làm xong 3-8 mới tới AI Engine.

---

## Vòng 3 — Chức năng 3: Quản lý độc giả (Backend ĐÃ XONG)

### 3.1 Frontend Agent — Lượt 4
```text
Frontend Agent — Vòng 3 (chức năng 3 — Quản lý độc giả):
1. Đọc Frontend/AGENTS.md, hỗ trợ/DE_BAI.md, Backend/api_docs.md (mục 11 — /api/readers) và Frontend/UI_DESIGN.md.
2. Tạo readers.html: danh sách độc giả + ô tìm theo mã/tên, form thêm, sửa, khoá/mở khoá thẻ, xoá (chỉ admin).
3. Field hiển thị: ma, hoTen, email, soDienThoai, loaiDocGia (sinh_vien/giang_vien/khac), trangThaiThe (hoat_dong/khoa), ngayTao.
4. Thêm vào js/api.js: readers, createReader, updateReader, deleteReader + fieldMap readerOut theo đúng api_docs.
5. Phân quyền: admin + librarian vào được trang; reader không thấy; nút Xoá chỉ admin.
6. Tự kiểm tra bằng admin/admin1 và librarian/librarian1 (librarian không xoá được — 403), gửi log:
   [FRONTEND] <thời gian> - Thay đổi: <mô tả> - Chức năng đề bài: 3 - Ảnh hưởng Backend: không - Ảnh hưởng AI Engine: không
```

### 3.2 Thư Ký Agent — quét lại
```text
Thư Ký — Quét lại toàn bộ: cập nhật changelog_tong.md, trang_thai_quet.md, ghi_nho_project.md; đóng YC-2026-08-09-003 sau khi xác nhận Frontend đã nối /api/readers; kiểm tra lệch pha chức năng 3.
```

---

## Vòng 4 — Chức năng 4: Mượn sách, trả sách, gia hạn, phạt quá hạn

### 4.1 Frontend Agent
```text
Frontend Agent — Vòng 4 (chức năng 4 — Mượn/trả/gia hạn/phạt):
1. Đọc Frontend/AGENTS.md, hỗ trợ/DE_BAI.md (chức năng 4 + mục 5), UI_DESIGN.md.
2. Tạo borrow.html: 3 khu vực — (a) Lập phiếu mượn: chọn độc giả + chọn sách + ngày mượn; (b) Trả sách/Gia hạn: chọn phiếu mượn đang hoạt động; (c) Hiển thị phạt quá hạn tự tính (mock theo cấu hình).
3. Chưa có API nên dùng mock + viết config chờ trong api.js: borrowSlip, returnBook, renewBook, getFine — ghi rõ endpoint/field cần Backend.
4. Ràng buộc hiển thị: thẻ độc giả khoá thì chặn mượn; sách còn 0 thì chặn chọn; giới hạn số sách/lần hiển thị từ cấu hình.
5. Gửi log:
   [FRONTEND] <thời gian> - Thay đổi: <mô tả> - Chức năng đề bài: 4 - Ảnh hưởng Backend: có - Ảnh hưởng AI Engine: không
```

### 4.2 Backend Agent
```text
Backend Agent — Vòng 4 (chức năng 4 — Mượn/trả/gia hạn/phạt):
1. Đọc Backend/AGENTS.md + hỗ trợ/DE_BAI.md. CHỈ làm chức năng 4.
2. Migration 0005: bảng BorrowSlips (ma_phieu, ma_doc_gia, ngay_muon, han_tra, ngay_tra, trang_thai), BorrowDetails (ma_phieu, ma_sach, so_luong, ngay_tra_chi_tiet), FineHistory (ma_phieu, ma_doc_gia, so_ngay_qua_han, so_tien, ngay_tinh).
3. API:
   - POST /api/borrows — lập phiếu: kiểm tra độc giả tồn tại + thẻ hoat_dong, sách còn > 0, không vượt max_books_at_once; han_tra = ngay_muon + max_borrow_days (từ LibraryConfig); giảm soLuong sách.
   - PUT /api/borrows/{ma}/return — trả sách: tăng soLuong, ghi ngày trả; nếu quá hạn → tự thêm FineHistory theo overdue_fine_per_day.
   - PUT /api/borrows/{ma}/renew — gia hạn: cộng thêm max_borrow_days, tối đa 1 lần (hoặc theo quy tắc đã chốt); tính phạt nếu đang quá hạn.
   - GET /api/borrows?docGia=... — danh sách phiếu theo trạng thái.
4. Phân quyền: thủ thư/admin dùng; độc giả xem phiếu của mình (tuỳ chọn đơn giản).
5. Test bắt buộc: mượn khi sách còn 0 → lỗi; trả trễ → phạt đúng công thức; gia hạn quá giới hạn → lỗi. Cập nhật api_docs.md (0.4.0), ghi audit log.
6. Gửi log: [BACKEND] <thời gian> - Thay đổi: <mô tả> - Chức năng: 4 - Ảnh hưởng Frontend: có - Ảnh hưởng AI Engine: có (dữ liệu lịch sử mượn cho AI-3)
```

### 4.3 Thư Ký — quét lại
```text
Thư Ký — Quét lại: ghi log Backend/Frontend chức năng 4; cập nhật canh_bao nếu Frontend chưa nối API mượn/trả.
```

---

## Vòng 5 — Chức năng 5: Tra cứu sách

### 5.1 Frontend Agent
```text
Frontend Agent — Vòng 5 (chức năng 5 — Tra cứu sách):
1. Tạo search.html (hoặc nâng cấp books.html): ô tìm kiếm theo tên/tác giả, lọc theo thể loại, lọc trạng thái còn/đang mượn.
2. Gọi GET /api/books kèm query params (q, theLoai, trangThai); hiển thị danh sách kết quả cho mọi role (reader dùng được).
3. Thêm config query vào js/api.js; ghi rõ field/endpoint cần Backend nếu chưa có.
4. Gửi log [FRONTEND] — Chức năng: 5.
```

### 5.2 Backend Agent
```text
Backend Agent — Vòng 5 (chức năng 5 — Tra cứu sách):
1. Nâng cấp GET /api/books thêm query params: q (tìm trong ten + tacGia), theLoai, trangThai (con | dang_muon — dựa trên soLuong và phiếu mượn đang hoạt động).
2. Cập nhật api_docs.md (0.5.0); test: tìm theo tên, tác giả, thể loại, trạng thái.
3. Gửi log [BACKEND] — Chức năng: 5.
```

### 5.3 Thư Ký — quét lại
```text
Thư Ký — Quét lại: ghi log chức năng 5; kiểm tra lệch pha search API ↔ UI.
```

---

## Vòng 6 — Chức năng 6: Đặt trước sách

### 6.1 Frontend Agent
```text
Frontend Agent — Vòng 6 (chức năng 6 — Đặt trước sách):
1. Thêm nút "Đặt trước" trên kết quả tra cứu khi sách hết/đang mượn hết (reader dùng được).
2. Tạo reservations.html cho thủ thư/admin: danh sách đặt trước, xác nhận/huỷ.
3. Mock + ghi rõ endpoint/field cần Backend; gửi log [FRONTEND] — Chức năng: 6.
```

### 6.2 Backend Agent
```text
Backend Agent — Vòng 6 (chức năng 6 — Đặt trước sách):
1. Migration 0006: bảng Reservations (ma_dat, ma_sach, ma_doc_gia, ngay_dat, trang_thai).
2. API: POST /api/reservations (chỉ cho phép khi sách hết/đang mượn hết), GET /api/reservations (thủ thư/admin), DELETE /api/reservations/{ma} (huỷ), PUT xác nhận/giao khi có sách trả.
3. Test: đặt trước khi sách còn → lỗi; đặt trùng → lỗi. Cập nhật api_docs.md (0.6.0); gửi log [BACKEND] — Chức năng: 6.
```

### 6.3 Thư Ký — quét lại
```text
Thư Ký — Quét lại: ghi log chức năng 6; kiểm tra lệch pha.
```

---

## Vòng 7 — Chức năng 7: Thống kê

### 7.1 Frontend Agent
```text
Frontend Agent — Vòng 7 (chức năng 7 — Thống kê):
1. Tạo stats.html (Dashboard): 3 nhóm — sách mượn nhiều nhất, độc giả hoạt động nhất, sách quá hạn (danh sách + số lượng).
2. Hiển thị bảng + biểu đồ đơn giản (CSS thuần, không cần thư viện); admin/librarian xem được.
3. Mock + ghi rõ endpoint cần Backend; gửi log [FRONTEND] — Chức năng: 7.
```

### 7.2 Backend Agent
```text
Backend Agent — Vòng 7 (chức năng 7 — Thống kê):
1. API GET /api/stats/top-books (sách mượn nhiều), GET /api/stats/top-readers (độc giả hoạt động), GET /api/stats/overdue-books (sách quá hạn: so với han_tra và ngay_tra).
2. Chỉ admin/librarian truy cập; cập nhật api_docs.md (0.7.0); test truy vấn.
3. Gửi log [BACKEND] — Chức năng: 7.
```

### 7.3 Thư Ký — quét lại
```text
Thư Ký — Quét lại: ghi log chức năng 7; kiểm tra lệch pha.
```

---

## Vòng 8 — Chức năng 8: Xuất danh sách sách, phiếu mượn, báo cáo

### 8.1 Frontend Agent
```text
Frontend Agent — Vòng 8 (chức năng 8 — Xuất dữ liệu):
1. Thêm nút Xuất trên: danh sách sách (books.html), danh sách phiếu mượn (borrow.html), báo cáo thống kê (stats.html).
2. Mỗi nút gọi API export tương ứng và tải file về (CSV tối thiểu; Excel/PDF nếu API hỗ trợ).
3. Gửi log [FRONTEND] — Chức năng: 8.
```

### 8.2 Backend Agent
```text
Backend Agent — Vòng 8 (chức năng 8 — Xuất dữ liệu):
1. API export: GET /api/export/books.csv, GET /api/export/borrows.csv, GET /api/export/report.csv (hoặc .xlsx/.pdf theo thư viện đã có).
2. Đảm bảo file tiếng Việt đúng encoding (UTF-8 BOM cho CSV); chỉ admin/librarian.
3. Cập nhật api_docs.md (0.8.0); test nội dung file. Gửi log [BACKEND] — Chức năng: 8.
```

### 8.3 Thư Ký — quét lại
```text
Thư Ký — Quét lại: ghi log chức năng 8; tổng kết đối chiếu 8 chức năng quản lý.
```

---

## SAU KHI XONG 3-8 → AI ENGINE (mới bắt đầu phần AI)

### AI Engine — AI-1 Chatbot tra cứu sách
```text
AI Engine Agent — Lượt 1 (AI-1): đọc AI_Engine/AI.txt + hỗ trợ/DE_BAI.md; tạo prompt template AI-1 giữ 2 câu ràng buộc gốc; dữ liệu sách lấy từ GET /api/books; provider/model/API key đọc từ /api/admin/config/ai (chưa có key thì mock); test 3 ca (mơ hồ, sách không tồn tại, sách hết); gửi log [AI_ENGINE] — AI-1.
```

### AI Engine — AI-2 Tóm tắt sách
```text
AI Engine Agent — Lượt 2 (AI-2): prompt riêng cho tóm tắt từ mô tả/mục lục sách (Backend cung cấp); không gửi dữ liệu cá nhân; test; log [AI_ENGINE] — AI-2.
```

### AI Engine — AI-3 Gợi ý sách liên quan
```text
AI Engine Agent — Lượt 3 (AI-3): prompt riêng dựa trên thể loại, tác giả, lịch sử mượn ĐÃ ẨN thông tin nhạy cảm (qua API Backend); thử ≥3 phiên bản prompt, ghi bản chốt; test; log [AI_ENGINE] — AI-3.
```

### Thư Ký — quét tổng
```text
Thư Ký — Quét tổng sau AI: cập nhật changelog, đối chiếu đủ 8 chức năng quản lý + 3 chức năng AI, xuất báo cáo tiến độ theo đề bài.
```
