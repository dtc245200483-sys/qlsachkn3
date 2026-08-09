# Đề tài: Hệ thống quản lý thư viện có tích hợp AI

## 1. Mô tả bài toán

Thư viện trường học hoặc thư viện nội bộ cần quản lý sách, độc giả, mượn trả, gia hạn, phạt trễ hạn và tra cứu tài liệu. Cách quản lý thủ công làm khó kiểm soát sách đang mượn, sách quá hạn và nhu cầu đọc của độc giả. Đề tài yêu cầu xây dựng hệ thống quản lý thư viện có chức năng AI hỗ trợ tra cứu sách, gợi ý sách và tóm tắt nội dung mô tả sách cho độc giả.

## 2. Mục tiêu

- Xây dựng hệ thống quản lý sách, độc giả, phiếu mượn/trả, quá hạn và thống kê thư viện.
- Tích hợp AI tạo sinh để hỗ trợ tìm sách bằng ngôn ngữ tự nhiên, gợi ý sách và tóm tắt nội dung.
- Sử dụng AI trong SDLC để phân tích nghiệp vụ thư viện, thiết kế CSDL, sinh API, giao diện, test case và tài liệu.
- Đảm bảo hệ thống dễ sử dụng cho thủ thư và độc giả.

## 3. Yêu cầu chức năng

### 3.1. Chức năng quản lý

1. Đăng nhập, phân quyền thủ thư, độc giả, quản trị viên.
2. Quản lý sách: mã sách, tên, tác giả, thể loại, nhà xuất bản, năm xuất bản, số lượng.
3. Quản lý độc giả: thông tin cá nhân, loại độc giả, trạng thái thẻ.
4. Quản lý mượn sách, trả sách, gia hạn và tính phạt quá hạn.
5. Tra cứu sách theo tên, tác giả, thể loại, trạng thái còn/đang mượn.
6. Quản lý đặt trước sách nếu sách đang được mượn.
7. Thống kê sách mượn nhiều, độc giả hoạt động, sách quá hạn.
8. Xuất danh sách sách, phiếu mượn và báo cáo thư viện.

### 3.2. Chức năng AI

1. Chatbot tra cứu sách: độc giả hỏi bằng ngôn ngữ tự nhiên, AI gợi ý sách phù hợp từ dữ liệu thư viện.
2. AI tóm tắt sách: sinh tóm tắt ngắn từ mô tả, mục lục hoặc đoạn giới thiệu sách.
3. AI gợi ý sách liên quan dựa trên thể loại, tác giả và lịch sử mượn.

## 4. Yêu cầu kỹ thuật

- Backend: Python FastAPI/Flask/Django.
- Frontend: React/Vue/HTML hoặc template engine.
- CSDL: SQLite/MySQL/PostgreSQL.
- AI Engine: OpenAI/Gemini/Claude/Hugging Face/Ollama.
- Có prompt template riêng cho tra cứu, tóm tắt và gợi ý.
- Khuyến khích dùng embedding hoặc tìm kiếm full-text cho tra cứu sách.
- Có test cho mượn/trả, quá hạn và chatbot tra cứu.

## 5. Dữ liệu đầu vào, đầu ra và dữ liệu hệ thống

- Dữ liệu chính: sách, tác giả, thể loại, độc giả, phiếu mượn, chi tiết mượn, lịch sử phạt.
- Đầu vào quản lý: thông tin sách, độc giả, phiếu mượn/trả, ngày gia hạn.
- Đầu vào AI: câu hỏi tra cứu, mô tả sách, lịch sử mượn đã ẩn thông tin nhạy cảm.
- Đầu ra quản lý: danh sách sách, phiếu mượn, trạng thái sách, báo cáo.
- Đầu ra AI: danh sách sách gợi ý, tóm tắt sách, giải thích lý do gợi ý.

Ví dụ dữ liệu mẫu: `Sách: Nhập môn trí tuệ nhân tạo, tác giả Nguyễn Văn A, thể loại Công nghệ, còn 3 bản`.

Prompt mẫu:

System: Bạn là trợ lý tra cứu thư viện. Chỉ gợi ý sách có trong dữ liệu được cung cấp. Không bịa mã sách hoặc tình trạng sách.
User: Tôi muốn tìm sách dễ đọc về trí tuệ nhân tạo cho người mới bắt đầu. Dữ liệu sách: {{book_list}}. Hãy gợi ý tối đa 5 cuốn, kèm lý do.

Không gửi dữ liệu cá nhân độc giả cho AI nếu chức năng chỉ cần dữ liệu sách.

## 6. Hướng dẫn sử dụng AI trong từng giai đoạn SDLC

### Giai đoạn 1: Phân tích yêu cầu và thiết kế hệ thống (Bài KT1)

- Dùng AI phân tích nghiệp vụ mượn/trả, gia hạn, đặt trước, phạt quá hạn.
- Dùng AI sinh use case cho thủ thư, độc giả và quản trị viên.
- Dùng AI thiết kế ERD và ràng buộc số lượng sách còn lại.
- Dùng AI xác định chức năng AI phù hợp: tra cứu, tóm tắt, gợi ý.
- Dùng AI sinh prototype trang tra cứu sách và trang quản lý mượn trả.

### Giai đoạn 2: Xây dựng chức năng quản lý (Bài KT2)

- Dùng AI sinh model, API và giao diện CRUD sách, độc giả, phiếu mượn.
- Dùng AI sinh logic kiểm tra số lượng sách còn, quá hạn và phạt.
- Dùng AI sinh truy vấn thống kê sách mượn nhiều, sách quá hạn.
- Dùng AI debug lỗi ràng buộc khi trả sách hoặc gia hạn.

### Giai đoạn 3: Tích hợp AI, tối ưu prompt và kiểm thử (Bài KT3)

- Dùng AI thiết kế prompt tra cứu sách không bịa dữ liệu.
- Dùng AI sinh code kết hợp tìm kiếm CSDL với lời giải thích của LLM.
- Dùng AI tạo test case cho câu hỏi mơ hồ, sách không tồn tại, sách hết.
- Thử nghiệm ít nhất 3 prompt để cải thiện độ đúng của gợi ý sách.

### Giai đoạn 4: Hoàn thiện, triển khai và báo cáo (Bài thi cuối kỳ)

- Dùng AI sinh hướng dẫn sử dụng cho thủ thư và độc giả.
- Dùng AI review luồng bảo mật dữ liệu độc giả.
- Dùng AI tạo báo cáo kỹ thuật và slide demo.
- Dùng AI hỗ trợ đóng gói ứng dụng và tạo dữ liệu mẫu.

## 7. Mức độ khó

Cơ bản: Nghiệp vụ rõ ràng, số lượng thực thể vừa phải. Chức năng AI có thể triển khai bằng prompt kết hợp dữ liệu sách đã lọc, chưa bắt buộc RAG hoặc xử lý dữ liệu lớn.
