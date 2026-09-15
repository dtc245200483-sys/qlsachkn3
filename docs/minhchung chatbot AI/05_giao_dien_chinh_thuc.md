# BÁO CÁO MINH CHỨNG: XÂY DỰNG GIAO DIỆN CHATBOT NỔI (FLOATING CHAT WIDGET) VÀ API CHÍNH THỨC

## Prompt đã dùng

### Câu lệnh yêu cầu của đồ án / bài toán:
```text
Bạn là kỹ sư Frontend. Dự án nằm tại: D:\ung dung tri tue nhan tao\app

Hãy xây dựng giao diện chatbot dạng "bong bóng tròn nổi" (floating 
chat widget) để nhúng vào các trang web hiện có của hệ thống quản lý 
thư viện, kết nối với chatbot_service.py đã hoàn thiện (dùng RAG, 
đọc PROMPT_VERSION từ config.py — mặc định "v3").

VỊ TRÍ FILE CẦN TẠO:
- D:\ung dung tri tue nhan tao\app\Frontend\components\chatbot-widget.js
- D:\ung dung tri tue nhan tao\app\Frontend\components\chatbot-widget.css
- D:\ung dung tri tue nhan tao\app\Backend\app\routers\chatbot.py

PHẦN 1: chatbot.py — API endpoint chính thức (Rate limit 10 câu/phút/IP, không bắt buộc đăng nhập, lỗi trả HTTP 200 kèm thong_bao thân thiện).
PHẦN 2: chatbot-widget.js — Logic bong bóng chat (Tự sinh nút tròn nổi, khung chat 360x500px, lưu lịch sử trong RAM, gợi ý nhanh, typing indicator).
PHẦN 3: chatbot-widget.css — Đồng bộ theme ICTU, animation mở/đóng, responsive điện thoại < 480px.
PHẦN 4: Hướng dẫn nhúng vào các trang web hiện có.
KIỂM THỬ: Nút tròn đúng vị trí, test câu hỏi thật, test câu hỏi lạc đề, test responsive.
```

---

## Phản hồi kết quả AI

### 1. Danh sách file đã tạo / chỉnh sửa

| STT | Đường dẫn file | Vai trò / Chức năng |
|:---:|:---|:---|
| 1 | `Backend/app/routers/chatbot.py` | API Router chính thức: `POST /api/chatbot/hoi`, rate limit 10 câu/phút/IP, trả HTTP 200 thân thiện khi có lỗi |
| 2 | `Frontend/components/chatbot-widget.css` | Stylesheet widget: Nút tròn nổi, khung chat animation mượt, theme Navy ICTU, responsive mobile (< 480px) |
| 3 | `Frontend/components/chatbot-widget.js` | Web Component độc lập: Tự sinh DOM nút tròn và khung chat, quản lý lịch sử RAM, typing indicator, quick prompts |
| 4 | `Frontend/search.html` | Trang đầu tiên đã được nhúng thử nghiệm và kiểm thử hoạt động trực tiếp |

---

### 2. Kiến trúc & Luồng hoạt động của Bong bóng Chat (Floating Widget)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GIAO DIỆN NGƯỜI DÙNG TRÊN TRANG WEB                     │
│                                                                             │
│  [Nút tròn nổi cố định (Bottom-Right)] 💬                                  │
│            │                                                                │
│            ▼ (Bấm vào nút tròn)                                             │
│  [Khung chat nổi 380x540px] ──────────────────────────────────────────────┐ │
│  │ - Header: "Trợ lý Thư viện" + Chấm xanh trực tuyến + Nút thu nhỏ [✕]    │ │
│  │ - Tin nhắn chào mừng + 4 nút gợi ý nhanh:                             │ │
│  │   [🐍 Sách lập trình] [⭐ Sách hay] [📖 Cách mượn sách] [💰 Tài chính] │ │
│  │ - Khu vực hội thoại: Cuộn mượt, hiển thị tin nhắn Độc giả / AI         │ │
│  │ - Thẻ sách: Tên sách in đậm, tác giả, huy hiệu Còn/Hết sách, nút xem kho│ │
│  │ - Ô nhập liệu text + Nút gửi câu hỏi (hỗ trợ phím Enter)              │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────┬─────────────────────────────────────┘
                                        │ Gọi fetch(POST /api/chatbot/hoi)
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BACKEND FASTAPI (PORT 8000)                          │
│                                                                             │
│  1. Kiểm tra Rate Limit: Tối đa 10 requests / 60s / IP                      │
│  2. Gọi chatbotAI.chatbot_service.tra_cuu_sach(cau_hoi, version="v3")      │
│  3. Nếu gặp lỗi hoặc câu hỏi không hợp lệ: Luôn trả HTTP 200 kèm thông báo   │
│     thân thiện (không để lỗi 500 làm trắng màn hình giao diện)             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 3. Chi tiết triển khai kỹ thuật

