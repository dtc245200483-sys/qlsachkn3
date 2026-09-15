"""
llm_client.py — Module kết nối tới LLM API qua OpenRouter (OpenAI-compatible).
Dành cho hệ thống quản lý thư viện — kiến trúc RAG.

Thay đổi so với phiên bản cũ:
  - Custom exception classes: LLMTimeoutError, LLMRateLimitError, LLMResponseError
  - Exponential backoff: lần 1 chờ 2s, lần 2 chờ 4s
  - Định dạng log mới: [time] [LLM] [model] [status] [Xms] [input_len chars]
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

# Đảm bảo hiển thị tiếng Việt trên Windows console
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

# ─── Nạp biến môi trường ────────────────────────────────────────────────────
CURRENT_DIR = Path(__file__).resolve().parent
ENV_PATH = CURRENT_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# ─── Cấu hình logging dùng chung (logs/ai_calls.log) ────────────────────────
LOGS_DIR = CURRENT_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / "ai_calls.log"

_logger = logging.getLogger("ai_calls")
_logger.setLevel(logging.INFO)
if not _logger.handlers:
    _fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    _fh.setFormatter(logging.Formatter(
        "[%(asctime)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    _logger.addHandler(_fh)

# ─── Hằng số ─────────────────────────────────────────────────────────────────
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "deepseek/deepseek-chat"
TIMEOUT_SECONDS = 15
MAX_RETRIES = 2
BACKOFF_BASE = 2  # Giây: lần 1 chờ 2s, lần 2 chờ 4s (exponential)


# ═════════════════════════════════════════════════════════════════════════════
# Custom Exception Classes
# ═════════════════════════════════════════════════════════════════════════════

class LLMError(Exception):
    """Base class cho mọi lỗi liên quan đến LLM client."""
    pass


class LLMTimeoutError(LLMError):
    """Raise khi request tới LLM API vượt quá timeout sau tất cả các lần retry."""
    pass


class LLMRateLimitError(LLMError):
    """Raise khi API trả về HTTP 429 (Rate Limit) sau tất cả các lần retry."""
    pass


class LLMResponseError(LLMError):
    """
    Raise khi phản hồi từ LLM không hợp lệ:
    - HTTP != 200 (trừ 429)
    - Response body không phải JSON hợp lệ
    - Thiếu trường 'choices' hoặc 'content' rỗng
    """
    pass


# ═════════════════════════════════════════════════════════════════════════════
# Hàm đọc API key
# ═════════════════════════════════════════════════════════════════════════════

def _get_api_key() -> Optional[str]:
    """Đọc OPENROUTER_API_KEY từ biến môi trường. TUYỆT ĐỐI không hardcode."""
    if ENV_PATH.exists():
        load_dotenv(dotenv_path=ENV_PATH, override=False)
    return os.getenv("OPENROUTER_API_KEY")


# ═════════════════════════════════════════════════════════════════════════════
# Hàm gọi LLM chính
# ═════════════════════════════════════════════════════════════════════════════

def call_llm(
    system_prompt: str,
    user_prompt: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 1500,
) -> str:
    """
    Gọi LLM API qua OpenRouter và trả về nội dung văn bản phản hồi.

    Tham số:
        system_prompt (str): Lời nhắc hệ thống định hình vai trò AI.
        user_prompt (str):   Nội dung câu hỏi/yêu cầu của người dùng.
        model (str):         Tên model (mặc định: 'deepseek/deepseek-chat').
        max_tokens (int):    Số lượng token phản hồi tối đa (mặc định 1500).

    Trả về:
        str: Nội dung text phản hồi từ LLM.

    Raise:
        LLMTimeoutError:    Nếu request timeout sau tất cả retry.
        LLMRateLimitError:  Nếu API trả HTTP 429 sau tất cả retry.
        LLMResponseError:   Nếu phản hồi không hợp lệ (HTTP lỗi, JSON sai, rỗng).
        ValueError:         Nếu API key chưa được cấu hình.
    """
    api_key = _get_api_key()
    total_input_len = len(system_prompt or "") + len(user_prompt or "")
    start_time = time.time()

    # Kiểm tra API key
    if not api_key or api_key.strip() in ("", "your_key_here"):
        msg = (
            "[Lỗi Cấu Hình] Không tìm thấy OPENROUTER_API_KEY hợp lệ. "
            "Vui lòng tạo file .env trong thư mục chatbotAI và cấu hình: "
            "OPENROUTER_API_KEY=your_actual_key"
        )
        elapsed_ms = int((time.time() - start_time) * 1000)
        _logger.error(
            f"[LLM] [{model}] [FAILURE] [{elapsed_ms}ms] [{total_input_len} chars] "
            f"Error: API key chưa cấu hình"
        )
        return msg  # Trả về thông báo thân thiện thay vì raise để không crash UI

    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://library-management-system.local",
        "X-Title": "Library Management AI System",
    }
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    last_exception: Optional[Exception] = None
    total_attempts = 1 + MAX_RETRIES  # 3 lần tổng cộng

    for attempt in range(1, total_attempts + 1):
        attempt_start = time.time()
        try:
            response = requests.post(
                OPENROUTER_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=TIMEOUT_SECONDS,
            )
            attempt_ms = int((time.time() - attempt_start) * 1000)

            # ── HTTP 429: Rate Limit → Retry với exponential backoff ──────────
            if response.status_code == 429:
                backoff = BACKOFF_BASE ** attempt  # 2s, 4s
                _logger.warning(
                    f"[LLM] [{model}] [RETRY {attempt}/{total_attempts}] "
                    f"[{attempt_ms}ms] [{total_input_len} chars] "
                    f"HTTP 429 — chờ {backoff}s"
                )
                last_exception = LLMRateLimitError(
                    f"API Rate Limit (HTTP 429) ở lần thử {attempt}/{total_attempts}. "
                    f"Thử lại sau {backoff}s."
                )
                if attempt < total_attempts:
                    time.sleep(backoff)
                    continue
                break  # Hết retry

            # ── HTTP != 200 (không phải 429) → Lỗi nghiêm trọng, không retry ─
            if response.status_code != 200:
                error_detail = response.text
                try:
                    err_json = response.json()
                    error_detail = err_json.get("error", {}).get("message", response.text)
                except Exception:
                    pass
                elapsed_ms = int((time.time() - start_time) * 1000)
                _logger.error(
                    f"[LLM] [{model}] [FAILURE] [{elapsed_ms}ms] [{total_input_len} chars] "
                    f"HTTP {response.status_code}: {error_detail[:100]}"
                )
                raise LLMResponseError(
                    f"HTTP {response.status_code}: {error_detail}"
                )

            # ── Parse JSON ────────────────────────────────────────────────────
            try:
                data = response.json()
            except (json.JSONDecodeError, ValueError) as e:
                elapsed_ms = int((time.time() - start_time) * 1000)
                _logger.error(
                    f"[LLM] [{model}] [FAILURE] [{elapsed_ms}ms] [{total_input_len} chars] "
                    f"JSON parse error: {response.text[:100]}"
                )
                raise LLMResponseError(
                    f"Phản hồi từ server không phải JSON hợp lệ: {e}"
                ) from e

            # ── Kiểm tra cấu trúc choices ─────────────────────────────────────
            choices = data.get("choices")
            if not choices or not isinstance(choices, list):
                elapsed_ms = int((time.time() - start_time) * 1000)
                _logger.error(
                    f"[LLM] [{model}] [FAILURE] [{elapsed_ms}ms] [{total_input_len} chars] "
                    f"Empty choices"
                )
                raise LLMResponseError("Server trả về danh sách 'choices' rỗng.")

            content = choices[0].get("message", {}).get("content")
            if content is None or (isinstance(content, str) and content.strip() == ""):
                elapsed_ms = int((time.time() - start_time) * 1000)
                _logger.error(
                    f"[LLM] [{model}] [FAILURE] [{elapsed_ms}ms] [{total_input_len} chars] "
                    f"Empty content"
                )
                raise LLMResponseError("Mô hình trả về nội dung text rỗng.")

            # ── Thành công ────────────────────────────────────────────────────
            elapsed_ms = int((time.time() - start_time) * 1000)
            _logger.info(
                f"[LLM] [{model}] [SUCCESS] [{elapsed_ms}ms] [{total_input_len} chars] "
                f"Response: {len(content)} chars"
            )
            return content

        except (LLMResponseError, LLMRateLimitError):
            raise  # Re-raise ngay, không retry với lỗi response

        except requests.exceptions.Timeout:
            attempt_ms = int((time.time() - attempt_start) * 1000)
            backoff = BACKOFF_BASE ** attempt  # 2s, 4s
            _logger.warning(
                f"[LLM] [{model}] [RETRY {attempt}/{total_attempts}] "
                f"[{attempt_ms}ms] [{total_input_len} chars] "
                f"Timeout ({TIMEOUT_SECONDS}s) — chờ {backoff}s"
            )
            last_exception = LLMTimeoutError(
                f"Request timeout ({TIMEOUT_SECONDS}s) ở lần thử {attempt}/{total_attempts}."
            )
            if attempt < total_attempts:
                time.sleep(backoff)
                continue
            break

        except requests.exceptions.ConnectionError as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            _logger.error(
                f"[LLM] [{model}] [FAILURE] [{elapsed_ms}ms] [{total_input_len} chars] "
                f"ConnectionError: {str(e)[:80]}"
            )
            raise LLMResponseError(
                f"Không thể kết nối tới server OpenRouter: {e}"
            ) from e

        except requests.exceptions.RequestException as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            _logger.error(
                f"[LLM] [{model}] [FAILURE] [{elapsed_ms}ms] [{total_input_len} chars] "
                f"RequestException: {str(e)[:80]}"
            )
            raise LLMResponseError(f"Lỗi request tới LLM API: {e}") from e

    # Hết tất cả retry → raise exception cuối cùng
    elapsed_ms = int((time.time() - start_time) * 1000)
    _logger.error(
        f"[LLM] [{model}] [FAILURE] [{elapsed_ms}ms] [{total_input_len} chars] "
        f"Exceeded max retries: {last_exception}"
    )
    if isinstance(last_exception, LLMTimeoutError):
        raise LLMTimeoutError(
            f"Timeout sau {MAX_RETRIES} lần retry. "
            f"Vui lòng kiểm tra kết nối mạng."
        ) from last_exception
    raise LLMRateLimitError(
        f"API Rate Limit sau {MAX_RETRIES} lần retry. "
        f"Vui lòng thử lại sau."
    ) from last_exception


# ═════════════════════════════════════════════════════════════════════════════
# Chạy thử khi gọi trực tiếp file này
# ═════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=== KIỂM TRA llm_client.py ===")
    print(f"File log: {LOG_FILE}")
    try:
        result = call_llm(
            system_prompt="Bạn là trợ lý thư viện ngắn gọn.",
            user_prompt="Giới thiệu 1 cuốn sách về Python trong 1 câu.",
        )
        print(f"Kết quả: {result}")
    except LLMTimeoutError as e:
        print(f"[Timeout] {e}")
    except LLMRateLimitError as e:
        print(f"[Rate Limit] {e}")
    except LLMResponseError as e:
        print(f"[Response Error] {e}")
    except Exception as e:
        print(f"[Lỗi khác] {e}")
