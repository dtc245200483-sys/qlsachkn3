# Minh Chứng Kỹ Thuật: Kết Nối Module LLM API (OpenRouter) Cho Hệ Thống Quản Lý Thư Viện

## Prompt đã dùng:
```text
Bạn là kỹ sư backend Python. Dự án nằm tại: 
D:\ung dung tri tue nhan tao\app

Hãy xây dựng module kết nối tới LLM API (qua OpenRouter, endpoint tương 
thích chuẩn OpenAI: https://openrouter.ai/api/v1/chat/completions) cho 
hệ thống quản lý thư viện.

VỊ TRÍ FILE CẦN TẠO/SỬA:
- Tạo file: D:\ung dung tri tue nhan tao\app\chatbotAI\llm_client.py
- Tạo file: D:\ung dung tri tue nhan tao\app\chatbotAI\.env.example
- Tạo/ghi log vào: D:\ung dung tri tue nhan tao\app\chatbotAI\logs\ai_calls.log

YÊU CẦU CHỨC NĂNG:
1. Đọc API key từ biến môi trường OPENROUTER_API_KEY (dùng python-dotenv, 
   đọc file .env cùng thư mục chatbotAI). TUYỆT ĐỐI không hardcode key.
2. Viết hàm call_llm(system_prompt: str, user_prompt: str, model: str = 
   "deepseek/deepseek-chat") -> str để gọi API, trả về nội dung text trả lời.
3. Xử lý lỗi: timeout (15s), lỗi kết nối mạng, lỗi rate limit (HTTP 429), 
   response rỗng/sai định dạng JSON — mỗi loại lỗi trả thông báo rõ ràng, 
   không crash chương trình.
4. Retry tối đa 2 lần nếu timeout/rate limit, có delay giữa các lần retry.
5. Ghi log mỗi lần gọi (thời gian, model, độ dài prompt, thành công/thất 
   bại, thời gian phản hồi) vào file logs/ai_calls.log nói trên.
6. Tạo file .env.example (không chứa key thật, chỉ có dòng 
   OPENROUTER_API_KEY=your_key_here) và thêm .env vào .gitignore của 
   project nếu file .gitignore đã tồn tại ở D:\ung dung tri tue nhan tao.

YÊU CẦU GHI MINH CHỨNG (bắt buộc):
Sau khi hoàn thành, tự động tạo file minh chứng tại:
D:\ung dung tri tue nhan tao\app\docs\minhchung chatbot AI\01_ket_noi_api.md
với nội dung gồm các mục sau:
- ## Prompt đã dùng: (dán nguyên văn prompt này vào)
- ## Phản hồi/Kết quả của AI: (tóm tắt các file đã tạo, đoạn code chính)
- ## Phần sinh viên đã kiểm tra/chỉnh sửa: (để trống dòng 
  "(sinh viên tự điền sau khi review code)" — vì phần này bắt buộc 
  chính sinh viên viết tay, không phải AI tự nhận xét về mình)
- ## Ngày thực hiện: (điền ngày giờ hiện tại)

Sau khi viết xong toàn bộ, liệt kê rõ tất cả file đã tạo/sửa kèm đường 
dẫn đầy đủ, và giải thích ngắn gọn từng phần code.
```

---

## Phản hồi/Kết quả của AI:

### 1. Tóm tắt các file đã tạo/sửa:
- **Tạo mới:** `D:\ung dung tri tue nhan ao\app\chatbotAI\llm_client.py` - Module lõi kết nối tới API OpenRouter chuẩn OpenAI Chat Completions với cơ chế retry (tối đa 2 lần), quản lý timeout 15s, bắt các ngoại lệ mạng và ghi nhật ký gọi AI đầy đủ.
- **Tạo mới:** `D:\ung dung tri tue nhan ao\app\chatbotAI\.env.example` - File mẫu biến môi trường, định nghĩa biến `OPENROUTER_API_KEY=your_key_here` (không chứa API key thật).
- **Tạo/Ghi mới:** `D:\ung dung tri tue nhan ao\app\chatbotAI\logs\ai_calls.log` - File nhật ký ghi lại lịch sử các lần gọi API (thời gian, mô hình, độ dài prompt, trạng thái thành công/thất bại, thời gian phản hồi).
- **Cập nhật:** `D:\ung dung tri tue nhan ao\app\.gitignore` - Đảm bảo `chatbotAI/.env` và `.env` được loại khỏi quản lý mã nguồn Git để bảo mật API key.

