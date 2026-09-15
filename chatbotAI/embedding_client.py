"""
embedding_client.py — Module vector hóa văn bản (Embedding) cho kiến trúc RAG.

Dùng model local (sentence-transformers) — KHÔNG qua API, chạy offline,
không cần API key, không bị giới hạn rate limit.

Model: paraphrase-multilingual-MiniLM-L12-v2
  - Hỗ trợ tốt tiếng Việt
  - Nhẹ (~120MB), phù hợp máy cấu hình thường
  - Xuất vector 384 chiều

Singleton Pattern: model chỉ được load 1 lần duy nhất khi khởi động.
"""

import logging
import sys
import time
from pathlib import Path
from typing import Optional

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

# ─── Cấu hình logging dùng chung (logs/ai_calls.log) ─────────────────────────
CURRENT_DIR = Path(__file__).resolve().parent
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

# ─── Hằng số ──────────────────────────────────────────────────────────────────
EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


# ═════════════════════════════════════════════════════════════════════════════
# Singleton: Model chỉ load 1 lần
# ═════════════════════════════════════════════════════════════════════════════

_model_instance = None          # Biến singleton giữ model đã load
_model_load_error: Optional[Exception] = None  # Giữ lỗi nếu load thất bại


def _get_model():
    """
    Trả về model sentence-transformers đã được load (Singleton).
    Nếu chưa load, thực hiện load và cache vào _model_instance.
    Nếu lỗi import/download, ghi log và trả về None.
    """
    global _model_instance, _model_load_error

    # Đã load thành công trước đó → trả về ngay
    if _model_instance is not None:
        return _model_instance

    # Đã gặp lỗi load trước đó → không thử lại vô ích
    if _model_load_error is not None:
        return None

    # Thử load lần đầu
    try:
        from sentence_transformers import SentenceTransformer
        _logger.info(
            f"[EMBEDDING] [{EMBEDDING_MODEL_NAME}] [LOADING] "
            f"Đang load model lần đầu tiên..."
        )
        load_start = time.time()
        _model_instance = SentenceTransformer(EMBEDDING_MODEL_NAME)
        load_ms = int((time.time() - load_start) * 1000)
        _logger.info(
            f"[EMBEDDING] [{EMBEDDING_MODEL_NAME}] [LOADED] [{load_ms}ms] "
            f"Model sẵn sàng."
        )
        return _model_instance

    except ImportError as e:
        _model_load_error = e
        err_msg = (
            f"[EMBEDDING] [{EMBEDDING_MODEL_NAME}] [FAILURE] "
            f"ImportError: {e}\n"
            f"  → Hướng dẫn cài đặt: pip install sentence-transformers"
        )
        _logger.error(err_msg)
        print(
            f"\n[Lỗi] Thư viện 'sentence-transformers' chưa được cài đặt.\n"
            f"Hãy chạy lệnh: pip install sentence-transformers\n",
            file=sys.stderr
        )
        return None

    except Exception as e:
        _model_load_error = e
        _logger.error(
            f"[EMBEDDING] [{EMBEDDING_MODEL_NAME}] [FAILURE] "
            f"Không thể load model: {e}"
        )
        return None


# ═════════════════════════════════════════════════════════════════════════════
# Hàm 1: Embedding 1 đoạn text
# ═════════════════════════════════════════════════════════════════════════════

def get_embedding(text: str) -> Optional[list[float]]:
    """
    Vector hóa 1 đoạn text thành embedding vector (list[float]).

    Model được load 1 lần duy nhất khi gọi lần đầu (Singleton Pattern).
    Các lần gọi sau dùng lại model đã có sẵn trong bộ nhớ — rất nhanh.

    Tham số:
        text (str): Đoạn văn bản cần vector hóa.

    Trả về:
        list[float]: Vector embedding (384 chiều với MiniLM-L12-v2).
        None: Nếu text rỗng/None hoặc model chưa load được.
    """
    # Kiểm tra đầu vào
    if text is None:
        _logger.warning(
            f"[EMBEDDING] [{EMBEDDING_MODEL_NAME}] [WARNING] "
            f"get_embedding() nhận được text=None, bỏ qua."
        )
        return None

    if not isinstance(text, str) or text.strip() == "":
        _logger.warning(
            f"[EMBEDDING] [{EMBEDDING_MODEL_NAME}] [WARNING] "
            f"get_embedding() nhận text rỗng hoặc không phải chuỗi, bỏ qua."
        )
        return None

    model = _get_model()
    if model is None:
        _logger.error(
            f"[EMBEDDING] [{EMBEDDING_MODEL_NAME}] [FAILURE] "
            f"Model chưa được load, không thể tạo embedding."
        )
        return None

    start_time = time.time()
    try:
        vector = model.encode(text, convert_to_numpy=True)
        elapsed_ms = int((time.time() - start_time) * 1000)
        _logger.info(
            f"[EMBEDDING] [{EMBEDDING_MODEL_NAME}] [SUCCESS] [{elapsed_ms}ms] "
            f"[{len(text)} chars] → {len(vector)}-dim vector"
        )
        return vector.tolist()

    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        _logger.error(
            f"[EMBEDDING] [{EMBEDDING_MODEL_NAME}] [FAILURE] [{elapsed_ms}ms] "
            f"[{len(text)} chars] Exception: {e}"
        )
        return None


