# Tiêu chí đánh giá (Bài kiểm tra thường xuyên 1) + Quy tắc làm việc

## 10 tiêu chí đánh giá

1. Phân tích đúng bài toán quản lý: xác định rõ bối cảnh, người dùng, dữ liệu, quy trình nghiệp vụ và vấn đề cần giải quyết.
2. Xác định đầy đủ yêu cầu chức năng: liệt kê chức năng quản lý cốt lõi phù hợp đề tài, có mô tả đầu vào, xử lý và đầu ra.
3. Xác định yêu cầu phi chức năng: bảo mật, hiệu năng, khả dụng, sao lưu, phân quyền và trải nghiệm người dùng.
4. Thiết kế actor và use case: actor chính, use case chính, có sơ đồ Use Case hoặc mô tả tương đương.
5. Thiết kế CSDL: ERD, bảng dữ liệu, khóa chính/khóa ngoại, ràng buộc và giải thích quan hệ.
6. Thiết kế kiến trúc hệ thống: frontend, backend, database, AI service và luồng dữ liệu chính.
7. Xác định vị trí ứng dụng AI: chọn chức năng AI hợp lý, gắn với dữ liệu và nhu cầu thực tế.
8. Thiết kế prompt và luồng gọi AI sơ bộ: system prompt, user prompt mẫu, input/output format, ràng buộc và giới hạn.
9. Minh chứng sử dụng AI trong phân tích và thiết kế: lưu prompt, phản hồi AI và nhận xét cách kiểm chứng/chỉnh sửa kết quả.
10. Tài liệu phân tích thiết kế: rõ ràng, có cấu trúc, có kế hoạch triển khai các giai đoạn tiếp theo.

## Quy tắc thực hiện (từ file điều kiện)

- KHÔNG hoàn thành tất cả: không tự ý viết toàn bộ dự án hay giải quyết toàn bộ 10 tiêu chí cùng một lúc.
- TỰ đối chiếu tiêu chí: phân tích yêu cầu hiện tại liên quan tiêu chí nào để tối ưu điểm.
- CHỈ làm đúng phạm vi: chỉ xử lý đúng và đủ yêu cầu giao ở phần này, sau đó dừng và chờ yêu cầu phần tiếp theo.

## Thông tin nhóm

- Thành viên: Phạm Vũ Quang Hưng, Trần Thị Thu Huyền
- Lớp: CNTT K23C — Trường Đại học Công nghệ thông tin và Truyền thông (ICTU) — Khoa Công nghệ thông tin

---

## Bài kiểm tra thường xuyên 2 (KT2) — 10 tiêu chí

1. Cấu trúc dự án hợp lý: Dự án tổ chức rõ ràng theo frontend/backend/database/config/docs hoặc cấu trúc phù hợp framework.
2. Xây dựng chức năng đăng nhập và phân quyền: Có xác thực người dùng, phân quyền vai trò và bảo vệ các chức năng quan trọng.
3. Hoàn thiện CRUD nghiệp vụ chính: Các chức năng thêm, xem, sửa, xóa dữ liệu chính hoạt động đúng.
4. Xây dựng chức năng tìm kiếm và lọc: Cho phép tìm kiếm, lọc, sắp xếp dữ liệu theo tiêu chí phù hợp.
5. Xây dựng thống kê/báo cáo cơ bản: Có báo cáo hoặc dashboard phục vụ nghiệp vụ của hệ thống.
6. Thiết kế giao diện rõ ràng, dễ sử dụng: Giao diện nhất quán, dễ thao tác, có thông báo lỗi và phản hồi người dùng.
7. Kết nối và thao tác CSDL ổn định: Lưu, đọc, cập nhật, xóa dữ liệu chính xác; có dữ liệu mẫu để demo.
8. Xử lý lỗi cơ bản: Xử lý input sai, dữ liệu thiếu, lỗi truy vấn, lỗi phân quyền; không để ứng dụng crash.
9. Minh chứng sử dụng AI khi lập trình: Có nhật ký prompt, phản hồi AI, phần code được hỗ trợ và phần sinh viên đã kiểm tra/chỉnh sửa.
10. Quản lý mã nguồn và tài liệu chạy thử: Có README, hướng dẫn cài đặt/chạy, .env.example, commit rõ ràng.

