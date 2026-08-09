# Đối chiếu Use Case (tài liệu Actor & Use Case) với Frontend/Backend hiện tại

> Nguồn: tài liệu "Phân tích Actor & Use Case — Hệ thống Quản lý Thư viện tích hợp AI (Đề tài 02)".
> Mục tiêu: sửa Frontend + Backend cho khớp 28 use case từ đầu đến cuối.

## Tổng quan lệch

| Khu vực | Tài liệu yêu cầu | Hiện trạng | Cần sửa |
|---|---|---|---|
| Đăng ký (UC01) | Độc giả đăng ký / đăng nhập | Chỉ có đăng nhập, không có đăng ký | ✅ Thêm API + UI đăng ký |
| Liên kết tài khoản ↔ độc giả (UC10) | Độc giả xem lịch sử mượn/trả/phạt của mình | Users và Readers tách biệt, chưa liên kết; độc giả không có API xem lịch sử | ✅ Thêm cột liên kết + API `borrows/me` + UI |
| Yêu cầu mượn/trả (UC07/08) | Độc giả gửi yêu cầu → thủ thư xử lý | Độc giả không gửi yêu cầu được; chỉ thủ thư tự lập phiếu | ✅ Thêm bảng YêuCầu + API + UI |
| Gia hạn từ độc giả (UC09) | Độc giả yêu cầu gia hạn (từ chối nếu có đặt trước) | Chỉ thủ thư gia hạn, chưa có yêu cầu từ độc giả | ✅ Gắn với luồng yêu cầu |
| Quản lý tài khoản (UC23) | Admin tạo/khoá tài khoản thủ thư + độc giả, phân quyền | ĐÃ XOÁ phần quản lý tài khoản thủ thư trước đó | ✅ Khôi phục + mở rộng quản lý cả độc giả |
| Danh mục thể loại/NXB (UC25) | Admin quản lý danh mục dùng chung | theLoai/NXB là text tự do trong Books | ✅ Thêm bảng TheLoai/NXB + API + UI + sửa Books |
| Đặt trước (UC06/18) | Độc giả đặt trước, thủ thư xử lý khi sách về | Chưa có | ⏳ Vòng 6 (đã có prompt) |
| Thông báo (UC11) | Nhắc hạn trả, sách đặt trước đã có | Chưa có | ⏳ Làm sau đặt trước |
| Thống kê/báo cáo (UC20/28) | Thủ thư + admin xem thống kê, xuất báo cáo | Chưa có | ⏳ Vòng 7-8 (đã có prompt) |
| AI (UC03/04/05, UC21, UC26) | Tra cứu AI, tóm tắt, gợi ý; admin giám sát; thủ thư kiểm duyệt (tuỳ chọn) | AIConfig có, chưa có code AI | ⏳ Sau các vòng quản lý |
| Sao lưu/phục hồi (UC27) | Backup + restore | Backup có, restore chưa | ✅ Thêm API restore (hoặc ghi chú) |
| Kiểm duyệt AI (UC21) | Thủ thư xác nhận/điều chỉnh kết quả AI (tùy chọn) | Chưa | 🟡 Tuỳ chọn, làm cùng AI |

## Đối chiếu chi tiết theo Use Case

