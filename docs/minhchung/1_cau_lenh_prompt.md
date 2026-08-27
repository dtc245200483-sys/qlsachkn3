# Minh chứng 2.9 (Phần 1): Các câu lệnh (Prompt) gửi cho AI

Thay vì đưa cho AI những yêu cầu chung chung như "hãy viết phần mềm quản lý thư viện", tôi đã đóng vai trò là một System Architect để chia nhỏ bài toán, thiết lập các Agent (Tác tử) với những Prompt (Câu lệnh) chứa quy tắc ràng buộc cực kỳ khắt khe, bám sát nghiệp vụ thực tế.

Dưới đây là minh chứng các Prompt gốc được trích xuất trực tiếp từ mã nguồn dự án:

## 1. Prompt điều khiển Backend Agent
*File trích xuất: `Backend/AGENTS.md`*

Tôi đã thiết lập các ràng buộc bắt buộc về nghiệp vụ kế toán thư viện và bảo mật dữ liệu nhạy cảm (PII), buộc AI phải tuân thủ khi sinh code:

> **Trích nguyên văn Prompt:**
> "BẮT BUỘC:
> 1. Không cho mượn khi số lượng sách còn = 0; số lượng không được âm.
> 2. Tự động tính phạt trễ hạn theo công thức người dùng xác nhận.
> 3. Đặt trước chỉ áp dụng khi sách đang hết/đang mượn hết.
> 4. Phân quyền chặt: độc giả không gọi được API quản trị.
> 5. API cấp cho AI Engine PHẢI lọc bỏ dữ liệu cá nhân độc giả (chỉ giữ những gì AI thật sự cần — đúng mục 5: 'đã ẩn thông tin nhạy cảm').
> 6. Có unit test/integration test cho: mượn/trả, tính quá hạn/phạt (đúng yêu cầu kỹ thuật mục 4). Không tự tạo dữ liệu mẫu nếu không được yêu cầu.
> 7. Mọi thay đổi schema phải có migration, không sửa tay DB."

## 2. Prompt điều khiển Frontend Agent
*File trích xuất: `frontend/AGENTS.md`*

Tôi đã ra lệnh cấm AI sử dụng các framework UI tạo sẵn để đảm bảo khả năng tùy biến sâu, đồng thời bắt buộc xử lý lỗi API trên màn hình một cách trực quan:

> **Trích nguyên văn Prompt:**
> "PHẠM VI: Chỉ code trong thư mục Frontend. Công nghệ: React/Vue/HTML-CSS-JS/template engine theo lựa chọn người dùng khi bắt đầu, không tự đổi...
> BẮT BUỘC:
> 1. Chỉ làm đúng phần UI được giao trong lượt, không tự thêm màn hình ngoài phạm vi.
> 2. Khi Backend chưa có API, dùng dữ liệu mock tạm và ghi rõ chỗ sẽ nối API.
> 3. Phân quyền ở màn hình: độc giả không nhìn thấy/không dùng được chức năng quản trị.
> 4. Hiển thị rõ lỗi API: sách hết, thẻ khóa, quá hạn, không có kết quả tra cứu.
> 5. Tự chạy checklist trước khi báo xong."

## 3. Prompt điều khiển AI Engine Agent
*File trích xuất: `ai_engine/AI_ENGINE_AGENT.md`*

Vì AI sinh text dễ bị tình trạng "ảo giác" (hallucination - bịa dữ liệu), tôi đã tạo System Prompt bắt buộc đóng khung dữ liệu:

> **Trích nguyên văn Prompt:**
> "PROMPT TEMPLATE BẮT BUỘC DÙNG LÀM GỐC:
> System: 'Bạn là trợ lý tra cứu thư viện. Chỉ gợi ý sách có trong dữ liệu được cung cấp. Không bịa mã sách hoặc tình trạng sách.'
> User mẫu: 'Tôi muốn tìm sách dễ đọc về <chủ đề> cho người mới bắt đầu. Dữ liệu sách: {{book_list}}. Hãy gợi ý tối đa 5 cuốn, kèm lý do.'
>
> BẮT BUỘC:
> 1. Không bịa mã sách hoặc tình trạng sách ngoài dữ liệu Backend cung cấp.
> 2. Không gửi dữ liệu cá nhân độc giả cho AI nếu chức năng chỉ cần dữ liệu sách (VD: chatbot tra cứu, tóm tắt sách → không cần lịch sử mượn).
> 3. Có test case cho: câu hỏi mơ hồ, sách không tồn tại, sách hết."

---
**Kết luận Phần 1:** 
Bằng cách xây dựng các System Prompt sắc bén, tôi đã kiểm soát được đầu vào của AI, ngăn chặn việc AI sinh code tràn lan, tự tạo dữ liệu giả rác, hoặc vi phạm luồng nghiệp vụ thư viện.