## Bài kiểm tra thường xuyên 3 (KT3) — 10 tiêu chí

1. Tích hợp được chức năng AI vào hệ thống: Chức năng AI chạy trong hệ thống, phục vụ nghiệp vụ cụ thể, không tách rời sản phẩm.
2. Kết nối API/model AI đúng cách: Gọi được OpenAI/Gemini/Claude/Hugging Face/Ollama hoặc mô hình tương đương; bảo vệ API key.
3. Thiết kế prompt có hệ thống: Prompt tách khỏi code, có system/user prompt, ràng buộc output và hướng dẫn xử lý dữ liệu.
4. Tối ưu prompt qua thử nghiệm: Có ít nhất 3 vòng thử nghiệm hoặc so sánh prompt/model, ghi nhận kết quả và cải tiến.
5. Sử dụng dữ liệu hệ thống trong chức năng AI: AI khai thác dữ liệu phù hợp từ CSDL, file hoặc báo cáo; có kiểm soát quyền truy cập dữ liệu.
6. Hiển thị kết quả AI rõ ràng: Kết quả AI được trình bày dễ hiểu, có định dạng phù hợp và có cảnh báo khi cần.
7. Xử lý lỗi và giới hạn AI: Xử lý timeout, rate limit, response rỗng/sai định dạng, dữ liệu quá dài, lỗi model.
8. Kiểm thử chức năng quản lý và chức năng AI: Có test case, manual test hoặc script test; bao gồm trường hợp đúng, sai và biên.
9. Review code và cải thiện chất lượng bằng AI: Có minh chứng dùng AI để review code, phát hiện lỗi, refactor hoặc cải thiện bảo mật.
10. Tích hợp chức năng AI với trải nghiệm người dùng: Luồng sử dụng AI tự nhiên, hữu ích, không gây nhầm lẫn với chức năng quản lý chính.

## Thi kết thúc học phần — 10 tiêu chí

1. Hoàn thiện chức năng hệ thống: Các chức năng quản lý và chức năng AI hoạt động đầy đủ, ổn định, đúng yêu cầu.
2. Chất lượng kiến trúc và mã nguồn: Code rõ ràng, module hóa, dễ bảo trì, tuân thủ quy ước của framework/ngôn ngữ.
3. Chất lượng cơ sở dữ liệu: CSDL hợp lý, dữ liệu nhất quán, có ràng buộc, dữ liệu mẫu và khả năng sao lưu/khôi phục cơ bản.
4. Chất lượng giao diện và trải nghiệm người dùng: Giao diện dễ dùng, nhất quán, responsive ở mức phù hợp, có phản hồi thao tác và thông báo lỗi.
5. Chất lượng chức năng AI: Kết quả AI hữu ích, đúng ngữ cảnh, có kiểm soát sai lệch, có giới hạn và cảnh báo rõ.
6. Bảo mật, quyền riêng tư và đạo đức AI: Bảo vệ tài khoản, phân quyền dữ liệu, không lộ API key, cân nhắc dữ liệu nhạy cảm khi gọi AI.
7. Hiệu năng và độ ổn định: Ứng dụng phản hồi hợp lý, xử lý được dữ liệu demo, có cơ chế tránh lỗi lặp lại hoặc lỗi do AI.
8. Triển khai và đóng gói: Có hướng dẫn triển khai, cấu hình môi trường, dữ liệu mẫu; khuyến khích Docker hoặc cloud demo.
9. Báo cáo kỹ thuật đầy đủ: Báo cáo mô tả phân tích, thiết kế, triển khai, kiểm thử, chức năng AI và vai trò của AI trong SDLC.
10. Thuyết trình và demo: Demo mạch lạc, trình bày rõ chức năng quản lý, chức năng AI, minh chứng sử dụng AI và trả lời câu hỏi tốt.
