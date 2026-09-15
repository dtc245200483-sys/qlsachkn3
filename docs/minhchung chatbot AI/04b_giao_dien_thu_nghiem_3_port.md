# BÁO CÁO MINH CHỨNG: HỆ THỐNG GIAO DIỆN THỬ NGHIỆM ĐỘC LẬP 3 PORT CHO 3 PHIÊN BẢN SYSTEM PROMPT

## 1. Mô tả kiến trúc 3 trang web thử nghiệm độc lập

Để phục vụ quá trình nghiên cứu, đánh giá khách quan và kiểm thử A/B testing mà không bị xung đột cấu hình hay phụ thuộc vào dropdown trên giao diện, hệ thống đã được thiết kế thành **3 ứng dụng web độc lập hoàn toàn**, phục vụ trên **3 Port mạng riêng biệt**:

```
                              ┌──────────────────────────────────────────────┐
                              │                 NGƯỜI DÙNG                   │
                              └───────┬──────────────┬──────────────┬────────┘
                                      │              │              │
                   Tab 1: Port 8001   │              │              │ Tab 3: Port 8003
                 ┌────────────────────┘              │              └────────────────────┐
                 │                                   │ Tab 2: Port 8002                  │
                 ▼                                   ▼                                   ▼
   ┌───────────────────────────┐       ┌───────────────────────────┐       ┌───────────────────────────┐
   │    TEST UI V1 (Cơ bản)    │       │  TEST UI V2 (Ràng buộc)   │       │  TEST UI V3 (Chính thức)  │
   │    http://localhost:8001  │       │    http://localhost:8002  │       │    http://localhost:8003  │
   │    Tone màu: Xám đen      │       │    Tone màu: Vàng hổ phách│       │    Tone màu: Xanh lá cây  │
   ├───────────────────────────┤       ├───────────────────────────┤       ├───────────────────────────┤
   │ Backend: api_v1.py        │       │ Backend: api_v2.py        │       │ Backend: api_v3.py        │
   │ Endpoint: POST /hoi       │       │ Endpoint: POST /hoi       │       │ Endpoint: POST /hoi       │
   │ Cố định: v1_co_ban.txt    │       │ Cố định: v2_co_rang_buoc  │       │ Cố định: v3_json_hoan_chin│
   └─────────────┬─────────────┘       └─────────────┬─────────────┘       └─────────────┬─────────────┘
                 │                                   │                                   │
                 └───────────────────────────────────┼───────────────────────────────────┘
                                                     ▼
                                       ┌───────────────────────────┐
                                       │    TẦNG DỊCH VỤ CHUNG     │
                                       │    (chatbot_service.py)   │
                                       │    ChromaDB Vector Store  │
                                       │    OpenRouter Gemini Flash│
                                       └───────────────────────────┘
```

### Đặc điểm từng ứng dụng:

1. **Bộ 1: Phiên bản V1 — Cơ bản (`http://localhost:8001`)**
   - **Mục đích**: Vòng thử nghiệm 1. Đóng vai trò baseline (đối chứng). Prompt tối giản, chưa có ràng buộc chống bịa, chưa có cấu trúc JSON, chưa có bộ lọc lạc đề.
   - **Giao diện**: Màu chủ đạo xám trung tính (`#374151`, `#4B5563`). Hiển thị câu trả lời tự nhiên của AI dạng đoạn văn.
   - **Tập tin**:
     - Backend: `D:\ung dung tri tue nhan ao\app\chatbotAI\test_ui\v1\api_v1.py`
     - Frontend: `D:\ung dung tri tue nhan ao\app\chatbotAI\test_ui\v1\index.html`

2. **Bộ 2: Phiên bản V2 — Có ràng buộc (`http://localhost:8002`)**
   - **Mục đích**: Vòng thử nghiệm 2. Đã bổ sung 6 quy tắc bắt buộc: chỉ dùng sách trong context, trung thực khi không có sách, cảnh báo hết hàng/đặt trước, giới hạn 5 cuốn. Chưa có bộ chặn lạc đề Rule 8 và chưa ép JSON.
   - **Giao diện**: Màu chủ đạo vàng cam hổ phách (`#D97706`, `#B45309`) mang tính cảnh báo và kiểm soát.
   - **Tập tin**:
     - Backend: `D:\ung dung tri tue nhan ao\app\chatbotAI\test_ui\v2\api_v2.py`
     - Frontend: `D:\ung dung tri tue nhan ao\app\chatbotAI\test_ui\v2\index.html`

3. **Bộ 3: Phiên bản V3 — JSON Hoàn chỉnh & Chặn lạc đề (`http://localhost:8003`)**
   - **Mục đích**: Phiên bản chính thức hoàn thiện nhất. Bổ sung đầy đủ: Output JSON nghiêm ngặt theo schema, Quy tắc 8 chặn đứng câu hỏi ngoài phạm vi thư viện (chính trị, đời tư, thời sự), kết hợp bộ lọc 2 tầng (Retrieval score + System Prompt).
   - **Giao diện**: Màu chủ đạo xanh lá cây hiện đại (`#059669`, `#10B981`) thể hiện sự an toàn, chuẩn hóa, dữ liệu được render dạng Book Card chuyên nghiệp.
   - **Tập tin**:
     - Backend: `D:\ung dung tri tue nhan ao\app\chatbotAI\test_ui\v3\api_v3.py`
     - Frontend: `D:\ung dung tri tue nhan ao\app\chatbotAI\test_ui\v3\index.html`