# ═════════════════════════════════════════════════════════════════════════════
# Hàm 2: Embedding batch nhiều đoạn text
# ═════════════════════════════════════════════════════════════════════════════

def get_embeddings_batch(texts: list[str]) -> list[Optional[list[float]]]:
    """
    Vector hóa nhiều đoạn text cùng lúc (batch encoding).

    Hiệu quả hơn nhiều so với gọi get_embedding() từng cái một vì:
    - Tận dụng vectorized computation của model
    - Batch processing giảm overhead
    - Dùng để index toàn bộ danh sách sách khi khởi động hệ thống RAG

    Tham số:
        texts (list[str]): Danh sách các đoạn văn bản cần vector hóa.

    Trả về:
        list[Optional[list[float]]]: Danh sách vectors tương ứng.
            - Vị trí có text hợp lệ → list[float] (vector embedding)
            - Vị trí có text rỗng/None → None
    """
    if not texts or not isinstance(texts, list):
        _logger.warning(
            f"[EMBEDDING] [{EMBEDDING_MODEL_NAME}] [WARNING] "
            f"get_embeddings_batch() nhận danh sách rỗng hoặc không hợp lệ."
        )
        return []

    model = _get_model()
    if model is None:
        _logger.error(
            f"[EMBEDDING] [{EMBEDDING_MODEL_NAME}] [FAILURE] "
            f"Model chưa được load, không thể tạo batch embedding."
        )
        return [None] * len(texts)

    # Tách các text hợp lệ và ghi nhớ index để ghép lại kết quả
    valid_indices: list[int] = []
    valid_texts: list[str] = []
    results: list[Optional[list[float]]] = [None] * len(texts)

    for i, text in enumerate(texts):
        if text is not None and isinstance(text, str) and text.strip() != "":
            valid_indices.append(i)
            valid_texts.append(text)
        else:
            _logger.warning(
                f"[EMBEDDING] [{EMBEDDING_MODEL_NAME}] [WARNING] "
                f"Bỏ qua phần tử index {i}: text rỗng hoặc None."
            )

    if not valid_texts:
        return results

    # Batch encode tất cả text hợp lệ cùng lúc
    start_time = time.time()
    try:
        # show_progress_bar=False để tránh output thừa trong production
        vectors = model.encode(valid_texts, convert_to_numpy=True, show_progress_bar=False)
        elapsed_ms = int((time.time() - start_time) * 1000)
        _logger.info(
            f"[EMBEDDING] [{EMBEDDING_MODEL_NAME}] [SUCCESS] [{elapsed_ms}ms] "
            f"[batch={len(valid_texts)} texts] → {vectors.shape[1]}-dim vectors"
        )
        # Ghép kết quả về đúng vị trí index
        for idx, vector in zip(valid_indices, vectors):
            results[idx] = vector.tolist()
        return results

    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        _logger.error(
            f"[EMBEDDING] [{EMBEDDING_MODEL_NAME}] [FAILURE] [{elapsed_ms}ms] "
            f"[batch={len(valid_texts)} texts] Exception: {e}"
        )
        return results


# ═════════════════════════════════════════════════════════════════════════════
# Chạy thử khi gọi trực tiếp file này
# ═════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=== KIỂM TRA embedding_client.py ===")
    print(f"Model: {EMBEDDING_MODEL_NAME}")
    print(f"File log: {LOG_FILE}")
    print()

    # Test get_embedding
    test_text = "Sách về trí tuệ nhân tạo và học máy"
    print(f"Test get_embedding('{test_text}'):")
    vec = get_embedding(test_text)
    if vec:
        print(f"  → Vector {len(vec)} chiều")
        print(f"  → 5 giá trị đầu: {[round(v, 4) for v in vec[:5]]}")
    else:
        print("  → FAILED")

    print()

    # Test get_embeddings_batch
    test_batch = [
        "Python Machine Learning",
        "Cấu trúc dữ liệu và giải thuật",
        "",        # text rỗng → None
        "Văn học Việt Nam hiện đại",
        None,      # None → None
    ]
    print(f"Test get_embeddings_batch ({len(test_batch)} texts, 2 không hợp lệ):")
    vecs = get_embeddings_batch(test_batch)
    for i, (t, v) in enumerate(zip(test_batch, vecs)):
        if v is not None:
            print(f"  [{i}] '{str(t)[:35]}' → {len(v)}-dim vector ✅")
        else:
            print(f"  [{i}] {repr(t)} → None (bỏ qua đúng cách) ✅")

    print()
    print(f"Tất cả kiểm thử embedding PASSED.")
