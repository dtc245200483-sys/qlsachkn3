# BÁO CÁO MINH CHỨNG: TÍCH HỢP CHATBOT AI V3 CHÍNH THỨC VÀO WEB APP THƯ VIỆN

## Prompt đã dùng

### Câu lệnh yêu cầu của đồ án / bài toán:
```text
Dọn dẹp môi trường thử nghiệm độc lập v1/v2/v3, tích hợp phiên bản System Prompt V3 
(JSON Schema chuẩn + Chặn câu hỏi lạc đề 2 tầng) trực tiếp vào hệ thống Web App 
quản lý thư viện chính thức của đề tài (Backend FastAPI + Frontend giao diện ICTU).
```

---

## Phản hồi kết quả AI

### 1. Kiến trúc hệ thống Chatbot AI V3 trên Web App chính

Sau khi thử nghiệm và đánh giá chất lượng qua 3 phiên bản, hệ thống đã chính thức tích hợp **Phiên bản V3** vào Web App duy nhất tại cổng **`http://localhost:8000`**:

```
                       ┌────────────────────────────────────────────────────────┐
                       │          TRÌNH DUYỆT NGƯỜI DÙNG (PORT 8000)            │
                       │   - Trang chuyên biệt: chatbot.html                    │
                       │   - Thanh điều hướng: Menu "🤖 Trợ lý AI"              │
                       │   - Bong bóng nổi: Floating Chatbot Widget (mọi trang) │
                       │   - Trang tra cứu: Nút "🤖 Hỏi Trợ lý AI"              │
                       └───────────────────────────┬────────────────────────────┘
                                                   │ Gọi qua API.call("chatbot")
                                                   ▼
                       ┌────────────────────────────────────────────────────────┐
                       │             BACKEND FASTAPI (PORT 8000)                │
                       │      Router: Backend/app/routers/chatbot.py            │
                       │   - POST /api/chatbot/hoi                              │
                       │   - GET  /api/chatbot/health                           │
                       └───────────────────────────┬────────────────────────────┘
                                                   │
                         ┌─────────────────────────┴─────────────────────────┐
                         ▼                                                   ▼
         ┌───────────────────────────────┐                   ┌───────────────────────────────┐
         │     TẦNG RETRIEVAL 2 LỚP      │                   │     SYSTEM PROMPT V3 (JSON)   │
         │  1. Embedding (ChromaDB)      │                   │  1. 8 Quy tắc ràng buộc       │
         │  2. Fuzzy match tên riêng     │                   │  2. JSON Schema bắt buộc      │
         │  3. Lọc ngưỡng score (0.35)   │                   │  3. Chặn câu hỏi lạc đề       │
         │  4. Ngưỡng lạc đề (< 0.15)    │                   │     (Chính trị, thời sự)      │
         └───────────────────────────────┘                   └───────────────────────────────┘
```

---

### 2. Chi tiết các thành phần đã triển khai

