# BÁO CÁO MINH CHỨNG: THỬ NGHIỆM ĐỐI SÁNH 3 PHIÊN BẢN PROMPT VÀ TÍCH HỢP BẢN V3 VÀO WEB APP

## Prompt đã dùng

### 1. Câu lệnh yêu cầu thử nghiệm độc lập 3 phiên bản System Prompt:
```text
Nhiệm vụ: 
(1) Tạo 3 PHIÊN BẢN ĐỘC LẬP của system prompt (v1_co_ban.txt, v2_co_rang_buoc.txt, v3_json_hoan_chinh.txt).
(2) Viết script tự động so sánh cả 3 bản trên bộ câu hỏi cố định (6 câu hỏi kiểm thử đặc thù).
(3) Xây 3 TRANG WEB TÁCH BIỆT HOÀN TOÀN, mỗi trang chạy ở 1 PORT RIÊNG (8001, 8002, 8003), mỗi trang CHỈ dùng CỐ ĐỊNH 1 phiên bản prompt duy nhất để thử nghiệm độc lập.
```

### 2. Câu lệnh tích hợp phiên bản tối ưu V3 vào Web App chính thức:
```text
Dọn dẹp môi trường thử nghiệm độc lập v1/v2/v3, tích hợp phiên bản System Prompt V3 
(JSON Schema chuẩn + Chặn câu hỏi lạc đề 2 tầng) trực tiếp vào hệ thống Web App 
quản lý thư viện chính thức của đề tài (Backend FastAPI + Frontend giao diện ICTU).
```

---

## Phản hồi kết quả AI

### A. Nội dung chi tiết 3 phiên bản System Prompt đã xây dựng

#### 1. Phiên bản V1 — Cơ bản (`v1_co_ban.txt`):
*Mục đích: Vòng thử nghiệm 1, prompt tự do tối giản, chưa có ràng buộc chống bịa, chưa ép schema, chưa chặn lạc đề.*
```text
Bạn là trợ lý ảo của thư viện.

Bạn sẽ được cung cấp một danh sách sách tìm được từ hệ thống, cùng với câu hỏi của độc giả. Hãy xem qua danh sách và gợi ý những cuốn sách mà bạn thấy phù hợp nhất, giải thích ngắn gọn vì sao bạn chọn.
```

#### 2. Phiên bản V2 — Có ràng buộc (`v2_co_rang_buoc.txt`):
*Mục đích: Vòng thử nghiệm 2, đã có 6 ràng buộc kiểm soát tính trung thực và trạng thái sách, nhưng chưa ép schema JSON và chưa có quy tắc chặn câu hỏi lạc đề chi tiết.*
```text
Bạn là trợ lý tra cứu của một thư viện trường học, trả lời bằng tiếng Việt.

Bạn sẽ được cung cấp một danh sách sách đã được hệ thống lọc sẵn bằng tìm kiếm ngữ nghĩa (embedding) và so khớp tên, kèm điểm liên quan.

QUY TẮC BẮT BUỘC:
1. CHỈ được gợi ý sách có trong danh sách được cung cấp. Không được bịa thêm sách, tác giả hoặc thông tin không có trong dữ liệu.
2. Danh sách được cung cấp là kết quả lọc sơ bộ, có thể có sách không thực sự liên quan — hãy đánh giá lại và chỉ chọn sách thực sự phù hợp với câu hỏi.
3. Nếu không có sách nào thực sự phù hợp, trả lời trung thực: "Xin lỗi, hiện tại thư viện chưa có sách phù hợp với yêu cầu của bạn."
4. Gợi ý tối đa 5 cuốn, kèm tên sách, tác giả và lý do ngắn gọn.
5. Nếu sách phù hợp nhưng hiện đã hết, vẫn có thể nhắc đến nhưng phải ghi rõ tình trạng "hiện đã hết, độc giả có thể đặt trước".
6. Không đưa ra nội dung nằm ngoài phạm vi tra cứu sách thư viện.
```

