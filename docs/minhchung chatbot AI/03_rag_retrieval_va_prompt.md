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

> **Kết luận:** Prompt là *cam kết với LLM*, đối chiếu là *kiểm tra độc lập với đầu ra*. Hai lớp bổ sung cho nhau, không thay thế nhau.

---

## Phần sinh viên đã kiểm tra/chỉnh sửa
(sinh viên tự điền sau khi review code)

---

## Ngày thực hiện
15/09/2026 11:00
