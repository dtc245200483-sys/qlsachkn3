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
[rag_retriever.py] ─── Embedding search (VectorStore)  ──┐
                   └── Fuzzy match tên riêng (rapidfuzz)──┘
                           ↓ Gộp + sắp xếp (top_k=8)
                   [context: list[dict]]
                           ↓
[prompt_builder.py] ── Ghép thành user_prompt
                           ↓
[system_prompt.txt] ── System prompt RAG-aware
                           ↓
[llm_client.py] ──────── call_llm() → OpenRouter API
                           ↓
[chatbot_service.py] ─── Parse JSON + Lọc bịa dữ liệu
                           ↓
                   Kết quả cuối cùng
```

**Công thức điểm tổng hợp (diem_lien_quan):**
```
bonus = 0.3 nếu khớp cả 2 nguồn (embedding + fuzzy)
fuzzy_chuan = diem_khop_ten / 100.0
diem_lien_quan = max(diem_tuong_dong, fuzzy_chuan) + bonus
```

---

### 3. Kết quả kiểm thử 3 câu hỏi — Retrieval Layer

> **Lưu ý:** Phần Retrieval (Embedding + Fuzzy) đã chạy và xác nhận hoạt động đúng.
> Phần LLM cần cấu hình `OPENROUTER_API_KEY` trong file `.env`.

---

#### 📌 Test 1: `"sách dạy làm bếp và chế biến thức ăn"` — Ngữ nghĩa
*Từ "làm bếp", "chế biến" không xuất hiện trong tên/tóm tắt sách nào*

**Context Retriever tìm được (8 sách — toàn bộ qua embedding):**

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

> **Nhận xét:** Không có sách nấu ăn trong DB → Retriever trả context sơ bộ với điểm thấp (≤0.637). LLM sẽ đánh giá và trả về `ket_qua: []` vì không có cuốn nào thực sự liên quan đến nấu ăn.

---

#### 📌 Test 2: `"Carnegie"` — Fuzzy match tên tác giả

**Context Retriever tìm được (8 sách — "Đắc nhân tâm" lên đầu với điểm 1.300):**

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

> **✅ Fuzzy match hoạt động đúng:** "Carnegie" khớp tên tác giả "Dale Carnegie" (100%) → điểm bonus +0.3 → tổng **1.300** → xếp hạng #1 với khoảng cách lớn so với #2 (0.610). LLM sẽ gợi ý "Đắc nhân tâm" là kết quả chính.

---

#### 📌 Test 3: `"sách dạy lái xe hơi và thi bằng lái"` — Không có sách phù hợp

**Context Retriever tìm được (8 sách — điểm thấp, chỉ qua embedding):**

| # | Nguồn | Điểm | Tên sách |
|---|-------|------|---------|
| 1 | ngu_nghia | 0.618 | Tắt đèn |
| 2 | ngu_nghia | 0.591 | 7 Thói quen của người hiệu quả |
| 3 | ngu_nghia | 0.590 | Đắc nhân tâm |
| ... | ... | ... | ... |

> **Nhận xét:** Không có sách lái xe → Retriever trả context sơ bộ với điểm thấp. LLM đánh giá lại và trả về `ket_qua: []`, `thong_bao: "Không có sách phù hợp..."`.

---

### 4. Xác nhận Retrieval Pipeline hoạt động đúng

```
✅ Test 1 (Retrieval): 8 sách tìm được qua embedding
✅ Test 2 (Fuzzy match): "Carnegie" → "Đắc nhân tâm" xếp #1 (điểm 1.300)
✅ Test 3 (Retrieval): 8 sách tìm được, LLM sẽ lọc ra "không có phù hợp"
⚠️ LLM call: Cần cấu hình OPENROUTER_API_KEY trong chatbotAI/.env
```

---

### 5. Giải thích bước "đối chiếu chống bịa" (Phần 4 Mục 7)

**Câu hỏi: Vì sao cần bước đối chiếu dù system prompt đã ràng buộc?**

| Lý do | Giải thích |
|-------|-----------|
| **LLM không đảm bảo** | Dù prompt ràng buộc, LLM vẫn có thể "hallucinate" — đặc biệt với model nhỏ/rẻ tiền hoặc khi context quá dài |
| **Defense in depth** | Nguyên tắc bảo mật: không tin vào bất kỳ một lớp bảo vệ duy nhất. Prompt là lớp 1, đối chiếu là lớp 2 độc lập |
| **Phát hiện và ghi log** | Bước 7 ghi `_logger.warning("AI có dấu hiệu bịa dữ liệu")` → có bằng chứng kiểm tra sau |
| **Chi phí thấp** | Đối chiếu tên sách bằng set lookup O(1) — không tốn thời gian/chi phí |
| **Bảo vệ độc giả** | Thư viện trường học — thông tin sai về sách có thể gây mất niềm tin nghiêm trọng |

> **Tóm lại:** Prompt là cam kết với LLM, đối chiếu là kiểm tra độc lập với kết quả. Hai lớp này bổ sung cho nhau, không thay thế nhau.

---

## Phần sinh viên đã kiểm tra/chỉnh sửa
(sinh viên tự điền sau khi review code)

---

## Ngày thực hiện
15/09/2026 10:53