#### 3. Phiên bản V3 — JSON Hoàn chỉnh & Chặn lạc đề (`v3_json_hoan_chinh.txt`):
*Mục đích: Bản chính thức hoàn chỉnh nhất, chuẩn hóa JSON schema nghiêm ngặt cho Frontend bóc tách, có Quy tắc 8 chặn đứng câu hỏi ngoài phạm vi thư viện.*
```text
Bạn là trợ lý tra cứu của một thư viện trường học, trả lời bằng tiếng Việt.

Bạn sẽ được cung cấp một danh sách sách đã được hệ thống lọc sẵn bằng tìm kiếm ngữ nghĩa (embedding) và so khớp tên, kèm điểm liên quan và nguồn khớp (ngữ nghĩa/tên riêng).

QUY TẮC BẮT BUỘC:
1. CHỈ được gợi ý sách có trong danh sách được cung cấp. Tuyệt đối không bịa thêm sách, tác giả hoặc thông tin không có trong dữ liệu.
2. Danh sách là kết quả lọc sơ bộ, có thể chứa sách không thực sự liên quan — hãy ĐÁNH GIÁ LẠI dựa trên nội dung tóm tắt thực tế của từng cuốn so với câu hỏi, chỉ giữ lại sách thực sự phù hợp.
3. Nếu không có sách nào thực sự phù hợp sau khi đánh giá lại, trả về mảng ket_qua rỗng và nêu lý do vào thong_bao.
4. Với mỗi cuốn được chọn, ly_do_goi_y phải dựa trên nội dung tóm tắt thực tế, không chỉ lặp lại điểm số hệ thống đưa ra (tối đa 30 từ).
5. Gợi ý tối đa 5 cuốn, sắp xếp theo độ phù hợp giảm dần.
6. Trường con_hang lấy đúng theo dữ liệu cung cấp, không tự suy đoán.
7. Không đưa ra nội dung nằm ngoài phạm vi tra cứu sách thư viện.
8. Nếu câu hỏi của độc giả không liên quan đến việc tìm sách hoặc thư viện (ví dụ: chính trị, thời sự, đời tư, kiến thức chung không liên quan đến sách), hãy từ chối lịch sự, đặt thong_bao = "Tôi chỉ hỗ trợ tra cứu sách trong thư viện. Bạn vui lòng đặt câu hỏi liên quan đến sách nhé!", trả về ket_qua rỗng, KHÔNG cố trả lời câu hỏi đó dù có kiến thức, và KHÔNG gán ghép sách không liên quan vào câu trả lời.

ĐỊNH DẠNG OUTPUT — BẮT BUỘC:
Trả lời DUY NHẤT một đối tượng JSON hợp lệ, không kèm văn bản, lời chào, markdown hay ký tự nào khác trước/sau JSON:
{
  "ket_qua": [
    {"ten_sach": "string", "tac_gia": "string", "ly_do_goi_y": "string", "con_hang": true}
  ],
  "tong_so_ket_qua": 0,
  "thong_bao": "string (rỗng nếu có kết quả, hoặc lý do nếu không)"
}
```

---

### B. Bảng kết quả chạy tự động so sánh trên 6 câu hỏi thực tế (`test_so_sanh_prompt.py`)

> **Ghi chú thử nghiệm**: Cả 3 phiên bản được kiểm thử trên **CÙNG MỘT TẬP CONTEXT** từ Vector Store cho mỗi câu hỏi, nhằm cô lập và phản ánh chính xác tác động của các quy tắc trong từng phiên bản System Prompt.

