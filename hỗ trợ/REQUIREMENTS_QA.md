# THU THẬP, LÀM RÕ YÊU CẦU CỦA ỨNG DỤNG

Nhóm 02 — Thành viên: Phạm Vũ Quang Hưng (Trưởng nhóm), Trần Thị Thu Huyền
Tên ứng dụng: Hệ thống quản lý thư viện có tích hợp AI
Thời gian thực hiện: 27/07/2026 – 27/09/2026 (9 tuần)

## Danh sách câu hỏi thu thập và làm rõ yêu cầu

| STT | Câu hỏi | Trả lời | Ghi chú |
|---|---|---|---|
| 1 | [Nghiệp vụ] Phạm vi demo có bao gồm đầy đủ quản lý sách, độc giả, mượn/trả, gia hạn, phạt quá hạn, đặt trước, tra cứu, thống kê và xuất báo cáo không? | Đã trả lời: đề tài nêu các nhóm chức năng này là phạm vi chính | Theo đề tài; SRS: Scope/Functional overview |
| 2 | [Nghiệp vụ] Quy trình mượn/trả xử lý bước nào: chọn sách, kiểm tra thẻ, kiểm tra sách còn bản, lập phiếu mượn, trả, gia hạn, tính phạt? | Đã trả lời một phần: đề tài nêu chức năng; chi tiết luồng chưa mô tả | Cần xác nhận; ảnh hưởng use case mượn/trả |
| 3 | [Actor/Phân quyền] Actor chính có phải thủ thư, độc giả, quản trị viên? | Đã trả lời: 3 vai trò theo đề tài | Theo đề tài |
| 4 | [Actor/Phân quyền] Từng vai trò truy cập module nào? | Chưa trả lời | Cần chốt ma trận phân quyền |
| 5 | [Quản lý sách] Ngoài mã sách, tên, tác giả, thể loại, NXB, năm, số lượng còn trường bắt buộc nào? | Đã trả lời một phần: trường chính theo đề tài; mô tả sách dùng cho AI tóm tắt | Cần xác nhận; ảnh hưởng form/CSDL |
| 6 | [Quản lý độc giả] Lưu thông tin cá nhân, loại độc giả, trạng thái thẻ ở mức chi tiết nào? | Đã trả lời một phần: đề tài nêu nhóm dữ liệu, chưa nêu trường chi tiết và quy tắc bảo vệ | Cần xác nhận; ảnh hưởng quyền riêng tư |
| 7 | [Mượn/trả] Phiếu mượn ghi nhận sách, độc giả, ngày mượn, hạn trả, gia hạn, phạt như thế nào? | Chưa trả lời | Ảnh hưởng trường phiếu mượn và kiểm soát quá hạn |
| 8 | [Thống kê/Báo cáo] Thống kê gồm sách mượn nhiều, độc giả hoạt động, sách quá hạn và xuất PDF/Excel/CSV? | Đã trả lời: đề tài nêu 3 nhóm thống kê và xuất báo cáo | Theo đề tài; SRS: Reporting/data export |
| 9 | [Tra cứu] Màn hình tra cứu hỗ trợ tìm/lọc theo tên, tác giả, thể loại, trạng thái còn/đang mượn? | Đã trả lời: đề tài nêu đầy đủ tiêu chí | Theo đề tài; SRS: Search module |
| 10 | [AI] Chatbot chỉ gợi ý sách có trong dữ liệu, tối đa 5 cuốn kèm lý do, không bịa mã/tình trạng? | Đã trả lời: prompt mẫu đề tài yêu cầu như vậy | Theo đề tài; SRS: AI guardrail |
| 11 | [AI] Tóm tắt dùng mô tả/mục lục/đoạn giới thiệu, trả tóm tắt ngắn đúng nội dung? | Đã trả lời: đề tài nêu nguồn và đầu ra | Theo đề tài; SRS: AI summarization |
| 12 | [AI] Gợi ý liên quan dựa trên thể loại, tác giả và lịch sử mượn đã ẩn thông tin nhạy cảm? | Đã trả lời một phần: 3 tiêu chí; cơ chế ẩn chưa chi tiết | Cần xác nhận; ảnh hưởng bảo mật |
| 13 | [AI] Xử lý AI khi timeout, rate limit, response rỗng/sai định dạng/hallucination hiển thị thế nào? | Chưa trả lời | Liên quan thử nghiệm ≥3 prompt và test mơ hồ/không tồn tại/hết sách |
| 14 | [Dữ liệu nhạy cảm] Ngoài nguyên tắc không gửi dữ liệu cá nhân khi không cần, còn dữ liệu nào bị cấm/cần ẩn danh? | Đã trả lời một phần: đề tài yêu cầu không gửi dữ liệu cá nhân nếu chỉ cần dữ liệu sách | Cần xác nhận; nguyên tắc tối thiểu dữ liệu |
| 15 | [Ràng buộc nghiệp vụ] Xử lý khi mượn vượt số lượng còn, gia hạn quá số lần cho phép, độc giả quá hạn? | Chưa trả lời | Business rule trọng yếu |
| 16 | [Ngoại lệ] Kiểm soát lỗi: mã sách trùng, số lượng âm, độc giả không tồn tại, thẻ khóa, ngày không hợp lệ? | Chưa trả lời | Ảnh hưởng validation và test biên |
| 17 | [Hiệu năng] Stack kỹ thuật cuối cùng: FastAPI/Flask/Django, React/Vue/HTML-CSS-JS, SQLite/MySQL/PostgreSQL? | Chưa trả lời | Đề tài cho phép nhiều lựa chọn |
| 18 | [Hiệu năng] Yêu cầu hiệu năng demo: số sách/độc giả/phiếu mượn, thời gian phản hồi tra cứu/AI? | Chưa trả lời | Liên quan tiêu chí hiệu năng/ổn định |
| 19 | [Triển khai] Chạy local/cloud, có Docker, sao lưu/khôi phục CSDL mức nào? | Đã trả lời một phần: đề tài cho phép local/cloud; chưa rõ sao lưu | Cần xác nhận |
| 20 | [Phạm vi chưa rõ] Có yêu cầu ngoài đề tài: nhà cung cấp sách, báo cáo lợi nhuận, in phiếu mượn, thông báo đẩy? | Chưa trả lời | Không tự thêm yêu cầu ngoài đề tài |