#### A. Tầng Backend API:
- **Router [Backend/app/routers/chatbot.py](file:///D:/ung%20dung%20tri%20tue%20nhan%20ao/app/Backend/app/routers/chatbot.py)**:
  - `POST /api/chatbot/hoi`: Nhận `{ "cau_hoi": str }`, gọi hàm `tra_cuu_sach(cau_hoi, prompt_version="v3")`, trả về đối tượng JSON chuẩn hóa với danh sách sách, tình trạng còn hàng và lý do gợi ý.
  - `GET /api/chatbot/health`: Trả về trạng thái sẵn sàng của dịch vụ AI và số lượng sách trong Vector Store.
- **Đăng ký vào ứng dụng**: Đã include router vào [Backend/app/main.py](file:///D:/ung%20dung%20tri%20tue%20nhan%20ao/app/Backend/app/main.py).
- **Kết nối API Frontend**: Đã bổ sung endpoint `chatbot: "/api/chatbot/hoi"` vào [frontend/js/api.js](file:///D:/ung%20dung%20tri%20tue%20nhan%20ao/app/frontend/js/api.js).

#### B. Tầng Giao diện Frontend:
1. **Trang Chatbot chuyên biệt ([frontend/chatbot.html](file:///D:/ung%20dung%20tri%20tue%20nhan%20ao/app/frontend/chatbot.html))**:
   - Tuân thủ bộ nhận diện thương hiệu ICTU: Phông chữ Be Vietnam Pro, màu chủ đạo Navy `#0a2e5c`.
   - Có sẵn các nút chủ đề chọn nhanh: Tư duy làm giàu, Lập trình Python, Nghệ thuật giao tiếp, Kiểm tra hết hàng...
   - Render sách dạng **Book Card** trực quan: Tên sách, tác giả, lý do AI đề xuất, huy hiệu tình trạng (Còn sách / Hết sách), nút bấm *"Xem trong kho"* chuyển hướng sang trang tìm kiếm.
   - Xử lý thông báo từ chối lịch sự khi gặp câu hỏi ngoài phạm vi thư viện theo đúng Quy tắc 8.
2. **Bộ điều khiển & Giao diện ([frontend/js/chatbot.js](file:///D:/ung%20dung%20tri%20tue%20nhan%20ao/app/frontend/js/chatbot.js), [frontend/css/chatbot.css](file:///D:/ung%20dung%20tri%20tue%20nhan%20ao/app/frontend/css/chatbot.css))**:
   - Tương tác mượt mà, hiệu ứng đang gõ (typing animation), tự động cuộn xuống tin nhắn mới nhất, đo thời gian xử lý (ms).
3. **Menu thanh điều hướng ([frontend/js/layout.js](file:///D:/ung%20dung%20tri%20tue%20nhan%20ao/app/frontend/js/layout.js))**:
   - Thêm mục **`🤖 Trợ lý AI`** vào navbar cho tất cả vai trò: Độc giả (`reader`), Thủ thư (`librarian`), Quản trị viên (`admin`).
4. **Bong bóng chat nổi ([frontend/js/chatbot-widget.js](file:///D:/ung%20dung%20tri%20tue%20nhan%20ao/app/frontend/js/chatbot-widget.js))**:
   - Xuất hiện nút tròn 🤖 ở góc dưới bên phải trên tất cả các trang (`search.html`, `books.html`, `profile.html`...). Bấm vào là mở ngay khung chat mini để hỏi AI mà không cần rời trang hiện tại.
5. **Trang tra cứu ([frontend/search.html](file:///D:/ung%20dung%20tri%20tue%20nhan%20ao/app/frontend/search.html))**:
   - Bổ sung nút bấm nổi bật *"🤖 Hỏi Trợ lý AI"* đặt cạnh nút Tìm kiếm.

---

### 3. Kết quả kiểm thử thực tế trên Web App chính (Port 8000)

#### Test Case 1: Kiểm tra trạng thái Health Check
- **Endpoint**: `GET http://localhost:8000/api/chatbot/health`
- **Kết quả trả về**:
```json
{
  "trang_thai": "san_sang",
  "phien_ban_prompt": "v3",
  "do_dai_prompt": 1812,
  "so_sach_vector_store": 10
}
```

#### Test Case 2: Tra cứu sách tài chính hợp lệ
- **Câu hỏi**: `"sách về tư duy làm giàu"`
- **Kết quả trả về**: Status `200 OK`, tìm thấy 2 cuốn sách:
  1. *Nghĩ giàu làm giàu* — Napoleon Hill (`con_hang: True`)
  2. *Cha giàu cha nghèo* — Robert T. Kiyosaki (`con_hang: True`)

#### Test Case 3: Chặn đứng câu hỏi ngoài phạm vi thư viện (Lạc đề)
- **Câu hỏi**: `"Ai là chủ tịch nước hiện tại?"`
- **Kết quả xử lý**: Hệ thống kích hoạt phòng vệ 2 tầng, phát hiện điểm tương đồng tối đa `0.0541 < 0.15` nên **chặn ngay tại tầng retrieval**, không tiêu tốn API token của LLM:
```json
{
  "ket_qua": [],
  "tong_so_ket_qua": 0,
  "thong_bao": "Tôi chỉ hỗ trợ tra cứu sách trong thư viện. Bạn vui lòng đặt câu hỏi liên quan đến sách nhé!",
  "prompt_version": "v3",
  "context_so_bo": 0,
  "canh_bao_bia": false
}
```

---

## Phần sinh viên đã kiểm tra chỉnh sửa
*(sinh viên tự điền sau khi review code)*

---

## Ngày thực hiện
- **Ngày thực hiện**: 15/09/2026
- **Người thực hiện**: Kỹ sư Full-stack AI / Thành viên nhóm đề tài Web App Thư viện
