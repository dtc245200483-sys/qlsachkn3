"""
Module kết nối tới LLM API qua OpenRouter (endpoint tương thích chuẩn OpenAI)
Dành cho hệ thống quản lý thư viện.
"""

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import requests

# Đảm bảo stdout/stderr hiển thị tiếng Việt trên Windows console không bị lỗi cp1252
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 1. Nạp biến môi trường từ file .env trong cùng thư mục chatbotAI
CURRENT_DIR = Path(__file__).resolve().parent
ENV_PATH = CURRENT_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Cấu hình đường dẫn thư mục logs và file ai_calls.log
LOGS_DIR = CURRENT_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / "ai_calls.log"

# Cấu hình logging
logger = logging.getLogger("ai_calls")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# Các hằng số cấu hình
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "deepseek/deepseek-chat"
TIMEOUT_SECONDS = 15
MAX_RETRIES = 2
RETRY_DELAY_SECONDS = 2  # Thời gian chờ (giây) trước mỗi lần retry


def get_api_key() -> Optional[str]:
    """
    Đọc API key từ biến môi trường OPENROUTER_API_KEY.
    Đảm bảo TUYỆT ĐỐI không hardcode API key.
    """
    if ENV_PATH.exists():
        load_dotenv(dotenv_path=ENV_PATH, override=False)
    return os.getenv("OPENROUTER_API_KEY")


