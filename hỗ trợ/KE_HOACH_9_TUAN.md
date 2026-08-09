# Kế hoạch thực hiện — Hệ thống quản lý thư viện có tích hợp AI

## Thông tin nhóm

- Nhóm 02 — Thành viên: Phạm Vũ Quang Hưng, Trần Thị Thu Huyền
- Lớp: CNTT K23C — Trường Đại học Công nghệ thông tin và Truyền thông (ICTU) — Khoa Công nghệ thông tin
- Tên ứng dụng: Hệ thống quản lý thư viện có tích hợp AI
- Thời gian thực hiện: 27/07/2026 – 27/09/2026 (9 tuần)

## Phạm vi và thông tin đầu vào/đầu ra

- Dữ liệu chính: sách, tác giả, thể loại, độc giả, phiếu mượn, chi tiết mượn, lịch sử phạt.
- Đầu vào quản lý: thông tin sách, độc giả, phiếu mượn/trả, ngày gia hạn.
- Đầu vào AI: câu hỏi tra cứu, mô tả sách, lịch sử mượn đã ẩn thông tin nhạy cảm.
- Đầu ra quản lý: danh sách sách, phiếu mượn, trạng thái sách, báo cáo.
- Đầu ra AI: danh sách sách gợi ý, tóm tắt sách, giải thích lý do gợi ý.

## Kế hoạch chi tiết