| UC | Use Case | Actor | Hiện trạng |
|---|---|---|---|
| UC01 | Đăng ký / Đăng nhập | Độc giả | ❌ Thiếu đăng ký |
| UC02 | Tra cứu sách thường | Độc giả | ✅ search.html + query books |
| UC03 | Tra cứu bằng Chatbot AI | Độc giả | ❌ Chưa (AI) |
| UC04 | Xem tóm tắt sách AI | Độc giả | ❌ Chưa (AI) |
| UC05 | Gợi ý sách liên quan AI | Độc giả | ❌ Chưa (AI) |
| UC06 | Đặt mượn trước | Độc giả | ❌ Chưa (vòng 6) |
| UC07 | Yêu cầu mượn sách | Độc giả | ❌ Chưa có luồng yêu cầu |
| UC08 | Yêu cầu trả sách | Độc giả | ❌ Chưa có luồng yêu cầu |
| UC09 | Gia hạn mượn | Độc giả | ❌ Chỉ thủ thư làm trực tiếp |
| UC10 | Xem lịch sử mượn/trả & phạt | Độc giả | ❌ Chưa liên kết Users-Readers, chưa API/UI |
| UC11 | Nhận thông báo | Độc giả | ❌ Chưa |
| UC12 | Đăng nhập quyền thủ thư | Thủ thư | ✅ |
| UC13 | Quản lý sách CRUD | Thủ thư | ✅ |
| UC14 | Quản lý độc giả | Thủ thư | ✅ |
| UC15 | Xử lý phiếu mượn | Thủ thư | ✅ API; UI mượn/trả còn thiếu |
| UC16 | Xử lý phiếu trả | Thủ thư | ✅ API; UI còn thiếu |
| UC17 | Xử lý gia hạn | Thủ thư | ✅ API; cần thêm điều kiện đặt trước |
| UC18 | Xử lý đặt trước | Thủ thư | ❌ Chưa (vòng 6) |
| UC19 | Tính & thu phạt quá hạn | Thủ thư | ✅ Tự tính khi trả; chưa có UI thu phạt |
| UC20 | Thống kê & xuất báo cáo | Thủ thư | ❌ Chưa (vòng 7-8) |
| UC21 | Kiểm duyệt nội dung AI | Thủ thư | 🟡 Tuỳ chọn |
| UC22 | Đăng nhập quyền admin | Admin | ✅ |
| UC23 | Quản lý tài khoản & phân quyền | Admin | ❌ Đã xoá — cần khôi phục + quản lý cả độc giả |
| UC24 | Cấu hình quy định mượn/trả | Admin | ✅ config/library |
| UC25 | Quản lý danh mục thể loại/NXB | Admin | ❌ Chưa có bảng danh mục |
| UC26 | Cấu hình & giám sát AI | Admin | ✅ config/ai; giám sát chưa |
| UC27 | Sao lưu & phục hồi | Admin | ✅ backup; ❌ restore |
| UC28 | Báo cáo tổng hợp | Admin | ❌ Chưa (vòng 7-8) |

## Kế hoạch sửa đề xuất

### Đợt A — Backend tương thích nền (làm trước, vì thay đổi CSDL/API)
1. Migration 0006: bảng TheLoai, Nxb; thêm cột liên kết Users↔Readers; bảng YeuCau (yêu cầu mượn/trả/gia hạn); thêm cột cho phép đăng ký.
2. API: đăng ký độc giả, xem lịch sử của độc giả, tạo/xử lý yêu cầu mượn-trả-gia hạn, khôi phục quản lý tài khoản admin, CRUD danh mục thể loại/NXB, restore backup.
3. Cập nhật api_docs (0.6.0) + test.

### Đợt B — Frontend tương thích
1. Trang đăng ký; trang hồ sơ/lịch sử mượn-phạt của độc giả; trang gửi yêu cầu mượn/trả/gia hạn.
2. Khôi phục trang quản lý tài khoản admin (thủ thư + độc giả); trang danh mục thể loại/NXB.
3. Cập nhật menu theo 3 actor.

### Đợt C — Đặt trước + thông báo (vòng 6) + thống kê/báo cáo (vòng 7-8)

### Đợt D — AI (UC03/04/05/21/26) + kiểm duyệt + giám sát

---

## So sánh tài liệu Actor & Use Case với đề bài (DE_BAI.md)

### ĐÚNG với đề bài (lõi 8 + 3)

- 3 actor chính (độc giả, thủ thư, quản trị viên) ✅ chức năng 1.
- UC13 Quản lý sách ✅ chức năng 2; UC14 Quản lý độc giả ✅ chức năng 3.
- UC15/16/17/19 Mượn/trả/gia hạn/phạt ✅ chức năng 4.
- UC02 Tra cứu sách ✅ chức năng 5; UC06/18 Đặt trước ✅ chức năng 6.
- UC20/28 Thống kê + báo cáo ✅ chức năng 7, 8.
- UC03/04/05 Chatbot AI, tóm tắt, gợi ý ✅ 3 chức năng AI (3.2).
- AI Engine là actor phụ (được hệ thống gọi, không tự truy vấn CSDL) ✅ đúng ràng buộc đề bài.

