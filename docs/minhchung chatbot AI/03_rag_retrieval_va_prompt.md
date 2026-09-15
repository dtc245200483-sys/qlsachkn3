# Minh Chứng Kỹ Thuật: RAG Retrieval & Prompt Engineering

## Prompt đã dùng
```text
Bạn là kỹ sư AI. Dự án nằm tại: D:\ung dung tri tue nhan tao\app

Hãy xây dựng tầng RAG Retrieval hoàn chỉnh cho chatbot tra cứu sách, 
kết hợp Vector Store (embedding, đã có ở chatbotAI\vector_store.py) với 
fuzzy match tên riêng (tên sách/tác giả), sau đó ghép context vào LLM 
để sinh câu trả lời cuối cùng.

VỊ TRÍ FILE CẦN TẠO:
- chatbotAI/rag_retriever.py
- chatbotAI/prompts/system_prompt.txt
- chatbotAI/prompt_builder.py
- chatbotAI/chatbot_service.py

[... nội dung đầy đủ như yêu cầu gốc ...]
```

---

## Phản hồi/Kết quả của AI

### 1. Danh sách file đã tạo

| File | Mô tả |
|------|-------|
| `chatbotAI/rag_retriever.py` | Retrieval: embedding + fuzzy match tên riêng, gộp kết quả |
| `chatbotAI/prompts/system_prompt.txt` | System prompt RAG-aware, schema JSON cố định |
| `chatbotAI/prompt_builder.py` | Ghép câu hỏi + context thành user prompt |
| `chatbotAI/chatbot_service.py` | Luồng RAG 7 bước hoàn chỉnh + lớp chống bịa |

---

### 2. Kiến trúc luồng RAG

```
Câu hỏi
   ↓
[rag_retriever.py] ── Embedding search (VectorStore)   ──┐
                   └─ Fuzzy match tên riêng (rapidfuzz) ──┘
                          ↓ Gộp + sắp xếp (top_k=8)
                   [context: list[dict]]
                          ↓
[prompt_builder.py] ── Ghép thành user_prompt
                          ↓
[system_prompt.txt] ── System prompt RAG-aware
                          ↓
[llm_client.py] ───────── call_llm() → OpenRouter API (deepseek-chat)
                          ↓
[chatbot_service.py] ──── Parse JSON + Lọc bịa dữ liệu
                          ↓
                   Kết quả cuối cùng
```

**Công thức điểm tổng hợp:**
```
bonus          = 0.3  nếu khớp cả 2 nguồn (embedding + fuzzy)
fuzzy_chuan    = diem_khop_ten / 100.0
diem_lien_quan = max(diem_tuong_dong, fuzzy_chuan) + bonus
```

---

### 3. Kết quả kiểm thử 3 câu hỏi — Kết quả thực tế (LLM đã phản hồi)

**Môi trường:** ChromaDB 1.5.9 | paraphrase-multilingual-MiniLM-L12-v2 | deepseek/deepseek-chat via OpenRouter

---

#### 📌 Test 1: `"sách dạy làm bếp và chế biến thức ăn"` — Ngữ nghĩa
*Từ "làm bếp", "chế biến" không xuất hiện trong tên/tóm tắt sách nào*

**Context Retriever tìm được (8 sách):**

| # | Nguồn | Điểm | Tên sách | Tác giả |
|---|-------|------|---------|---------|
| 1 | ngu_nghia | 0.637 | Lập trình Python từ cơ bản đến nâng cao | Nguyễn Thành Nam |
| 2 | ngu_nghia | 0.636 | Nghĩ giàu làm giàu | Napoleon Hill |
| 3 | ngu_nghia | 0.630 | Tắt đèn | Ngô Tất Tố |
| 4 | ngu_nghia | 0.628 | Cha giàu cha nghèo | Robert T. Kiyosaki |
| 5 | ngu_nghia | 0.626 | 7 Thói quen của người hiệu quả | Stephen R. Covey |
| 6 | ngu_nghia | 0.618 | Đắc nhân tâm | Dale Carnegie |
| 7 | ngu_nghia | 0.588 | Trí tuệ nhân tạo: Tiếp cận hiện đại | Stuart Russell |
| 8 | ngu_nghia | 0.586 | Số đỏ | Vũ Trọng Phụng |

**Câu trả lời LLM:**
```json
{
  "ket_qua": [],
  "tong_so_ket_qua": 0,
  "thong_bao": "Không tìm thấy sách nào về dạy làm bếp và chế biến thức ăn trong danh sách."
}
```

**✅ Kết quả: LLM đánh giá lại đúng** — dù Retriever trả 8 sách sơ bộ, LLM nhận ra không có cuốn nào thực sự về nấu ăn và trả về danh sách rỗng + giải thích rõ lý do.

---

#### 📌 Test 2: `"Carnegie"` — Fuzzy match tên tác giả

