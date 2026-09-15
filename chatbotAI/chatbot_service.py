"""
chatbot_service.py — Hàm tổng hợp toàn bộ luồng RAG tra cứu sách.

Luồng chính:
  1. truy_xuat_context()   → Retrieval (embedding + fuzzy)
  2. xay_dung_user_prompt()→ Ghép prompt
  3. Đọc system_prompt.txt
  4. call_llm()            → Gọi LLM sinh câu trả lời
  5. Parse + Validate JSON → Kiểm soát bịa dữ liệu
  6. Trả về kết quả sạch

Lớp bảo vệ chống hallucination:
  Dù system prompt đã ràng buộc LLM, bước 7 vẫn đối chiếu tên sách
  trong kết quả LLM với context ban đầu — loại bỏ mọi sách LLM tự bịa.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Optional

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

# Thêm thư mục app gốc vào sys.path
APP_ROOT = Path(__file__).resolve().parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from chatbotAI.rag_retriever import truy_xuat_context    # noqa: E402
from chatbotAI.prompt_builder import xay_dung_user_prompt # noqa: E402
from chatbotAI.llm_client import call_llm                 # noqa: E402

_logger = logging.getLogger("ai_calls")

SYSTEM_PROMPT_FILE = Path(__file__).resolve().parent / "prompts" / "system_prompt.txt"


# ─────────────────────────────────────────────────────────────────────────────
# Hàm đọc system prompt
# ─────────────────────────────────────────────────────────────────────────────

def _doc_system_prompt() -> str:
    if not SYSTEM_PROMPT_FILE.exists():
        raise FileNotFoundError(
            f"Không tìm thấy system prompt tại: {SYSTEM_PROMPT_FILE}"
        )
    return SYSTEM_PROMPT_FILE.read_text(encoding="utf-8").strip()


# ─────────────────────────────────────────────────────────────────────────────
# Hàm parse + validate JSON từ LLM
# ─────────────────────────────────────────────────────────────────────────────

def _parse_json_llm(phan_hoi: str) -> Optional[dict]:
    """Trích xuất JSON hợp lệ từ phản hồi LLM (phòng khi LLM thêm text thừa)."""
    noi_dung = phan_hoi.strip()
    # Tìm khối {} đầu tiên và cuối cùng
    bat_dau = noi_dung.find("{")
    ket_thuc = noi_dung.rfind("}") + 1
    if bat_dau != -1 and ket_thuc > bat_dau:
        noi_dung = noi_dung[bat_dau:ket_thuc]
    try:
        data = json.loads(noi_dung)
        # Validate schema tối thiểu
        if "ket_qua" not in data:
            return None
        if not isinstance(data["ket_qua"], list):
            return None
        return data
    except (json.JSONDecodeError, ValueError):
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Lớp kiểm soát chống bịa — Phần 4 Mục 7
# ─────────────────────────────────────────────────────────────────────────────

def _loc_ket_qua_bija(ket_qua_llm: list[dict], context: list[dict]) -> list[dict]:
    """
    Đối chiếu tên sách LLM trả về với context ban đầu.
    Loại bỏ mọi sách mà LLM tự bịa (không có trong context).

    Kiểm tra theo ten_sach (lowercase, strip) — đủ chắc vì LLM thường
    copy nguyên tên từ context mà không thay đổi.
    """
    # Tập hợp tên sách hợp lệ từ context (lowercase để so khớp mềm)
    ten_hop_le = {s["ten_sach"].lower().strip() for s in context if s.get("ten_sach")}
    ket_qua_sach = []

    for item in ket_qua_llm:
        if not isinstance(item, dict):
            continue
        ten = (item.get("ten_sach") or "").lower().strip()
        if ten and ten in ten_hop_le:
            ket_qua_sach.append(item)
        else:
            _logger.warning(
                f"[CHATBOT_SERVICE] ⚠️ AI có dấu hiệu bịa dữ liệu: "
                f"Sách '{item.get('ten_sach', '?')}' không có trong context — đã loại bỏ."
            )

    return ket_qua_sach


# ─────────────────────────────────────────────────────────────────────────────
# Hàm chính: tra_cuu_sach()
# ─────────────────────────────────────────────────────────────────────────────

def tra_cuu_sach(cau_hoi: str) -> dict:
    """
    Luồng RAG tra cứu sách hoàn chỉnh.

    Tham số:
        cau_hoi (str): Câu hỏi của độc giả.

    Trả về:
        dict: {
          "ket_qua": [...],        # danh sách sách gợi ý
          "tong_so_ket_qua": int,
          "thong_bao": str,        # rỗng nếu có kết quả
          "context_so_bo": int,    # số sách retriever tìm được ban đầu
        }
        hoặc {"loi": str} nếu hệ thống gặp sự cố.
    """
    # ── Bước 1: Retrieval ─────────────────────────────────────────────────────
    try:
        context = truy_xuat_context(cau_hoi)
    except Exception as e:
        _logger.error(f"[CHATBOT_SERVICE] Retrieval thất bại: {e}")
        return {"loi": f"Lỗi tìm kiếm: {e}"}

    # ── Bước 2: Không có context → trả về ngay, không cần gọi LLM ────────────
    if not context:
        _logger.info(f"[CHATBOT_SERVICE] '{cau_hoi[:50]}' → context rỗng, bỏ qua LLM")
        return {
            "ket_qua": [],
            "tong_so_ket_qua": 0,
            "thong_bao": "Không tìm thấy sách phù hợp trong thư viện.",
            "context_so_bo": 0,
        }

    # ── Bước 3: Xây dựng user prompt ─────────────────────────────────────────
    try:
        user_prompt = xay_dung_user_prompt(cau_hoi, context)
    except Exception as e:
        return {"loi": f"Lỗi xây dựng prompt: {e}"}

    # ── Bước 4: Đọc system prompt ────────────────────────────────────────────
    try:
        system_prompt = _doc_system_prompt()
    except FileNotFoundError as e:
        return {"loi": f"Lỗi cấu hình: {e}"}

    # ── Bước 5: Gọi LLM ──────────────────────────────────────────────────────
    try:
        phan_hoi_llm = call_llm(system_prompt=system_prompt, user_prompt=user_prompt)
    except Exception as e:
        _logger.error(f"[CHATBOT_SERVICE] Gọi LLM thất bại: {e}")
        return {"loi": f"LLM không phản hồi: {e}"}

    # Nếu call_llm trả về chuỗi lỗi cấu hình (không có API key)
    if isinstance(phan_hoi_llm, str) and phan_hoi_llm.startswith("[Lỗi"):
        return {"loi": phan_hoi_llm}

    # ── Bước 6: Parse JSON — thử lại 1 lần nếu lỗi ──────────────────────────
    ket_qua_dict = _parse_json_llm(phan_hoi_llm)

    if ket_qua_dict is None:
        _logger.warning(
            "[CHATBOT_SERVICE] Parse JSON lần 1 thất bại — thử lại với yêu cầu bổ sung."
        )
        # Thử lại lần 2: yêu cầu LLM output lại đúng JSON
        retry_prompt = (
            f"{user_prompt}\n\n"
            "[QUAN TRỌNG: Phản hồi trước của bạn không phải JSON hợp lệ. "
            "Hãy trả lời LẠI DUY NHẤT một đối tượng JSON theo đúng schema đã quy định, "
            "không kèm bất kỳ văn bản nào khác.]"
        )
        try:
            phan_hoi_llm_2 = call_llm(
                system_prompt=system_prompt,
                user_prompt=retry_prompt,
            )
            ket_qua_dict = _parse_json_llm(phan_hoi_llm_2)
        except Exception:
            ket_qua_dict = None

        if ket_qua_dict is None:
            _logger.error("[CHATBOT_SERVICE] Parse JSON lần 2 vẫn thất bại.")
            return {"loi": "Hệ thống AI gặp sự cố, vui lòng thử lại"}

    # ── Bước 7: Đối chiếu chống bịa dữ liệu ────────────────────────────────
    ket_qua_goc = ket_qua_dict.get("ket_qua", [])
    ket_qua_sach = _loc_ket_qua_bija(ket_qua_goc, context)

    so_bi_loai = len(ket_qua_goc) - len(ket_qua_sach)
    if so_bi_loai > 0:
        _logger.warning(
            f"[CHATBOT_SERVICE] Đã loại bỏ {so_bi_loai} sách LLM bịa "
            f"khỏi kết quả cuối cùng."
        )

    thong_bao = ket_qua_dict.get("thong_bao", "")
    if not ket_qua_sach and not thong_bao:
        thong_bao = "Không có sách nào thực sự phù hợp với yêu cầu của bạn."

    ket_qua_cuoi = {
        "ket_qua": ket_qua_sach,
        "tong_so_ket_qua": len(ket_qua_sach),
        "thong_bao": thong_bao,
        "context_so_bo": len(context),
    }

    _logger.info(
        f"[CHATBOT_SERVICE] '{cau_hoi[:50]}' → "
        f"context={len(context)}, LLM chọn={len(ket_qua_goc)}, "
        f"sau lọc bịa={len(ket_qua_sach)}"
    )

    return ket_qua_cuoi
