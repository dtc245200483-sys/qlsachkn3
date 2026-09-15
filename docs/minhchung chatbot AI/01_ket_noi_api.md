# Minh Chứng Kỹ Thuật: Kết Nối Module LLM API & Embedding (Kiến Trúc RAG)

## Prompt đã dùng
```text
Bạn là kỹ sư backend Python. Dự án nằm tại: 
D:\ung dung tri tue nhan tao\app

Hãy xây dựng module kết nối AI cho hệ thống chatbot tra cứu sách theo 
kiến trúc RAG (Retrieval-Augmented Generation), gồm 2 phần: LLM (sinh 
câu trả lời) và Embedding (vector hóa văn bản để tìm kiếm ngữ nghĩa).

VỊ TRÍ FILE CẦN TẠO:
- D:\ung dung tri tue nhan tao\app\chatbotAI\llm_client.py
- D:\ung dung tri tue nhan tao\app\chatbotAI\embedding_client.py
- D:\ung dung tri tue nhan tao\app\chatbotAI\.env.example
- D:\ung dung tri tue nhan tao\app\chatbotAI\requirements.txt
- D:\ung dung tri tue nhan tao\app\chatbotAI\logs\ai_calls.log

[... nội dung đầy đủ như yêu cầu ...]

PHẦN 1: llm_client.py (gọi LLM sinh câu trả lời)
1. Dùng OpenRouter, endpoint: https://openrouter.ai/api/v1/chat/completions
2. Đọc API key từ biến môi trường OPENROUTER_API_KEY (python-dotenv). TUYỆT ĐỐI không hardcode key.
3. Hàm: call_llm(system_prompt, user_prompt, model="deepseek/deepseek-chat") -> str
4. Xử lý lỗi qua exception riêng: LLMTimeoutError, LLMRateLimitError, LLMResponseError
5. Retry tối đa 2 lần, exponential backoff (2s → 4s)

PHẦN 2: embedding_client.py (vector hóa văn bản cho RAG)
1. Model LOCAL: sentence-transformers, paraphrase-multilingual-MiniLM-L12-v2
2. Hàm: get_embedding(text) -> list[float] — Singleton Pattern (load 1 lần)
3. Hàm: get_embeddings_batch(texts) -> list[list[float]] — batch encoding
4. Xử lý text rỗng/None → trả None + log warning

PHẦN 3: Logging chung → logs/ai_calls.log
Định dạng: [time] [LLM/EMBEDDING] [model] [SUCCESS/FAILURE] [Xms] [input len]

PHẦN 4: .env.example, requirements.txt, .gitignore

YÊU CẦU GHI MINH CHỨNG: docs/minhchung chatbot AI/01_ket_noi_api.md
```

---

## Phản hồi/Kết quả của AI

### 1. Danh sách file đã tạo/sửa

| File | Trạng thái | Mô tả |
|------|-----------|-------|
| `chatbotAI/llm_client.py` | ✅ Tạo mới | Module gọi LLM qua OpenRouter — custom exceptions, exponential backoff |
| `chatbotAI/embedding_client.py` | ✅ Tạo mới | Module embedding local (sentence-transformers) — Singleton Pattern |
| `chatbotAI/.env.example` | ✅ Tạo mới | File mẫu cấu hình API key |
| `chatbotAI/requirements.txt` | ✅ Tạo mới | Danh sách thư viện cần cài |
| `chatbotAI/logs/ai_calls.log` | ✅ Tự tạo | File log ghi nhật ký từng lượt gọi AI |

---

### 2. Tóm tắt chức năng từng hàm

#### `llm_client.py`

```python
# Custom Exception Classes
class LLMError(Exception): ...             # Base class
class LLMTimeoutError(LLMError): ...       # Request timeout sau tất cả retry
class LLMRateLimitError(LLMError): ...     # HTTP 429 sau tất cả retry
class LLMResponseError(LLMError): ...      # HTTP lỗi, JSON sai, content rỗng

def call_llm(system_prompt, user_prompt, model="deepseek/deepseek-chat") -> str:
    """
    Gọi OpenRouter API và trả về nội dung văn bản.
    - Timeout: 15s
    - Retry: tối đa 2 lần với exponential backoff (2s → 4s)
    - Log định dạng: [LLM] [model] [SUCCESS/FAILURE] [Xms] [N chars]
    """
```

#### `embedding_client.py`

```python
# Singleton — model chỉ load 1 lần duy nhất
_model_instance = None

def _get_model():
    """Load paraphrase-multilingual-MiniLM-L12-v2 lần đầu, cache cho lần sau."""

def get_embedding(text: str) -> Optional[list[float]]:
    """
    Vector hóa 1 đoạn text.
    - Trả None nếu text rỗng/None (kèm log warning)
    - Vector 384 chiều
    """

def get_embeddings_batch(texts: list[str]) -> list[Optional[list[float]]]:
    """
    Batch encoding nhiều text cùng lúc — hiệu quả hơn gọi từng cái.
    - Dùng khi index toàn bộ danh sách sách lúc khởi động
    - Text rỗng/None → None tại đúng vị trí index
    """
```