---

## 2. Các lệnh khởi chạy 3 máy chủ thử nghiệm

Mỗi ứng dụng có thể chạy đồng thời trên 3 cửa sổ terminal riêng biệt mà không gây tranh chấp cổng:

### Cửa sổ Terminal 1 (Chạy Test UI V1 - Port 8001):
```powershell
cd "D:\ung dung tri tue nhan ao\app"
uvicorn chatbotAI.test_ui.v1.api_v1:app --reload --port 8001
```

### Cửa sổ Terminal 2 (Chạy Test UI V2 - Port 8002):
```powershell
cd "D:\ung dung tri tue nhan ao\app"
uvicorn chatbotAI.test_ui.v2.api_v2:app --reload --port 8002
```

### Cửa sổ Terminal 3 (Chạy Test UI V3 - Port 8003):
```powershell
cd "D:\ung dung tri tue nhan ao\app"
uvicorn chatbotAI.test_ui.v3.api_v3:app --reload --port 8003
```

---

## 3. Hướng dẫn mở và kiểm thử song song trên trình duyệt

### Cách truy cập giao diện:
Do mỗi backend FastAPI đều đã tích hợp sẵn route `GET /` phục vụ trực tiếp file `index.html` tương ứng, người kiểm thử có thể:
1. Mở trình duyệt Web (Chrome, Edge, Firefox,...).
2. Mở 3 tab cạnh nhau (hoặc chia 3 cửa sổ màn hình):
   - Tab 1: `http://localhost:8001`
   - Tab 2: `http://localhost:8002`
   - Tab 3: `http://localhost:8003`
3. *(Tùy chọn)* Có thể mở trực tiếp file `index.html` bằng cách nhấp đúp file trong Windows Explorer hoặc kéo thả vào trình duyệt, do frontend đã được cấu hình CORS `*` và gọi thẳng URL tuyệt đối của từng port.

### Tính năng hỗ trợ kiểm thử nhanh trên giao diện:
Cả 3 trang web đều tích hợp sẵn 6 nút bấm mẫu:
- `1. Ngữ nghĩa: Làm giàu & tài chính`
- `2. Mơ hồ: "sách gì hay hay"`
- `3. Ngoài thư viện: Lái xe ô tô`
- `4. Hết hàng: Kiến trúc hệ thống phân tán`
- `5. Tên tác giả: "Carnegie"`
- `6. Lạc đề: Chủ tịch nước`

Khi nhấp vào nút bất kỳ, câu hỏi được tự động điền vào ô nhập. Người kiểm thử chỉ cần bấm **"Gửi Hỏi"** trên từng tab để quan sát sự khác biệt rõ rệt về:
- **Tốc độ phản hồi (ms)**
- **Số lượng và chi tiết context thu được từ ChromaDB (có thể bấm mở rộng để soi)**
- **Hình thức kết quả: Văn bản tự do (V1/V2) vs Thẻ sách JSON chuẩn (V3)**
- **Khả năng nhận biết sách hết hàng và cảnh báo chống bịa đặt ⚠️**
- **Phản ứng khi gặp câu hỏi lạc đề (Câu 6)**: V1/V2 bị cuốn theo câu hỏi chính trị/thời sự; V3 kiên quyết từ chối đúng phạm vi thư viện.

---

## 4. Ảnh chụp và kết quả kiểm thử đối sánh thực tế trên 3 Port

*(Sinh viên tự chụp màn hình trình duyệt hiển thị 3 tab cạnh nhau khi test cùng 1 câu hỏi và chèn vào mục này)*

### Minh chứng 1: Thử nghiệm câu hỏi lạc đề ("Ai là chủ tịch nước hiện tại?")
- **Kết quả Port 8001 (V1)**: 
  *(sinh viên tự điền sau khi review code)*
- **Kết quả Port 8002 (V2)**: 
  *(sinh viên tự điền sau khi review code)*
- **Kết quả Port 8003 (V3)**: 
  *(sinh viên tự điền sau khi review code)*

### Minh chứng 2: Thử nghiệm câu hỏi sách đã hết hàng ("Kiến trúc hệ thống phân tán")
- **Kết quả Port 8001 (V1)**: 
  *(sinh viên tự điền sau khi review code)*
- **Kết quả Port 8002 (V2)**: 
  *(sinh viên tự điền sau khi review code)*
- **Kết quả Port 8003 (V3)**: 
  *(sinh viên tự điền sau khi review code)*

---

## 5. Ngày thực hiện
- **Ngày thực hiện**: 15/09/2026
- **Người thực hiện**: Kỹ sư Full-stack AI / Sinh viên thực tập dự án thư viện