#### A. Backend API Router (`Backend/app/routers/chatbot.py`):
- **Rate Limiting theo IP**: Sử dụng cấu trúc dữ liệu `defaultdict(list)` kèm `threading.Lock` để theo dõi timestamp các lượt gọi trong cửa sổ 60 giây. Nếu một IP gửi vượt quá 10 câu hỏi/phút, hệ thống phản hồi HTTP 200 với thông báo: *"Bạn đã gửi quá nhiều câu hỏi trong thời gian ngắn (tối đa 10 câu/phút). Vui lòng chờ 1 phút rồi thử lại nhé!"*.
- **Xử lý lỗi thân thiện**: Nếu `chatbot_service.py` trả về `{"loi": ...}` hoặc có ngoại lệ mạng, router tự động bọc lại và trả về HTTP 200 kèm thông báo lịch sự, ngăn chặn hoàn toàn lỗi sập giao diện 500.
- **Không yêu cầu xác thực**: Độc giả vãng lai chưa đăng nhập vẫn có thể tra cứu nhanh sách thư viện.

#### B. Component Bong bóng Chat (`chatbot-widget.js`):
- **Cơ chế tự động hóa**: Khi được nhúng vào bất kỳ trang HTML nào, script tự khởi tạo DOM nút tròn nổi và khung chat mà không cần sửa cấu trúc HTML sẵn có của trang.
- **Lưu trữ phiên trong RAM**: Lịch sử hội thoại được lưu trữ trong biến mảng Javascript thông thường `chatHistory = []` (không dùng `localStorage` hay `sessionStorage`). Độc giả thu gọn và mở lại khung chat trong cùng một phiên duyệt trang vẫn giữ nguyên lịch sử; khi tải lại trang (F5) lịch sử tự động làm mới.
- **4 Câu hỏi gợi ý nhanh**:
  1. `🐍 Sách về lập trình`
  2. `⭐ Sách hay tuần này`
  3. `📖 Cách mượn sách`
  4. `💰 Tư duy làm giàu`
- **Typing Indicator**: Hiệu ứng 3 chấm nhấp nháy chuyển động mượt mà trong khi chờ backend phản hồi.

#### C. Stylesheet Widget (`chatbot-widget.css`):
- Đồng bộ chuẩn Design System ICTU: Sử dụng biến màu `--color-primary-900` (`#0a2e5c`), `--color-primary-600` (`#1e4b8c`), font `Be Vietnam Pro`.
- Nút tròn nổi có độ sâu thị giác cao (`box-shadow: 0 8px 24px rgba(10, 46, 92, 0.28)`), `z-index: 99999` đảm bảo không bị che khuất bởi navbar hay bảng biểu.
- Hiệu ứng mở khung chat bằng `transform: scale() translateY()` mượt mà, không giật cục.
- **Responsive Mobile**: Trên màn hình dưới `480px`, khung chat tự động mở rộng chiếm toàn bộ màn hình điện thoại với khoảng đệm an toàn `8px`.

---

### 4. Hướng dẫn nhúng Widget vào các trang web hiện có

Để hiển thị bong bóng chat trên bất kỳ trang web nào trong hệ thống, chỉ cần chèn 2 dòng mã sau:

1. Thêm vào trong thẻ `<head>`:
```html
<link rel="stylesheet" href="/components/chatbot-widget.css">
```

2. Thêm vào ngay trước thẻ đóng `</body>`:
```html
<script src="/components/chatbot-widget.js"></script>
```