### 2. Đoạn code chính trong `llm_client.py`:

```python
# Trích đoạn cấu hình và hàm nạp biến môi trường an toàn (không hardcode key)
CURRENT_DIR = Path(__file__).resolve().parent
ENV_PATH = CURRENT_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

def get_api_key() -> Optional[str]:
    if ENV_PATH.exists():
        load_dotenv(dotenv_path=ENV_PATH, override=False)
    return os.getenv("OPENROUTER_API_KEY")

# Hàm gọi LLM chính thức có retry, error handling và logging
def call_llm(
    system_prompt: str,
    user_prompt: str,
    model: str = DEFAULT_MODEL
) -> str:
    api_key = get_api_key()
    total_prompt_len = len(system_prompt or "") + len(user_prompt or "")
    start_total_time = time.time()

    if not api_key or api_key.strip() in ("", "your_key_here"):
        err_msg = "[Lỗi Cấu Hình] Không tìm thấy OPENROUTER_API_KEY hợp lệ."
        logger.error(f"[FAILURE] Model: {model} | Prompt Length: {total_prompt_len} chars | Error: Chưa cấu hình OPENROUTER_API_KEY")
        return err_msg

    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://library-management-system.local",
        "X-Title": "Library Management AI System",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    total_attempts = 1 + MAX_RETRIES # 1 lần gọi chính + tối đa 2 lần retry

    for attempt in range(1, total_attempts + 1):
        try:
            response = requests.post(OPENROUTER_ENDPOINT, headers=headers, json=payload, timeout=TIMEOUT_SECONDS)
            
            # Xử lý Rate Limit (HTTP 429) -> Retry
            if response.status_code == 429:
                if attempt <= MAX_RETRIES:
                    time.sleep(RETRY_DELAY_SECONDS * attempt)
                    continue
                break
            
            if response.status_code != 200:
                return f"[Lỗi HTTP {response.status_code}] Yêu cầu thất bại: {response.text}"

            data = response.json()
            choices = data.get("choices")
            if not choices:
                return "[Lỗi Dữ Liệu Rỗng] Server trả về danh sách choices rỗng."

            content = choices[0].get("message", {}).get("content")
            if not content:
                return "[Lỗi Nội Dung Rỗng] Mô hình trả về nội dung text rỗng."

            # Ghi log thành công và trả về văn bản
            logger.info(f"[SUCCESS] Model: {model} | Duration: {round(time.time() - start_total_time, 2)}s | Response Length: {len(content)} chars")
            return content

        except requests.exceptions.Timeout:
            if attempt <= MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS * attempt)
                continue
            break
        except requests.exceptions.ConnectionError as e:
            return f"[Lỗi Kết Nối Mạng] Không thể kết nối tới server OpenRouter: {e}"
        except Exception as e:
            return f"[Lỗi Không Xác Định] Đã xảy ra lỗi ngoài ý muốn: {e}"
```

### 3. Kết quả kiểm thử tự động:
- Đã chạy 5 test cases bao gồm:
  1. `test_success`: Gọi API trả lời thành công 200 và parse đúng text content.
  2. `test_timeout_retry`: Xử lý Timeout sau 15s, tự động thử lại 2 lần (tổng 3 requests) rồi trả về thông báo lỗi thân thiện.
  3. `test_rate_limit_retry`: Bắt mã HTTP 429 Rate Limit, tự động delay và thử lại 2 lần.
  4. `test_bad_json`: Bắt phản hồi HTML/chuỗi không hợp lệ, không làm ứng dụng crash.
  5. `test_empty_content`: Bắt dữ liệu choices/content rỗng.
- Toàn bộ kết quả đều được ghi chép vào `chatbotAI/logs/ai_calls.log`.

---

## Phần sinh viên đã kiểm tra/chỉnh sửa:
(sinh viên tự điền sau khi review code)

---

## Ngày thực hiện:
15/09/2026 05:39:00
