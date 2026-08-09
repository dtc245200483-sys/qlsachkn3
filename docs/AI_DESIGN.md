# Thiết kế chức năng AI

## 1. Vị trí AI trong hệ thống

- AI Engine là **actor phụ** (UC03/04/05): được hệ thống gọi, không tự truy vấn CSDL.
- Frontend **không gọi thẳng** nhà cung cấp AI — mọi gọi đi qua Backend (lọc dữ liệu, kiểm quyền, che API key).
- Admin cấu hình provider/model/API key/prompt trong `AIConfig` (API `/api/admin/config/ai`).

## 2. Prompt template gốc (bắt buộc giữ 2 câu ràng buộc)

System:
> Bạn là trợ lý tra cứu thư viện. Chỉ gợi ý sách có trong dữ liệu được cung cấp. Không bịa mã sách hoặc tình trạng sách.

User (AI-1):
> Tôi muốn tìm sách dễ đọc về {{chủ đề}} cho người mới bắt đầu. Dữ liệu sách: {{book_list}}. Hãy gợi ý tối đa 5 cuốn, kèm lý do.

## 3. Từng chức năng

### AI-1 — Chatbot tra cứu sách
- Đầu vào: câu hỏi tự nhiên của reader.
- Dữ liệu: danh sách sách đã lọc từ `GET /api/books` (không kèm thông tin độc giả).
- Đầu ra: tối đa 5 sách + lý do; cảnh báo "kết quả do AI tạo".
- API dự kiến: `POST /api/ai/search` {question} → {answer, books[]}.

### AI-2 — Tóm tắt sách
- Đầu vào: mô tả/mục lục/đoạn giới thiệu sách (Backend cung cấp theo mã sách).
- Prompt riêng: yêu cầu tóm tắt ngắn, trung thực theo nội dung được cung cấp.
- API dự kiến: `POST /api/ai/summarize` {ma_sach}.

### AI-3 — Gợi ý sách liên quan
- Đầu vào: thể loại, tác giả, lịch sử mượn **đã ẩn thông tin nhạy cảm** (Backend chỉ gửi mã sách/thể loại, không gửi tên/email/CCCD độc giả).
- Prompt riêng; thử nghiệm ≥ 3 phiên bản prompt, ghi bản chốt + lý do.
- API dự kiến: `POST /api/ai/recommend` {ma_sach}.

## 4. Ràng buộc & xử lý lỗi

- Không bịa mã sách/trạng thái; không gửi dữ liệu cá nhân nếu không cần.
- Xử lý timeout, rate limit, response rỗng/sai định dạng → trả lỗi thân thiện cho UI.
- Log mỗi lần gọi AI (giám sát, cảnh báo — UC26).