def call_llm(
    system_prompt: str,
    user_prompt: str,
    model: str = DEFAULT_MODEL
) -> str:
    """
    Gửi prompt tới LLM API (OpenRouter) và trả về nội dung câu trả lời dạng văn bản.

    Tham số:
        system_prompt (str): Lời nhắc hệ thống định hình vai trò và ngữ cảnh của AI.
        user_prompt (str): Nội dung câu hỏi/yêu cầu từ người dùng.
        model (str): Tên mô hình cần gọi (mặc định là 'deepseek/deepseek-chat').

    Trả về:
        str: Nội dung phản hồi từ LLM hoặc thông báo lỗi chi tiết, không làm crash chương trình.
    """
    api_key = get_api_key()
    total_prompt_len = len(system_prompt or "") + len(user_prompt or "")
    start_total_time = time.time()

    # Kiểm tra tính khả dụng của API key
    if not api_key or api_key.strip() in ("", "your_key_here"):
        duration = round(time.time() - start_total_time, 2)
        err_msg = (
            "[Lỗi Cấu Hình] Không tìm thấy OPENROUTER_API_KEY hợp lệ. "
            "Vui lòng tạo file .env trong thư mục chatbotAI và cấu hình: OPENROUTER_API_KEY=your_actual_key"
        )
        logger.error(
            f"[FAILURE] Model: {model} | Prompt Length: {total_prompt_len} chars | "
            f"Duration: {duration}s | Error: Chưa cấu hình OPENROUTER_API_KEY"
        )
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

    last_error_message = ""
    total_attempts = 1 + MAX_RETRIES

    for attempt in range(1, total_attempts + 1):
        attempt_start_time = time.time()
        try:
            response = requests.post(
                OPENROUTER_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=TIMEOUT_SECONDS,
            )
            attempt_duration = round(time.time() - attempt_start_time, 2)

            # 1. Xử lý lỗi Rate Limit (HTTP 429) -> Có retry
            if response.status_code == 429:
                last_error_message = (
                    f"[Lỗi Rate Limit] API bị giới hạn tần suất gọi (HTTP 429) ở lần thử {attempt}/{total_attempts}."
                )
                logger.warning(
                    f"[RETRY] Attempt {attempt}/{total_attempts} | Model: {model} | "
                    f"Prompt Length: {total_prompt_len} chars | Duration: {attempt_duration}s | HTTP 429 Rate Limit"
                )
                if attempt <= MAX_RETRIES:
                    time.sleep(RETRY_DELAY_SECONDS * attempt)
                    continue
                else:
                    break

            # 2. Xử lý lỗi HTTP khác (401, 403, 500, 502, 503...) -> Không retry nếu lỗi auth/client
            if response.status_code != 200:
                error_body = response.text
                try:
                    err_json = response.json()
                    error_body = err_json.get("error", {}).get("message", response.text)
                except Exception:
                    pass

                last_error_message = f"[Lỗi HTTP {response.status_code}] Yêu cầu thất bại: {error_body}"
                logger.error(
                    f"[FAILURE] Attempt {attempt}/{total_attempts} | Model: {model} | "
                    f"Prompt Length: {total_prompt_len} chars | Duration: {attempt_duration}s | "
                    f"HTTP {response.status_code}: {error_body}"
                )
                return last_error_message

            # 3. Xử lý response không đúng định dạng JSON
            try:
                data = response.json()
            except (json.JSONDecodeError, ValueError) as json_err:
                last_error_message = f"[Lỗi Định Dạng JSON] Phản hồi từ server không phải JSON hợp lệ: {str(json_err)}"
                logger.error(
                    f"[FAILURE] Model: {model} | Prompt Length: {total_prompt_len} chars | "
                    f"Duration: {attempt_duration}s | Invalid JSON: {response.text[:200]}"
                )
                return last_error_message

            # 4. Xử lý response rỗng / thiếu trường choices
            choices = data.get("choices")
            if not choices or not isinstance(choices, list) or len(choices) == 0:
                last_error_message = "[Lỗi Dữ Liệu Rỗng] Server trả về danh sách 'choices' rỗng."
                logger.error(
                    f"[FAILURE] Model: {model} | Prompt Length: {total_prompt_len} chars | "
                    f"Duration: {attempt_duration}s | Empty choices in response"
                )
                return last_error_message

            message_obj = choices[0].get("message", {})
            content = message_obj.get("content")

            if content is None or (isinstance(content, str) and content.strip() == ""):
                last_error_message = "[Lỗi Nội Dung Rỗng] Mô hình trả về nội dung text rỗng."
                logger.error(
                    f"[FAILURE] Model: {model} | Prompt Length: {total_prompt_len} chars | "
                    f"Duration: {attempt_duration}s | Empty content"
                )
                return last_error_message

            # Thành công: Ghi log thành công và trả kết quả
            total_duration = round(time.time() - start_total_time, 2)
            response_len = len(content)
            logger.info(
                f"[SUCCESS] Model: {model} | Prompt Length: {total_prompt_len} chars | "
                f"Duration: {total_duration}s | Response Length: {response_len} chars"
            )
            return content

        except requests.exceptions.Timeout:
            attempt_duration = round(time.time() - attempt_start_time, 2)
            last_error_message = (
                f"[Lỗi Timeout] Yêu cầu tới LLM quá thời gian chờ ({TIMEOUT_SECONDS}s) "
                f"ở lần thử {attempt}/{total_attempts}."
            )
            logger.warning(
                f"[RETRY] Attempt {attempt}/{total_attempts} | Model: {model} | "
                f"Prompt Length: {total_prompt_len} chars | Duration: {attempt_duration}s | Timeout ({TIMEOUT_SECONDS}s)"
            )
            if attempt <= MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS * attempt)
                continue
            else:
                break

        except requests.exceptions.ConnectionError as conn_err:
            attempt_duration = round(time.time() - attempt_start_time, 2)
            last_error_message = f"[Lỗi Kết Nối Mạng] Không thể kết nối tới server OpenRouter: {str(conn_err)}"
            logger.error(
                f"[FAILURE] Model: {model} | Prompt Length: {total_prompt_len} chars | "
                f"Duration: {attempt_duration}s | ConnectionError: {str(conn_err)}"
            )
            return last_error_message

        except requests.exceptions.RequestException as req_err:
            attempt_duration = round(time.time() - attempt_start_time, 2)
            last_error_message = f"[Lỗi Yêu Cầu] Lỗi trong quá trình gửi request tới LLM API: {str(req_err)}"
            logger.error(
                f"[FAILURE] Model: {model} | Prompt Length: {total_prompt_len} chars | "
                f"Duration: {attempt_duration}s | RequestException: {str(req_err)}"
            )
            return last_error_message

        except Exception as unexpected_err:
            attempt_duration = round(time.time() - attempt_start_time, 2)
            last_error_message = f"[Lỗi Không Xác Định] Đã xảy ra lỗi ngoài ý muốn: {str(unexpected_err)}"
            logger.error(
                f"[FAILURE] Model: {model} | Prompt Length: {total_prompt_len} chars | "
                f"Duration: {attempt_duration}s | Unexpected Exception: {str(unexpected_err)}"
            )
            return last_error_message

    # Nếu thoát khỏi vòng lặp do hết lượt retry (Timeout hoặc HTTP 429)
    total_duration = round(time.time() - start_total_time, 2)
    final_error = f"{last_error_message} (Đã thử lại tối đa {MAX_RETRIES} lần nhưng không thành công)."
    logger.error(
        f"[FAILURE] Model: {model} | Prompt Length: {total_prompt_len} chars | "
        f"Duration: {total_duration}s | Exceeded max retries | Last error: {last_error_message}"
    )
    return final_error


if __name__ == "__main__":
    print("=== KIỂM TRA MODULE LLM_CLIENT ===")
    print(f"File log: {LOG_FILE}")
    test_sys = "Bạn là thủ thư AI tư vấn sách thân thiện."
    test_user = "Giới thiệu cho tôi một cuốn sách hay về lập trình Python."
    result = call_llm(test_sys, test_user)
    print("Kết quả gọi call_llm:")
    print(result)
