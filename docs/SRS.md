# SRS — Đặc tả yêu cầu phần mềm
## Hệ thống quản lý thư viện có tích hợp AI (Đề tài 02)

> Dựa trên `hỗ trợ/DE_BAI.md` + `hỗ trợ/REQUIREMENTS_QA.md` + hiện trạng triển khai (api_docs 0.12.0).

## 1. Phạm vi

Web app quản lý thư viện trường học: quản lý sách, độc giả, mượn/trả/gia hạn/phạt, tra cứu, đặt trước, thống kê, xuất báo cáo và 3 chức năng AI (chatbot tra cứu, tóm tắt sách, gợi ý sách liên quan).

## 2. Actor

| Actor | Mô tả |
|---|---|
| Độc giả | Tra cứu, đặt trước, gửi yêu cầu mượn/trả/gia hạn, xem lịch sử/phạt, dùng AI |
| Thủ thư | Quản lý sách/độc giả, xử lý mượn/trả/gia hạn/phạt/đặt trước, thống kê, xuất báo cáo |
| Quản trị viên | Quản lý tài khoản/phân quyền, cấu hình thư viện/AI, danh mục, audit, backup/restore, báo cáo tổng hợp |

## 3. Yêu cầu chức năng

### 3.1 Chức năng quản lý (mục 3.1 đề bài)

| # | Chức năng | Đầu vào | Xử lý | Đầu ra |
|---|---|---|---|---|
| 1 | Đăng nhập, phân quyền 3 vai trò | username, password | Kiểm tra tài khoản (băm mật khẩu, trạng thái hoạt động), sinh JWT | Token + role + tên |
| 2 | Quản lý sách | mã, tên, tác giả, thể loại, NXB, năm, số lượng | CRUD, ràng buộc số lượng ≥ 0, không trùng mã | Danh mục sách |
| 3 | Quản lý độc giả | thông tin cá nhân, loại, trạng thái thẻ | CRUD, khoá/mở khoá thẻ, email unique | Hồ sơ độc giả |
| 4 | Mượn/trả/gia hạn/phạt | mã độc giả, sách, ngày | Kiểm tra thẻ hoạt động, sách còn, giới hạn; tự tính hạn trả, phạt quá hạn, thu phạt | Phiếu mượn, lịch sử phạt |
| 5 | Tra cứu sách | từ khoá, thể loại, trạng thái | Lọc theo tên/tác giả/thể loại/trạng thái còn-đang mượn | Danh sách sách khớp |
| 6 | Đặt trước sách | mã sách đang hết | Tạo phiếu đặt trước (không trùng, chỉ khi hết); xử lý khi sách về | Phiếu đặt trước, trạng thái |
| 7 | Thống kê | — | Đếm sách mượn nhiều, độc giả hoạt động, sách quá hạn | 3 báo cáo thống kê |
| 8 | Xuất danh sách/báo cáo | — | Sinh CSV (UTF-8 BOM) sách, phiếu mượn, báo cáo | File CSV tải về |

### 3.2 Chức năng AI (mục 3.2 đề bài)

| # | Chức năng | Đầu vào | Xử lý | Đầu ra |
|---|---|---|---|---|
| AI-1 | Chatbot tra cứu sách | câu hỏi ngôn ngữ tự nhiên | Prompt kết hợp dữ liệu sách đã lọc (không bịa) | Gợi ý ≤ 5 sách + lý do |
| AI-2 | Tóm tắt sách | mô tả/mục lục/đoạn giới thiệu | Prompt tóm tắt riêng | Tóm tắt ngắn đúng nội dung |
| AI-3 | Gợi ý sách liên quan | thể loại, tác giả, lịch sử mượn đã ẩn nhạy cảm | Prompt gợi ý riêng | Danh sách sách đề xuất + lý do |

## 4. Yêu cầu phi chức năng

- **Bảo mật:** mật khẩu hash, JWT, phân quyền chặt theo vai trò (API 401/403), API key AI do Backend giữ, không lộ.
- **Quyền riêng tư:** lịch sử mượn gửi AI phải ẩn thông tin cá nhân độc giả; độc giả chỉ xem dữ liệu của mình.
- **Hiệu năng:** phản hồi API trong vài giây với dữ liệu demo; AI có timeout/xử lý lỗi.
- **Khả dụng:** giao diện rõ ràng, thông báo lỗi thân thiện, không crash.
- **Sao lưu:** backup/restore CSDL qua admin.
- **Trải nghiệm:** UI theo UI_DESIGN.md (WCAG 2.1 AA+), dùng được trên desktop/browser.

## 5. Ràng buộc nghiệp vụ

- Không cho mượn khi sách còn 0; số lượng không âm.
- Thẻ độc giả khoá thì không mượn được.
- Gia hạn tối đa 1 lần; từ chối gia hạn nếu có người đặt trước.
- Đặt trước chỉ khi sách hết/đang mượn hết; không đặt trùng.
- Phạt = số ngày quá hạn × phạt/ngày (cấu hình admin).
- Admin không thao tác mượn/trả/đặt trước (chỉ thủ thư).