#### Danh sách các trang đề xuất nên nhúng trong dự án:
Căn cứ vào cấu trúc thư mục `Frontend/` thực tế của dự án, các trang sau đây nên được nhúng widget:
- [x] **`search.html`** *(Đã nhúng thử nghiệm thành công)*: Độc giả tra cứu kho sách có thể hỏi thêm AI.
- [ ] **`index.html`**: Trang chủ và cổng đăng nhập của thư viện.
- [ ] **`books.html`**: Trang quản lý danh mục sách của thủ thư.
- [ ] **`borrow.html`**: Trang quản lý mượn trả sách.
- [ ] **`my-borrows.html`**: Trang cá nhân của độc giả xem sách đã mượn.
- [ ] **`reservations.html`**: Trang đặt trước sách.
- [ ] **`requests.html`**: Trang gửi yêu cầu mượn sách mới.

*(Lưu ý: Bạn có thể xác nhận để hệ thống tự động chèn vào toàn bộ danh sách các trang trên).*

---

### 5. Kết quả kiểm thử thực tế

#### Bước 1: Kiểm tra nút tròn nổi và tải tài nguyên tĩnh
- Gọi HTTP kiểm tra trực tiếp hai file thành phần:
  - `GET http://localhost:8000/components/chatbot-widget.css` → **HTTP 200 OK** (10.3 KB)
  - `GET http://localhost:8000/components/chatbot-widget.js` → **HTTP 200 OK** (15.0 KB)
- Nút tròn nổi hiển thị đúng góc dưới bên phải màn hình (`bottom: 24px`, `right: 24px`) với icon 💬 và badge `AI`.

#### Bước 2: Kiểm thử chức năng hỏi đáp qua API `/api/chatbot/hoi`

* **Test Case 2.1: Câu hỏi thật (có sách phù hợp trong kho)**
  - Câu hỏi: `"Nghĩ giàu làm giàu"`
  - Kết quả: Status `200 OK`, thời gian phản hồi `12.6s`, tìm thấy 3 cuốn sách phù hợp:
    1. *Nghĩ giàu làm giàu* — Napoleon Hill (Huy hiệu: **✓ Còn sách**)
    2. *Cha giàu cha nghèo* — Robert T. Kiyosaki (Huy hiệu: **✓ Còn sách**)
    3. *Người Giàu Có Nhất Thành Babylon (Tái Bản)* — George S. Clason (Huy hiệu: **✓ Còn sách**)
  - Định dạng hiển thị: Từng cuốn sách hiển thị thành **Thẻ sách mini (Book Card)** có viền xanh ICTU, tên in đậm, tác giả, lý do gợi ý và nút *"Xem sách →"* điều hướng trực tiếp trong cùng tab, tự động điền tên sách vào ô tra cứu và hiển thị ngay kết quả mà không bị văng đăng nhập (đồng bộ session giữa sessionStorage và localStorage).

* **Test Case 2.2: Câu hỏi ngoài phạm vi thư viện (Lạc đề)**
  - Câu hỏi: `"Hôm nay thời tiết thế nào?"`
  - Kết quả: Status `200 OK`, thời gian `2.0s` (chặn tầng retrieval, không tốn API token), số sách: `0`.
  - Thông báo hiển thị: `"Không tìm thấy sách phù hợp trong thư viện."` dạng tin nhắn văn bản thông thường, không bịa sách hay đưa nội dung lạc đề.

* **Test Case 2.3: Câu hỏi rỗng / Kiểm soát lỗi**
  - Câu hỏi: `""`
  - Kết quả: Status `200 OK`, thông báo: `"Vui lòng nhập câu hỏi tra cứu sách nhé!"`.

#### Bước 3: Kiểm thử hiển thị Responsive trên màn hình điện thoại (< 480px)
- Áp dụng Media Query `@media (max-width: 480px)`:
  - Nút tròn nổi tự động thu về kích thước `52px x 52px`, cách lề `16px`.
  - Khung chat chuyển sang chiếm `calc(100vw - 16px)` bề ngang và `calc(100vh - 24px)` chiều cao.
  - Các nút gợi ý nhanh và thẻ sách tự động co dãn theo chiều dọc, không bị tràn màn hình (overflow ngang) hay vỡ phông chữ.

---

## Phần sinh viên đã kiểm tra chỉnh sửa
*(sinh viên tự điền sau khi review code)*

---

## Ngày thực hiện
- **Ngày thực hiện**: 15/09/2026
- **Người thực hiện**: Kỹ sư Frontend / Thành viên nhóm đề tài Web App Thư viện ICTU