| Tuần | Công việc | Thành viên thực hiện | Ghi chú |
|---|---|---|---|
| Tuần 01 (27/07–02/08) | Khảo sát bài toán, xác định phạm vi và mục tiêu dự án | Cả nhóm | Cùng khảo sát, thống nhất phạm vi, mục tiêu |
| Tuần 01 | Dùng AI phân tích nghiệp vụ mượn/trả, gia hạn, đặt trước và phạt quá hạn | Phạm Vũ Quang Hưng | Phân tích luồng nghiệp vụ |
| Tuần 01 | Dùng AI xác định chức năng AI phù hợp: tra cứu, tóm tắt, gợi ý sách | Trần Thị Thu Huyền | Đề xuất và chốt chức năng AI |
| Tuần 01 | Thiết lập môi trường làm việc chung, cấu trúc dự án và Git | Cả nhóm | Chuẩn bị công cụ phát triển, phân chia công việc |
| Tuần 01 | Lập danh sách tài liệu tham khảo và biểu mẫu CSDL ban đầu | Trần Thị Thu Huyền | Thu thập tài liệu, chuẩn bị biểu mẫu |
| Tuần 02 (03/08–09/08) | Dùng AI sinh use case cho thủ thư, độc giả và quản trị viên | Phạm Vũ Quang Hưng | Viết use case cho thủ thư và quản trị viên |
| Tuần 02 | Dùng AI thiết kế ERD và ràng buộc số lượng sách còn lại | Trần Thị Thu Huyền | Thiết kế ERD và ràng buộc dữ liệu |
| Tuần 02 | Dùng AI sinh prototype trang tra cứu sách và trang quản lý mượn trả | Cả nhóm | Cùng dựng prototype |
| Tuần 02 | Tinh chỉnh giao diện prototype dựa trên trải nghiệm người dùng | Phạm Vũ Quang Hưng | Tối ưu bố cục trang chính |
| Tuần 02 | Kiểm tra tính toàn vẹn mô hình CSDL sơ bộ | Trần Thị Thu Huyền | Rà soát quan hệ ERD |
| Tuần 03 (10/08–16/08) | Hoàn thiện đặc tả yêu cầu và thiết kế hệ thống | Trần Thị Thu Huyền | Hoàn thiện tài liệu đặc tả yêu cầu |
| Tuần 03 | Rà soát, chỉnh sửa prototype theo góp ý | Phạm Vũ Quang Hưng | Rà soát và chỉnh sửa prototype |
| Tuần 03 | Tổng hợp và hoàn thiện báo cáo giai đoạn 1 | Cả nhóm | Phối hợp rà soát tài liệu thiết kế |
| Tuần 03 | Đóng gói hồ sơ minh chứng, tài liệu chuẩn bị nộp | Trần Thị Thu Huyền | Chuẩn bị file theo định dạng yêu cầu |
| Tuần 03 | Nộp Bài KT1 (Phân tích yêu cầu và thiết kế hệ thống) | Cả nhóm | Deliverable Bài KT1 |
| Tuần 04 (17/08–23/08) | Dùng AI sinh model, API và giao diện CRUD sách, độc giả | Phạm Vũ Quang Hưng | Xây dựng model, API, giao diện quản lý sách/độc giả |
| Tuần 04 | Dùng AI sinh model, API và giao diện CRUD phiếu mượn | Trần Thị Thu Huyền | Xây dựng model, API, giao diện quản lý phiếu mượn |
| Tuần 04 | Dùng AI sinh logic kiểm tra số lượng sách còn, quá hạn và phạt | Phạm Vũ Quang Hưng | Logic kiểm tra số lượng, quá hạn, tính phạt |
| Tuần 04 | Kiểm tra kết nối CSDL và cấu hình ORM | Trần Thị Thu Huyền | Đảm bảo bảng liên kết hoạt động ổn định |
| Tuần 04 | Viết Unit Test cơ bản cho các API CRUD cốt lõi | Phạm Vũ Quang Hưng | Kiểm tra độ chính xác dữ liệu trả về |
| Tuần 05 (24/08–30/08) | Xây dựng chức năng mượn sách, trả sách, gia hạn | Trần Thị Thu Huyền | Hoàn thiện mượn, trả, gia hạn |
| Tuần 05 | Xây dựng chức năng đặt trước sách khi sách đang mượn | Phạm Vũ Quang Hưng | Xây dựng đặt trước sách |
| Tuần 05 | Dùng AI sinh truy vấn thống kê: sách mượn nhiều, độc giả hoạt động, sách quá hạn | Trần Thị Thu Huyền | Viết truy vấn thống kê |
| Tuần 05 | Dùng AI debug lỗi ràng buộc khi trả sách hoặc gia hạn | Phạm Vũ Quang Hưng | Debug ràng buộc mượn/trả |
| Tuần 05 | Kiểm thử luồng nghiệp vụ mượn trả toàn diện | Cả nhóm | Chạy thử kịch bản thực tế |
| Tuần 06 (31/08–06/09) | Hoàn thiện quản lý, xuất danh sách sách, phiếu mượn và báo cáo | Cả nhóm | Hoàn thiện và xuất báo cáo |
| Tuần 06 | Kiểm tra, sửa lỗi các chức năng quản lý | Trần Thị Thu Huyền | Kiểm tra và sửa lỗi |
| Tuần 06 | Tối ưu giao diện quản trị và Dashboard | Phạm Vũ Quang Hưng | Cải thiện tốc độ tải, hiển thị thống kê |
| Tuần 06 | Đóng gói, chuẩn bị tài liệu bàn giao chức năng quản lý cơ bản | Trần Thị Thu Huyền | Soạn hướng dẫn sử dụng phần quản lý |
| Tuần 06 | Nộp Bài KT2 (Xây dựng chức năng quản lý) | Cả nhóm | Deliverable Bài KT2 |
| Tuần 07 (07/09–13/09) | Dùng AI thiết kế prompt tra cứu sách không bịa dữ liệu | Phạm Vũ Quang Hưng | Thiết kế prompt, ràng buộc không bịa dữ liệu |
| Tuần 07 | Xây dựng chatbot tra cứu sách bằng ngôn ngữ tự nhiên | Trần Thị Thu Huyền | Xây dựng chatbot |
| Tuần 07 | Xây dựng AI tóm tắt sách và gợi ý sách liên quan | Cả nhóm | Cùng xây dựng tóm tắt và gợi ý |
| Tuần 07 | Tích hợp API dịch vụ AI vào backend chính | Phạm Vũ Quang Hưng | Kết nối module AI với CSDL sách |
| Tuần 07 | Kiểm tra độ trễ phản hồi của tính năng tích hợp AI | Trần Thị Thu Huyền | Đánh giá thời gian phản hồi AI |
| Tuần 08 (14/09–20/09) | Thử nghiệm ít nhất 3 prompt để cải thiện độ đúng gợi ý sách | Phạm Vũ Quang Hưng | Thử nghiệm và so sánh prompt |
| Tuần 08 | Dùng AI tạo test case: câu hỏi mơ hồ, sách không tồn tại, sách hết | Trần Thị Thu Huyền | Viết test case |
| Tuần 08 | Kiểm thử mượn/trả, quá hạn và chatbot tra cứu | Cả nhóm | Kiểm thử tích hợp |
| Tuần 08 | Khắc phục lỗi phát sinh trong kiểm thử tích hợp AI | Phạm Vũ Quang Hưng | Xử lý ngoại lệ chatbot |
| Tuần 08 | Nộp Bài KT3 (Tích hợp AI, tối ưu prompt và kiểm thử) | Cả nhóm | Deliverable Bài KT3 |
| Tuần 09 (21/09–27/09) | Dùng AI sinh hướng dẫn sử dụng cho thủ thư và độc giả | Trần Thị Thu Huyền | Viết hướng dẫn sử dụng |
| Tuần 09 | Dùng AI review luồng bảo mật dữ liệu độc giả | Phạm Vũ Quang Hưng | Review bảo mật |
| Tuần 09 | Dùng AI tạo báo cáo kỹ thuật và slide demo | Cả nhóm | Chuẩn bị báo cáo, slide |
| Tuần 09 | Chạy thử (Dry-run) toàn bộ hệ thống trước ngày bảo vệ | Cả nhóm | Kiểm tra kịch bản demo |
| Tuần 09 | Đóng gói ứng dụng, tạo dữ liệu mẫu, nộp Bài thi cuối kỳ | Cả nhóm | Deliverable Bài thi cuối kỳ |
