"""
Backend Router: Chatbot AI Tra cứu Sách (Phiên bản V3 chính thức).
Tích hợp RAG Retrieval (ChromaDB + Fuzzy) kết hợp System Prompt V3 (JSON Schema + Guardrails).
"""

import sys
from pathlib import Path
from typing import Optional, List, Any
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

# Đảm bảo root path được đưa vào sys.path để import module chatbotAI
_app_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_app_root) not in sys.path:
    sys.path.insert(0, str(_app_root))

from chatbotAI.chatbot_service import tra_cuu_sach
from chatbotAI.vector_store import VectorStore
from chatbotAI.config import PROMPT_VERSION, doc_system_prompt

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])


class QuestionRequest(BaseModel):
    cau_hoi: str


class BookItem(BaseModel):
    ten_sach: str
    tac_gia: Optional[str] = ""
    ly_do_goi_y: Optional[str] = ""
    con_hang: Optional[bool] = True


class ChatbotResponse(BaseModel):
    ket_qua: List[Any] = []
    tong_so_ket_qua: int = 0
    thong_bao: str = ""
    thoi_gian_ms: int = 0
    prompt_version: str = "v3"
    context_so_bo: int = 0
    canh_bao_bia: bool = False


@router.post("/hoi", response_model=ChatbotResponse)
def hoi_chatbot(req: QuestionRequest):
    """
    Endpoint chính thức nhận câu hỏi tự nhiên từ độc giả / thủ thư và trả về gợi ý sách.
    Luôn áp dụng phiên bản prompt V3 chuẩn hóa JSON và bảo vệ 2 lớp chống lạc đề.
    """
    cau_hoi = (req.cau_hoi or "").strip()
    if not cau_hoi:
        raise HTTPException(status_code=400, detail="Vui lòng nhập câu hỏi.")

    try:
        # Gọi tra cứu sách với phiên bản V3 chính thức
        res = tra_cuu_sach(cau_hoi, prompt_version="v3")
        if "loi" in res:
            raise HTTPException(status_code=500, detail=res["loi"])

        return ChatbotResponse(
            ket_qua=res.get("ket_qua", []),
            tong_so_ket_qua=res.get("tong_so_ket_qua", 0),
            thong_bao=res.get("thong_bao", ""),
            thoi_gian_ms=res.get("thoi_gian_ms", 0),
            prompt_version=res.get("prompt_version", "v3"),
            context_so_bo=res.get("context_so_bo", 0),
            canh_bao_bia=res.get("canh_bao_bia", False),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý chatbot AI: {str(e)}")


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