### NGOÀI đề bài (tài liệu mở rộng — đề bài KHÔNG yêu cầu)

| UC | Nội dung | Ghi chú |
|---|---|---|
| UC01 | Đăng ký tài khoản độc giả | Đề bài chỉ nói "Đăng nhập, phân quyền" — không yêu cầu đăng ký tự do |
| UC07/08 | Độc giả gửi yêu cầu mượn/trả online | Đề bài để thủ thư quản lý mượn/trả trực tiếp |
| UC09 | Độc giả yêu cầu gia hạn | Tương tự UC07/08 |
| UC10 | Độc giả xem lịch sử/phạt cá nhân | Không có trong đề bài (hợp lý nhưng là thêm) |
| UC11 | Nhận thông báo | Không có trong đề bài |
| UC21 | Kiểm duyệt nội dung AI | Tuỳ chọn, không có trong đề bài |
| UC23 | Admin quản lý tài khoản & phân quyền | Suy ra từ chức năng 1 nhưng không nêu rõ — **ĐÃ CHỐT 2026-08-09: GIỮ làm phần mở rộng** (khôi phục quản lý tài khoản thủ thư + mở rộng quản lý độc giả) |
| UC25 | Admin quản lý danh mục thể loại/NXB | Đề bài chỉ yêu cầu trường thể loại/NXB trong sách |
| UC28 | Báo cáo tổng hợp cho admin | Nhánh nhỏ của chức năng 8 |

### Cần bổ sung/chỉnh trong tài liệu để khớp đề bài

1. UC05 (gợi ý AI): ghi rõ "lịch sử mượn ĐÃ ẨN thông tin nhạy cảm trước khi gửi AI" — đúng mục 5 đề bài.
2. UC15 (xử lý mượn): input bổ sung "kiểm tra thẻ độc giả hoạt động + sách còn bản" — đúng ràng buộc đề bài.
3. Các UC ngoài phạm vi nên đánh dấu "(Mở rộng)" để giảng viên thấy ranh giới với đề bài.

## QUYẾT ĐỊNH NGƯỜI DÙNG (2026-08-09)

- **UC23: ĐƯỢC GIỮ làm phần mở rộng** — khôi phục tính năng admin quản lý tài khoản thủ thư + mở rộng quản lý tài khoản độc giả (tạo/sửa/khoá/xoá, phân quyền). Hết mâu thuẫn với quyết định xoá trước đó.
- **MƯỢN/TRẢ/GIA HẠN: CHỈ THỦ THƯ (librarian)** — admin KHÔNG thao tác phiếu mượn (UC15-17 là của Thủ thư). Đã sửa: API /api/borrows chỉ nhận role librarian; menu web "Mượn/Trả sách" chỉ hiện với librarian.
- Các UC mở rộng khác (đăng ký, yêu cầu mượn/trả, lịch sử cá nhân, thông báo, danh mục, kiểm duyệt AI...): làm sau phần lõi 8+3, ưu tiên theo kế hoạch Đợt A-D.

### Kết luận

- Cốt lõi: tài liệu **ĐÚNG và đủ** với đề bài (phủ kín 8 chức năng quản lý + 3 chức năng AI).
- Nhưng có **9 use case mở rộng ngoài đề bài** — không sai về mặt phân tích, nhưng nếu code theo hết sẽ phình hệ thống và mâu thuẫn với quyết định xoá "quản lý tài khoản thủ thư" trước đó (UC23).
- Khuyến nghị: giữ tài liệu làm hồ sơ KT1 nhưng đánh dấu phần mở rộng; code chỉ ưu tiên 8+3, các UC ngoài làm sau khi đủ điểm lõi (hoặc bỏ bớt).
