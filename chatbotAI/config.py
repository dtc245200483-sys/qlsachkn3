"""
config.py — Cấu hình phiên bản prompt và các thiết lập toàn cục cho Chatbot AI.
"""

from pathlib import Path
from typing import Optional

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"

# Phiên bản prompt mặc định của hệ thống chính
PROMPT_VERSION = "v3"

PROMPT_MAP = {
    "v1": PROMPTS_DIR / "v1_co_ban.txt",
    "v2": PROMPTS_DIR / "v2_co_rang_buoc.txt",
    "v3": PROMPTS_DIR / "v3_json_hoan_chinh.txt",
}


def doc_system_prompt(version: Optional[str] = None) -> str:
    """
    Đọc nội dung system prompt theo phiên bản mong muốn.

    Tham số:
        version (str, optional): "v1", "v2", "v3" hoặc tên file cụ thể.
            Nếu không truyền, sử dụng PROMPT_VERSION mặc định.

    Trả về:
        str: Nội dung system prompt đã đọc.
    """
    target_version = version or PROMPT_VERSION

    if target_version in PROMPT_MAP:
        file_path = PROMPT_MAP[target_version]
    else:
        # Nếu truyền tên file cụ thể hoặc path
        possible_path = PROMPTS_DIR / target_version
        if possible_path.exists():
            file_path = possible_path
        else:
            # Fallback về system_prompt.txt
            file_path = PROMPTS_DIR / "system_prompt.txt"

    if not file_path.exists():
        raise FileNotFoundError(f"Không tìm thấy system prompt tại: {file_path}")

    return file_path.read_text(encoding="utf-8").strip()