**Context Retriever tìm được (8 sách — "Đắc nhân tâm" lên #1 điểm 1.300):**

| # | Nguồn | Điểm | Tên sách | Tác giả |
|---|-------|------|---------|---------|
| ★1 | **ngu_nghia+ten_rieng** | **1.300** | **Đắc nhân tâm** | **Dale Carnegie** |
| 2 | ngu_nghia | 0.610 | Nghĩ giàu làm giàu | Napoleon Hill |
| 3 | ngu_nghia | 0.604 | Lược sử thời gian | Nguyễn Thành Nam |
| 4 | ngu_nghia | 0.583 | 7 Thói quen của người hiệu quả | Stephen R. Covey |
| 5 | ngu_nghia | 0.576 | Số đỏ | Vũ Trọng Phụng |
| 6 | ngu_nghia | 0.576 | Cha giàu cha nghèo | Robert T. Kiyosaki |
| 7 | ngu_nghia | 0.550 | Kiến trúc hệ thống phân tán | Martin Kleppmann |
| 8 | ngu_nghia | 0.513 | Lập trình Python | Nguyễn Thành Nam |

**Câu trả lời LLM:**
```json
{
  "ket_qua": [
    {
      "ten_sach": "Đắc nhân tâm",
      "tac_gia": "Dale Carnegie",
      "ly_do_goi_y": "Sách của tác giả Dale Carnegie, phù hợp với từ khóa tìm kiếm.",
      "con_hang": true
    }
  ],
  "tong_so_ket_qua": 1,
  "thong_bao": ""
}
```

**✅ Kết quả: Fuzzy match hoạt động đúng** — tên tác giả "Carnegie" khớp "Dale Carnegie" → điểm 1.300 (bonus khớp 2 nguồn) → LLM chọn đúng "Đắc nhân tâm" và loại bỏ 7 sách không liên quan.

---

#### 📌 Test 3: `"sách dạy lái xe hơi và thi bằng lái"` — Không có sách phù hợp

**Context Retriever tìm được (8 sách — điểm thấp, không có sách lái xe):**

| # | Nguồn | Điểm | Tên sách |
|---|-------|------|---------|
| 1 | ngu_nghia | 0.618 | Tắt đèn |
| 2 | ngu_nghia | 0.591 | 7 Thói quen của người hiệu quả |
| 3 | ngu_nghia | 0.590 | Đắc nhân tâm |
| ... | ... | ... | ... |

**Câu trả lời LLM:**
```json
{
  "ket_qua": [],
  "tong_so_ket_qua": 0,
  "thong_bao": "Không tìm thấy sách về dạy lái xe hoặc thi bằng lái trong danh sách được cung cấp."
}
```

**✅ Kết quả: LLM từ chối gợi ý đúng** — không cố gợi ý sách không liên quan, trả thông báo rõ ràng.

---

### 4. Tổng kết kết quả kiểm thử

```
TEST 1 (Ngữ nghĩa - không có sách phù hợp): ✅ PASS
  → LLM đánh giá lại đúng, trả ket_qua rỗng + giải thích

TEST 2 (Tên tác giả - fuzzy match):          ✅ PASS  
  → Fuzzy match đẩy "Đắc nhân tâm" lên điểm 1.300, LLM chọn đúng

TEST 3 (Ngoài phạm vi - lái xe):             ✅ PASS
  → LLM từ chối gợi ý, thông báo rõ "không có sách phù hợp"

🎉 TẤT CẢ 3 TEST PASS — Luồng RAG hoàn chỉnh hoạt động đúng!
```

---

### 5. Giải thích bước "đối chiếu chống bịa" (Phần 4 Mục 7)

**Câu hỏi: Vì sao cần bước đối chiếu dù system prompt đã ràng buộc?**

| Lý do | Giải thích |
|-------|-----------|
| **LLM không đảm bảo tuyệt đối** | Dù prompt ràng buộc, LLM vẫn có thể hallucinate — đặc biệt với model nhỏ/rẻ hoặc khi context quá dài |
| **Defense in depth** | Nguyên tắc bảo mật: không tin vào một lớp duy nhất. Prompt là lớp 1, đối chiếu là lớp 2 hoàn toàn độc lập |
| **Phát hiện và log** | Ghi `warning("AI có dấu hiệu bịa dữ liệu")` → có bằng chứng audit sau |
| **Chi phí O(1)** | Set lookup cực nhanh, không tốn thêm token hay API call |
| **Bảo vệ độc giả** | Thư viện trường học — thông tin sách sai gây mất niềm tin nghiêm trọng |

### 6. Bổ sung 2 lớp bảo vệ chống câu hỏi lạc đề (Out-of-Domain Guardrails)

#### Prompt bổ sung đã dùng:
```text
Bạn là kỹ sư AI. Dự án nằm tại: D:\ung dung tri tue nhan tao\app

Bổ sung 2 lớp bảo vệ cho chatbot chống câu hỏi lạc đề (ngoài phạm vi 
thư viện, VD: chính trị, thời sự, đời tư, spam), vào các file đã có:
D:\ung dung tri tue nhan tao\app\chatbotAI\rag_retriever.py
D:\ung dung tri tue nhan tao\app\chatbotAI\chatbot_service.py
D:\ung dung tri tue nhan tao\app\chatbotAI\prompts\system_prompt.txt
(và cả 3 file v1/v2/v3 nếu đã tồn tại)

YÊU CẦU:
1. Trong rag_retriever.py, hàm truy_xuat_context(): thêm tham số 
   nguong_lien_quan: float = 0.35. Sau khi có kết quả cuối cùng, LỌC 
   BỎ những sách có điểm liên quan (diem_tuong_dong hoặc 
   diem_khop_ten quy đổi về cùng thang 0-1) THẤP HƠN ngưỡng này. Nếu 
   sau khi lọc không còn cuốn nào, trả về list rỗng.

2. Trong chatbot_service.py, hàm tra_cuu_sach(): khi context rỗng 
   (do không tìm thấy HOẶC do bị lọc ở bước 1), phân biệt 2 
   trường hợp bằng cách kiểm tra thêm: nếu điểm cao nhất trước khi 
   lọc (nếu có) vẫn rất thấp (< 0.15) → đây là dấu hiệu câu hỏi HOÀN 
   TOÀN lạc đề, trả về thong_bao = "Tôi chỉ hỗ trợ tra cứu sách trong 
   thư viện. Bạn vui lòng đặt câu hỏi liên quan đến sách nhé!" Nếu 
   điểm ở mức trung bình (0.15 - 0.35) → có thể là câu hỏi về sách 
   nhưng thư viện chưa có, trả về thong_bao = "Không tìm thấy sách 
   phù hợp trong thư viện." Cả 2 trường hợp đều KHÔNG gọi LLM.

3. Trong TẤT CẢ các file system prompt (system_prompt.txt, v1, v2, 
   v3 nếu tồn tại), thêm 1 quy tắc riêng biệt với các quy tắc đã có:
   "Nếu câu hỏi của độc giả không liên quan đến việc tìm sách hoặc 
   thư viện (ví dụ: hỏi về chính trị, thời sự, đời tư, kiến thức 
   chung không liên quan đến sách), hãy từ chối lịch sự và nhắc rằng 
   bạn chỉ hỗ trợ tra cứu sách trong thư viện, KHÔNG cố gắng trả lời 
   câu hỏi đó dù có kiến thức, và KHÔNG gán ghép sách không liên quan 
   vào câu trả lời."

KIỂM THỬ (bắt buộc):
Chạy thử tra_cuu_sach() với 3 câu hỏi hoàn toàn lạc đề:
1. "Ai là chủ tịch nước hiện tại?"
2. "Cho tôi công thức nấu phở"
3. "1 với 1 bằng mấy?"
Xác nhận cả 3 đều bị chặn ở bước similarity threshold (KHÔNG gọi 
LLM), in ra log xác nhận "đã chặn ở tầng retrieval, không tốn API 
call" cho từng câu.

Sau đó chạy thử 1 câu hỏi THỰC SỰ về sách nhưng thư viện không có 
(VD: "sách Harry Potter") để xác nhận nó KHÔNG bị nhầm sang nhánh 
"lạc đề hoàn toàn" mà vẫn đi đúng nhánh "không có sách phù hợp".
```

#### Kiến trúc 2 tầng phòng ngự (Defense-in-Depth):
```
                                  Câu hỏi người dùng
                                          │
                                          ▼
                   ┌──────────────────────────────────────────────┐
                   │   LỚP 1: BẢO VỆ TẦNG RETRIEVAL               │
                   │   - rag_retriever.py: nguong_lien_quan = 0.35│
                   │   - Lọc bỏ mọi sách có điểm < 0.35           │
                   │   - Ghi nhận diem_cao_nhat_truoc_loc         │
                   └──────────────────────┬───────────────────────┘
                                          │
                        ┌─────────────────┴─────────────────┐
                        │ Context rỗng?                     │
                        ▼                                   ▼
                      [CÓ]                                [KHÔNG]
                        │                          (Đạt ngưỡng >= 0.35)
                        │                                   │
      ┌─────────────────┴─────────────────┐                 ▼
      │ Kiểm tra diem_cao_nhat_truoc_loc │   ┌──────────────────────────────┐
      ▼                                   ▼   │ Ghép Prompt → Gửi tới LLM    │
 [Điểm < 0.15]                    [0.15 - 0.35] │ (deepseek-chat)              │
 (Lạc đề hoàn toàn)               (Sách ngoài TV)├──────────────────────────────┤
      │                                   │   │ LỚP 2: BẢO VỆ SYSTEM PROMPT │
      ▼                                   ▼   │ - Quy tắc 8: Từ chối lịch sự│
Thoát ngay (NO LLM)              Thoát ngay (NO LLM) │   nếu câu hỏi lạc đề lọt qua │
"Tôi chỉ hỗ trợ tra cứu          "Không tìm thấy sách  │ - Schema JSON chuẩn          │
sách trong thư viện..."          phù hợp trong TV."    └──────────────────────────────┘
```

#### Log kiểm thử thực tế 4 câu hỏi bắt buộc:
```
[CHATBOT_SERVICE] 'Ai là chủ tịch nước hiện tại?' → đã chặn ở tầng retrieval, không tốn API call (câu hỏi hoàn toàn lạc đề (điểm cao nhất 0.0541 < 0.15))
  💬 Thông báo: "Tôi chỉ hỗ trợ tra cứu sách trong thư viện. Bạn vui lòng đặt câu hỏi liên quan đến sách nhé!"
  Kết luận: ✅ PASS (Chặn tầng retrieval: True, Điểm < 0.15: True)

[CHATBOT_SERVICE] 'Cho tôi công thức nấu phở' → đã chặn ở tầng retrieval, không tốn API call (câu hỏi hoàn toàn lạc đề (điểm cao nhất 0.0299 < 0.15))
  💬 Thông báo: "Tôi chỉ hỗ trợ tra cứu sách trong thư viện. Bạn vui lòng đặt câu hỏi liên quan đến sách nhé!"
  Kết luận: ✅ PASS (Chặn tầng retrieval: True, Điểm < 0.15: True)

[CHATBOT_SERVICE] '1 với 1 bằng mấy?' → đã chặn ở tầng retrieval, không tốn API call (câu hỏi hoàn toàn lạc đề (điểm cao nhất 0.0284 < 0.15))
  💬 Thông báo: "Tôi chỉ hỗ trợ tra cứu sách trong thư viện. Bạn vui lòng đặt câu hỏi liên quan đến sách nhé!"
  Kết luận: ✅ PASS (Chặn tầng retrieval: True, Điểm < 0.15: True)

[CHATBOT_SERVICE] 'sách Harry Potter' → đã chặn ở tầng retrieval, không tốn API call (không có sách phù hợp trong thư viện (điểm cao nhất 0.2344 nằm trong [0.15, 0.35]))
  💬 Thông báo: "Không tìm thấy sách phù hợp trong thư viện."
  Kết luận: ✅ PASS (Chặn tầng retrieval: True, Điểm trong [0.15, 0.35]: True)
```

#### Bảng kết quả tổng hợp:
| STT | Câu hỏi kiểm thử | Thể loại | Điểm max trước lọc | Phân nhánh xử lý | Gọi LLM? | Kết quả thông báo | Đánh giá |
|:---:|:---|:---|:---:|:---|:---:|:---|:---:|
| 1 | *"Ai là chủ tịch nước hiện tại?"* | Chính trị / Lãnh đạo | **0.0541** (< 0.15) | Lạc đề hoàn toàn | ❌ KHÔNG | *"Tôi chỉ hỗ trợ tra cứu sách trong thư viện. Bạn vui lòng đặt câu hỏi liên quan đến sách nhé!"* | ✅ PASS |
| 2 | *"Cho tôi công thức nấu phở"* | Ẩm thực / Nấu ăn | **0.0299** (< 0.15) | Lạc đề hoàn toàn | ❌ KHÔNG | *"Tôi chỉ hỗ trợ tra cứu sách trong thư viện. Bạn vui lòng đặt câu hỏi liên quan đến sách nhé!"* | ✅ PASS |
| 3 | *"1 với 1 bằng mấy?"* | Toán đố / Spam | **0.0284** (< 0.15) | Lạc đề hoàn toàn | ❌ KHÔNG | *"Tôi chỉ hỗ trợ tra cứu sách trong thư viện. Bạn vui lòng đặt câu hỏi liên quan đến sách nhé!"* | ✅ PASS |
| 4 | *"sách Harry Potter"* | Sách ngoài thư viện | **0.2344** (0.15 - 0.35) | Sách chưa có | ❌ KHÔNG | *"Không tìm thấy sách phù hợp trong thư viện."* | ✅ PASS |
| 5 | *"Carnegie"* | Sách có trong TV | **1.3000** (>= 0.35) | Đạt ngưỡng context |  CÓ | Gợi ý cuốn *"Đắc nhân tâm"* | ✅ PASS |

---

## Phần sinh viên đã kiểm tra/chỉnh sửa
(sinh viên tự điền sau khi review code)

---

## Ngày thực hiện
15/09/2026 11:20
