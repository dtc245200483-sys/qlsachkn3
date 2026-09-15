"""
api_v2.py — Backend FastAPI cho giao diện thử nghiệm V2 (Port 8002).
Cố định sử dụng system prompt: v2_co_rang_buoc.txt
"""

import sys
from pathlib import Path

# Thêm thư mục app gốc vào sys.path
APP_ROOT = Path(__file__).resolve().parent.parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from chatbotAI.chatbot_service import tra_cuu_sach

app = FastAPI(title="Chatbot AI Test UI - V2 (Có ràng buộc)")

# Cho phép CORS từ mọi origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HTML_FILE = Path(__file__).resolve().parent / "index.html"


class QuestionRequest(BaseModel):
    cau_hoi: str


@app.get("/", response_class=HTMLResponse)
def get_ui():
    """Phục vụ trực tiếp file giao diện index.html."""
    if HTML_FILE.exists():
        return HTMLResponse(content=HTML_FILE.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Không tìm thấy index.html</h1>", status_code=404)


@app.post("/hoi")
def hoi_v2(req: QuestionRequest):
    """
    Endpoint nhận câu hỏi và LUÔN ép sử dụng phiên bản prompt v2.
    """
    ket_qua = tra_cuu_sach(req.cau_hoi, prompt_version="v2")
    return ket_qua


if __name__ == "__main__":
    import uvicorn
    print("🚀 Đang khởi động Test UI V2 tại http://localhost:8002")
    uvicorn.run(app, host="0.0.0.0", port=8002)