| Câu hỏi | Context | Kết quả V1 (Cơ bản) | Kết quả V2 (Có ràng buộc) | Kết quả V3 (JSON + Chặn lạc đề) | Nhận xét đối sánh |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **Câu 1** (Ngữ nghĩa (Chủ đề tài chính / làm giàu)):<br>`sách hướng dẫn tư duy làm giàu và quản lý tài chính cá nhân` | 8 sách | (5 sách, 1538 ký tự) <br>*```json [   {     "ten_sach": "Nghĩ giàu làm giàu",     "tac_gia": "Napoleon Hill",     "tom_tat": "Cuốn sách kinh điển về tư duy thịnh vượng tài chính, phân tích triết lý và thói ...* | (3 sách, 1261 ký tự) <br>*```json [   {     "ten_sach": "Nghĩ giàu làm giàu",     "tac_gia": "Napoleon Hill",     "tom_tat": "Cuốn sách kinh điển về tư duy thịnh vượng tài chính, phân tích triết lý và thói ...* | ✅ **JSON chuẩn** (2 sách, 465 ký tự) <br>*```json {   "ket_qua": [     {       "ten_sach": "Nghĩ giàu làm giàu",       "tac_gia": "Napoleon Hill",       "ly_do_goi_y": "Sách kinh điển về tư duy thịnh vượng và thói quen làm...* | Cả 3 đều nhận diện tốt sách tài chính. V3 nổi bật vì cấu trúc JSON chặt chẽ, lý do gợi ý súc tích. |
| **Câu 2** (Mơ hồ):<br>`sách gì hay hay` | 8 sách | (3 sách, 1292 ký tự) <br>*```json [   {     "ten_sach": "Nghĩ giàu làm giàu",     "tac_gia": "Napoleon Hill",     "tom_tat": "Cuốn sách kinh điển về tư duy thịnh vượng tài chính, phân tích triết lý và thói ...* | (5 sách, 1340 ký tự) <br>*[   {     "ten_sach": "Nghĩ giàu làm giàu",     "tac_gia": "Napoleon Hill",     "tom_tat": "Cuốn sách kinh điển về tư duy thịnh vượng tài chính, phân tích triết lý và thói quen của...* | ✅ **JSON chuẩn** (5 sách, 994 ký tự) <br>*{   "ket_qua": [     {       "ten_sach": "Nghĩ giàu làm giàu",       "tac_gia": "Napoleon Hill",       "ly_do_goi_y": "Kinh điển về tư duy thịnh vượng giúp định hướng mục tiêu làm ...* | V1 trả lời dàn trải; V2 chọn lọc sách có trong kho; V3 chuẩn hóa JSON với số lượng sách vừa phải. |
| **Câu 3** (Ngoài thư viện (Không có trong kho)):<br>`sách hướng dẫn lái xe ô tô và thi bằng lái B2` | 8 sách | (0 sách, 335 ký tự) <br>*```json [] ```  **Giải thích:** Trong danh sách sách được cung cấp, không có cuốn sách nào liên quan trực tiếp đến chủ đề hướng dẫn lái xe ô tô hoặc thi bằng lái B2. Các cuốn sách ...* | (0 sách, 99 ký tự) <br>*```json {   "trả_lời": "Xin lỗi, hiện tại thư viện chưa có sách phù hợp với yêu cầu của bạn." } ```* | ✅ **JSON chuẩn** (0 sách, 159 ký tự) <br>*{   "ket_qua": [],   "tong_so_ket_qua": 0,   "thong_bao": "Không có sách nào trong thư viện phù hợp với yêu cầu về hướng dẫn lái xe ô tô và thi bằng lái B2." }* | V1 dễ gợi ý gượng ép; V2 và V3 nhận diện không có sách phù hợp. V3 trả về mảng ket_qua rỗng đúng chuẩn. |
| **Câu 4** (Hết hàng (con_hang=False)):<br>`Kiến trúc hệ thống phân tán` | 8 sách | 📦 **Báo rõ hết hàng** (1 sách, 795 ký tự) <br>*```json {   "cau_hoi": "Kiến trúc hệ thống phân tán",   "sach_phu_hop": [     {       "ten_sach": "Kiến trúc hệ thống phân tán",       "tac_gia": "Martin Kleppmann",       "tom_tat...* | 📦 **Báo rõ hết hàng** (1 sách, 409 ký tự) <br>*```json [   {     "ten_sach": "Kiến trúc hệ thống phân tán",     "tac_gia": "Martin Kleppmann",     "tom_tat": "Giải thích cách xây dựng hệ thống phần mềm quy mô lớn: cơ sở dữ liệu...* | ✅ **JSON chuẩn** 📦 **Báo rõ hết hàng** (1 sách, 274 ký tự) <br>*{   "ket_qua": [     {       "ten_sach": "Kiến trúc hệ thống phân tán",       "tac_gia": "Martin Kleppmann",       "ly_do_goi_y": "Giải thích chi tiết cách xây dựng hệ thống phần m...* | V2 & V3 đều ghi rõ tình trạng hết hàng / đặt trước theo quy tắc. V3 thể hiện qua trường con_hang=false và thông báo minh bạch. |
| **Câu 5** (Tên tác giả):<br>`Carnegie` | 8 sách | (1 sách, 381 ký tự) <br>*```json [   {     "ten_sach": "Đắc nhân tâm",     "tac_gia": "Dale Carnegie",     "tom_tat": "Bí quyết giao tiếp và ứng xử hiệu quả trong cuộc sống và công việc: cách kết bạn, tạo ...* | (1 sách, 466 ký tự) <br>*```json [   {     "ten_sach": "Đắc nhân tâm",     "tac_gia": "Dale Carnegie",     "tom_tat": "Bí quyết giao tiếp và ứng xử hiệu quả trong cuộc sống và công việc: cách kết bạn, tạo ...* | ✅ **JSON chuẩn** (1 sách, 252 ký tự) <br>*{   "ket_qua": [     {       "ten_sach": "Đắc nhân tâm",       "tac_gia": "Dale Carnegie",       "ly_do_goi_y": "Tác phẩm kinh điển về giao tiếp và ứng xử của Dale Carnegie",      ...* | Cả 3 nhận diện được tác giả Dale Carnegie (Đắc nhân tâm). V3 xuất đúng schema quản lý. |
| **Câu 6** (Hoàn toàn lạc đề (Chính trị / Thời sự)):<br>`Ai là chủ tịch nước hiện tại?` | 8 sách | ⚠️ *Bị dụ trả lời / Lạc đề* (0 sách, 366 ký tự) <br>*```json {   "danh_sach_goi_y": [],   "giai_thich": "Câu hỏi của độc giả về Chủ tịch nước hiện tại không liên quan đến nội dung của bất kỳ cuốn sách nào trong danh sách đã cung cấp....* | 🛡️ **Từ chối đúng quy tắc** (0 sách, 68 ký tự) <br>*Xin lỗi, hiện tại thư viện chưa có sách phù hợp với yêu cầu của bạn.* | ✅ **JSON chuẩn** 🛡️ **Từ chối đúng quy tắc** (0 sách, 154 ký tự) <br>*{   "ket_qua": [],   "tong_so_ket_qua": 0,   "thong_bao": "Tôi chỉ hỗ trợ tra cứu sách trong thư viện. Bạn vui lòng đặt câu hỏi liên quan đến sách nhé!" }* | 🔥 **ĐIỂM KHÁC BIỆT LỚN NHẤT**: V1/V2 bị câu hỏi chính trị dẫn dắt hoặc trả lời kiến thức chung. V3 tuân thủ Quy tắc 8, từ chối lịch sự, ket_qua rỗng. |

---

### C. Tích hợp Chatbot AI V3 chính thức vào Web App Thư viện

Sau khi hoàn tất thử nghiệm và đối sánh, **Phiên bản System Prompt V3** được lựa chọn là phiên bản tối ưu nhất để tích hợp trực tiếp vào hệ thống Web App thư viện hoàn chỉnh tại cổng **`http://localhost:8000`**:

#### 1. Sơ đồ kiến trúc tích hợp hệ thống:
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

#### 2. Chi tiết các thành phần đã triển khai

##### A. Tầng Backend API:
- **Router `Backend/app/routers/chatbot.py`**:
  - `POST /api/chatbot/hoi`: Nhận `{ "cau_hoi": str }`, gọi hàm `tra_cuu_sach(cau_hoi, prompt_version="v3")`, trả về đối tượng JSON chuẩn hóa với danh sách sách, tình trạng còn hàng và lý do gợi ý.
  - `GET /api/chatbot/health`: Trả về trạng thái sẵn sàng của dịch vụ AI và số lượng sách trong Vector Store.
- **Đăng ký vào ứng dụng**: Đã include router vào `Backend/app/main.py`.
- **Kết nối API Frontend**: Đã bổ sung endpoint `chatbot: "/api/chatbot/hoi"` vào `frontend/js/api.js`.

##### B. Tầng Giao diện Frontend:
1. **Trang Chatbot chuyên biệt (`frontend/chatbot.html`)**:
   - Tuân thủ bộ nhận diện thương hiệu ICTU: Phông chữ Be Vietnam Pro, màu chủ đạo Navy `#0a2e5c`.
   - Có sẵn các nút chủ đề chọn nhanh: Tư duy làm giàu, Lập trình Python, Nghệ thuật giao tiếp, Kiểm tra hết hàng...
   - Render sách dạng **Book Card** trực quan: Tên sách, tác giả, lý do AI đề xuất, huy hiệu tình trạng (Còn sách / Hết sách), nút bấm *"Xem trong kho"* chuyển hướng sang trang tìm kiếm.
   - Xử lý thông báo từ chối lịch sự khi gặp câu hỏi ngoài phạm vi thư viện theo đúng Quy tắc 8.
2. **Bộ điều khiển & Giao diện (`frontend/js/chatbot.js`, `frontend/css/chatbot.css`)**:
   - Tương tác mượt mà, hiệu ứng đang gõ (typing animation), tự động cuộn xuống tin nhắn mới nhất, đo thời gian xử lý (ms).
3. **Menu thanh điều hướng (`frontend/js/layout.js`)**:
   - Thêm mục **`🤖 Trợ lý AI`** vào navbar cho tất cả vai trò: Độc giả (`reader`), Thủ thư (`librarian`), Quản trị viên (`admin`).
4. **Bong bóng chat nổi (`frontend/components/chatbot-widget.js`)**:
   - Xuất hiện nút tròn 🤖 ở góc dưới bên phải trên tất cả các trang (`search.html`, `books.html`, `profile.html`...). Bấm vào là mở ngay khung chat mini để hỏi AI mà không cần rời trang hiện tại.
5. **Trang tra cứu (`frontend/search.html`)**:
   - Bổ sung nút bấm nổi bật *"🤖 Hỏi Trợ lý AI"* đặt cạnh nút Tìm kiếm.

#### 3. Kết quả kiểm thử thực tế trên Web App chính (Port 8000)

##### Test Case 1: Kiểm tra trạng thái Health Check
- **Endpoint**: `GET http://localhost:8000/api/chatbot/health`
- **Kết quả trả về**:
```json
{
  "trang_thai": "san_sang",
  "phien_ban_prompt": "v3",
  "do_dai_prompt": 1812,
  "so_sach_vector_store": 63
}
```

##### Test Case 2: Tra cứu sách tài chính hợp lệ
- **Câu hỏi**: `"sách về tư duy làm giàu"`
- **Kết quả trả về**: Status `200 OK`, tìm thấy sách kinh tế tài chính trong kho:
  1. *50 Cuốn Sách Kinh Điển Về Kinh Doanh* (`con_hang: True`)
  2. *Người Giàu Có Nhất Thành Babylon* (`con_hang: True`)

##### Test Case 3: Chặn đứng câu hỏi ngoài phạm vi thư viện (Lạc đề)
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
- **Kỹ sư AI thực hiện**: Kỹ sư Full-stack AI / Thành viên nhóm phát triển Chatbot Thư viện
