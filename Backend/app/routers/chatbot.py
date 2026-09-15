"""
Backend Router: Chatbot AI Tra cứu Sách (Phiên bản V3 chính thức).
Tích hợp RAG Retrieval (ChromaDB + Fuzzy) kết hợp System Prompt V3 (JSON Schema + Guardrails).
"""

import sys
from pathlib import Path
from typing import Optional, List, Any
from pydantic import BaseModel
import time
import threading
from collections import defaultdict
from fastapi import APIRouter, Request

# Đảm bảo root path được đưa vào sys.path để import module chatbotAI
_app_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_app_root) not in sys.path:
    sys.path.insert(0, str(_app_root))

from chatbotAI.chatbot_service import tra_cuu_sach
from chatbotAI.vector_store import VectorStore
from chatbotAI.config import PROMPT_VERSION, doc_system_prompt

router = APIRouter(prefix="/api/chatbot", tags=["Chatbot AI"])

# Rate limit đơn giản theo IP (dict lưu timestamp): tối đa 10 câu hỏi / phút / IP
_rate_limit_lock = threading.Lock()
_ip_call_history = defaultdict(list)
RATE_LIMIT_MAX_CALLS = 10
RATE_LIMIT_WINDOW = 60.0  # giây


def _check_rate_limit(client_ip: str) -> bool:
    """Trả về True nếu được phép gọi, False nếu vượt ngưỡng rate limit."""
    now = time.time()
    with _rate_limit_lock:
        calls = _ip_call_history[client_ip]
        # Lọc bỏ các timestamp cũ hơn cửa sổ 60s
        valid_calls = [t for t in calls if now - t < RATE_LIMIT_WINDOW]
        _ip_call_history[client_ip] = valid_calls

        if len(valid_calls) >= RATE_LIMIT_MAX_CALLS:
            return False

        _ip_call_history[client_ip].append(now)
        return True


class QuestionRequest(BaseModel):
    cau_hoi: str


class BookItem(BaseModel):
    ma_sach: Optional[str] = ""
    ten_sach: str
    tac_gia: Optional[str] = ""
    the_loai: Optional[str] = ""
    tom_tat: Optional[str] = ""
    ly_do_goi_y: Optional[str] = ""
    khop_voi_tu_khoa: Optional[List[str]] = []
    con_hang: Optional[bool] = True


class ChatbotResponse(BaseModel):
    ket_qua: List[Any] = []
    tong_so_ket_qua: int = 0
    thong_bao: str = ""
    tu_khoa_nhan_manh: List[str] = []
    phan_tich_yeu_cau: Optional[str] = ""
    thoi_gian_ms: int = 0
    prompt_version: str = "v3"
    context_so_bo: int = 0
    canh_bao_bia: bool = False


@router.post("/hoi", response_model=ChatbotResponse)
def hoi_chatbot(req: QuestionRequest, request: Request):
    """
    Endpoint chính thức nhận câu hỏi tự nhiên từ độc giả / thủ thư và trả về gợi ý sách.
    - Không yêu cầu đăng nhập (độc giả vãng lai dùng được).
    - Rate limit: tối đa 10 câu hỏi / phút / IP.
    - Luôn trả HTTP 200 kèm thong_bao thân thiện nếu gặp lỗi (không trả 500 gây trắng màn hình).
    """
    client_ip = "unknown"
    if request.client and request.client.host:
        client_ip = request.client.host

    # Kiểm tra rate limit theo IP
    if not _check_rate_limit(client_ip):
        return ChatbotResponse(
            ket_qua=[],
            tong_so_ket_qua=0,
            thong_bao="Bạn đã gửi quá nhiều câu hỏi trong thời gian ngắn (tối đa 10 câu/phút). Vui lòng chờ 1 phút rồi thử lại nhé!",
            thoi_gian_ms=0,
            prompt_version="v3",
        )

    cau_hoi = (req.cau_hoi or "").strip()
    if not cau_hoi:
        return ChatbotResponse(
            ket_qua=[],
            tong_so_ket_qua=0,
            thong_bao="Vui lòng nhập câu hỏi tra cứu sách nhé!",
            thoi_gian_ms=0,
            prompt_version="v3",
        )

    try:
        # Gọi tra cứu sách với phiên bản V3 chính thức
        res = tra_cuu_sach(cau_hoi, prompt_version="v3")

        # Xử lý lỗi từ chatbot_service: trả HTTP 200 kèm nội dung lỗi thân thiện
        if "loi" in res:
            return ChatbotResponse(
                ket_qua=[],
                tong_so_ket_qua=0,
                thong_bao=f"Thông báo: {res['loi']}",
                thoi_gian_ms=0,
                prompt_version="v3",
            )

        return ChatbotResponse(
            ket_qua=res.get("ket_qua", []),
            tong_so_ket_qua=res.get("tong_so_ket_qua", 0),
            thong_bao=res.get("thong_bao", ""),
            tu_khoa_nhan_manh=res.get("tu_khoa_nhan_manh", []),
            phan_tich_yeu_cau=res.get("phan_tich_yeu_cau", ""),
            thoi_gian_ms=res.get("thoi_gian_ms", 0),
            prompt_version=res.get("prompt_version", "v3"),
            context_so_bo=res.get("context_so_bo", 0),
            canh_bao_bia=res.get("canh_bao_bia", False),
        )
    except Exception as e:
        # Luôn trả HTTP 200 kèm thông báo thân thiện thay vì lỗi 500
        return ChatbotResponse(
            ket_qua=[],
            tong_so_ket_qua=0,
            thong_bao="Xin lỗi, hệ thống đang gặp sự cố kết nối với AI. Bạn vui lòng thử lại sau nhé!",
            thoi_gian_ms=0,
            prompt_version="v3",
        )


@router.get("/health")
def chatbot_health():
    """
    Kiểm tra trạng thái sẵn sàng của dịch vụ Chatbot AI và Vector Store.
    """
    try:
        vs = VectorStore()
        so_luong_sach = vs.dem_so_luong()
        sys_prompt = doc_system_prompt("v3")
        return {
            "trang_thai": "san_sang",
            "phien_ban_prompt": PROMPT_VERSION,
            "do_dai_prompt": len(sys_prompt),
            "so_sach_vector_store": so_luong_sach,
        }
    except Exception as e:
        return {
            "trang_thai": "loi",
            "chi_tiet": str(e),
            "phien_ban_prompt": PROMPT_VERSION,
        }