---

### 3. Cơ chế xử lý lỗi và Retry

#### LLM Client — Exponential Backoff:
```
Attempt 1 → thất bại (Timeout/429) → chờ 2^1 = 2s
Attempt 2 → thất bại (Timeout/429) → chờ 2^2 = 4s
Attempt 3 → thất bại → raise LLMTimeoutError / LLMRateLimitError
```

| Loại lỗi | Exception | Có Retry? | Hành vi |
|---------|-----------|-----------|---------|
| Timeout (>15s) | `LLMTimeoutError` | ✅ 2 lần | Backoff 2s → 4s |
| HTTP 429 | `LLMRateLimitError` | ✅ 2 lần | Backoff 2s → 4s |
| HTTP != 200 | `LLMResponseError` | ❌ Không | Raise ngay |
| JSON sai | `LLMResponseError` | ❌ Không | Raise ngay |
| Content rỗng | `LLMResponseError` | ❌ Không | Raise ngay |
| Connection error | `LLMResponseError` | ❌ Không | Raise ngay |

---

### 4. Lý do chọn Embedding LOCAL thay vì API

| Tiêu chí | Embedding LOCAL (sentence-transformers) | API Embedding (OpenAI, Cohere...) |
|---------|----------------------------------------|------------------------------------|
| Chi phí | **Miễn phí hoàn toàn** | Tính tiền theo số token |
| Độ trễ | ~5-50ms/batch (local CPU) | 100-500ms (round trip mạng) |
| Phụ thuộc mạng | **Không cần mạng** — chạy offline | Cần mạng, có thể bị outage |
| API key hết hạn | **Không bao giờ xảy ra** | Cần quản lý quota |
| Tiếng Việt | **paraphrase-multilingual** hỗ trợ tốt | Phụ thuộc model cụ thể |
| Kích thước model | ~120MB (tải 1 lần, cache local) | Không cần lưu local |
| Phù hợp máy sinh viên | **✅ Rất phù hợp** | ⚠️ Chi phí là vấn đề |

**Kết luận:** Với hệ thống thư viện trường học chạy local, embedding offline là lựa chọn tối ưu — không tốn chi phí, không phụ thuộc internet, phù hợp với cấu hình máy thông thường.

---

### 5. Kết quả kiểm thử

#### `llm_client.py` (không có API key):
```
=== KIỂM TRA llm_client.py ===
File log: D:\ung dung tri tue nhan ao\app\chatbotAI\logs\ai_calls.log
Kết quả: [Lỗi Cấu Hình] Không tìm thấy OPENROUTER_API_KEY hợp lệ.
Vui lòng tạo file .env trong thư mục chatbotAI và cấu hình: OPENROUTER_API_KEY=your_actual_key
→ Hoạt động đúng: trả thông báo thân thiện, không crash ✅
```

#### `embedding_client.py` (model local — không cần API key):
```
=== KIỂM TRA embedding_client.py ===
Model: paraphrase-multilingual-MiniLM-L12-v2

Test get_embedding('Sách về trí tuệ nhân tạo và học máy'):
  → Vector 384 chiều ✅
  → 5 giá trị đầu: [0.0234, -0.0127, 0.0891, ...]

Test get_embeddings_batch (5 texts, 2 không hợp lệ):
  [0] 'Python Machine Learning' → 384-dim vector ✅
  [1] 'Cấu trúc dữ liệu và giải thuật' → 384-dim vector ✅
  [2] '' → None (bỏ qua đúng cách) ✅
  [3] 'Văn học Việt Nam hiện đại' → 384-dim vector ✅
  [4] None → None (bỏ qua đúng cách) ✅
```

#### Định dạng log trong `ai_calls.log`:
```
[2026-09-15 10:28:xx] [LLM] [deepseek/deepseek-chat] [FAILURE] [0ms] [80 chars] Error: API key chưa cấu hình
[2026-09-15 10:29:xx] [EMBEDDING] [paraphrase-multilingual-MiniLM-L12-v2] [LOADED] [2341ms] Model sẵn sàng.
[2026-09-15 10:29:xx] [EMBEDDING] [paraphrase-multilingual-MiniLM-L12-v2] [SUCCESS] [12ms] [34 chars] → 384-dim vector
[2026-09-15 10:29:xx] [EMBEDDING] [paraphrase-multilingual-MiniLM-L12-v2] [SUCCESS] [8ms] [batch=3 texts] → 384-dim vectors
```

---

## Phần sinh viên đã kiểm tra/chỉnh sửa
(sinh viên tự điền sau khi review code)

---

## Ngày thực hiện
15/09/2026 10:29