## Tóm tắt yêu cầu dự kiến (không thay thế SRS)

- Quản lý đăng nhập/đăng xuất và phân quyền cho thủ thư, độc giả, quản trị viên.
- Quản lý sách, độc giả, phiếu mượn/trả, gia hạn, phạt quá hạn, đặt trước, tra cứu, thống kê và xuất báo cáo.
- Chức năng AI: chatbot tra cứu sách, AI tóm tắt sách, AI gợi ý sách liên quan.

## Vấn đề cần xác minh trước khi viết SRS

- Công nghệ cuối cùng, môi trường demo local/cloud, lựa chọn CSDL và AI Engine.
- Ma trận phân quyền chi tiết theo vai trò và module.
- Quy tắc phạt quá hạn, gia hạn, đặt trước và ràng buộc số lượng sách còn lại.
- Giới hạn bảo mật, ẩn danh dữ liệu khi gọi AI, xử lý lỗi AI và tiêu chí hiệu năng/sao lưu.

## Sơ đồ phân cấp chức năng

1. Quản trị hệ thống — 1.1 Đăng nhập/đăng xuất; 1.2 Quản lý người dùng, vai trò và phân quyền
2. Quản lý dữ liệu nền — 2.1 Quản lý sách; 2.2 Quản lý độc giả
3. Nghiệp vụ mượn/trả — 3.1 Mượn sách, trả sách; 3.2 Gia hạn và tính phạt quá hạn; 3.3 Đặt trước sách
4. Tra cứu, thống kê và xuất dữ liệu — 4.1 Tra cứu sách; 4.2 Thống kê thư viện; 4.3 Xuất danh sách sách, phiếu mượn, báo cáo
5. Chức năng AI — 5.1 Chatbot tra cứu sách; 5.2 AI tóm tắt sách; 5.3 AI gợi ý sách liên quan
