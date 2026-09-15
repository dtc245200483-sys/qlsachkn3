"""
prompt_builder.py — Xây dựng user prompt từ câu hỏi + context RAG.

Ghép câu hỏi độc giả + danh sách sách đã lọc (context) thành user prompt
gửi cho LLM. Context được rút gọn và định dạng JSON rõ ràng.
"""

import json
import sys
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def xay_dung_user_prompt(cau_hoi: str, context: list[dict]) -> str:
    """
    Ghép câu hỏi của độc giả + context (từ truy_xuat_context()) thành user prompt.

    Context được rút gọn — chỉ giữ các trường cần thiết cho LLM đánh giá:
        ten_sach, tac_gia, tom_tat (≤300 ký tự), con_hang,
        nguon_khop, diem_lien_quan

    Tham số:
        cau_hoi (str):       Câu hỏi gốc của độc giả.
        context (list[dict]): Danh sách sách từ truy_xuat_context().

    Trả về:
        str: User prompt hoàn chỉnh, sẵn sàng gửi cho LLM.
    """
    cau_hoi = (cau_hoi or "").strip() or "(Không có câu hỏi)"

    # Rút gọn context để tiết kiệm token, chỉ giữ trường LLM cần
    context_rut_gon = []
    for sach in (context or []):
        if not isinstance(sach, dict):
            continue

        tom_tat_goc = (sach.get("tom_tat") or "").strip()
        # Giữ trọn vẹn tóm tắt (tối đa 1000 ký tự) để AI đọc hiểu đầy đủ cốt truyện / chủ đề
        tom_tat_rut = (
            (tom_tat_goc[:1000] + "...") if len(tom_tat_goc) > 1000
            else tom_tat_goc
        )

        nguon_khop = sach.get("nguon_khop", [])
        mo_ta_nguon = []
        if "ngu_nghia" in nguon_khop:
            diem = sach.get("diem_tuong_dong", 0)
            mo_ta_nguon.append(f"ngữ nghĩa ({diem:.2f})")
        if "ten_rieng" in nguon_khop:
            diem = sach.get("diem_khop_ten", 0)
            mo_ta_nguon.append(f"tên riêng ({diem}%)")

        context_rut_gon.append({
            "ma_sach": sach.get("ma_sach", ""),
            "ten_sach": sach.get("ten_sach", ""),
            "tac_gia": sach.get("tac_gia", ""),
            "the_loai": sach.get("the_loai", ""),
            "tom_tat": tom_tat_rut,
            "con_hang": sach.get("con_hang", False),
            "nguon_khop": " + ".join(mo_ta_nguon) if mo_ta_nguon else "không rõ",
            "diem_lien_quan": sach.get("diem_lien_quan", 0),
        })

    context_json = json.dumps(context_rut_gon, ensure_ascii=False, indent=2)

    user_prompt = (
        f"Câu hỏi của độc giả: {cau_hoi}\n\n"
        f"Danh sách sách tìm được từ thư viện (kèm tóm tắt nội dung thực tế):\n"
        f"{context_json}\n\n"
        "Nhiệm vụ của bạn:\n"
        "1. Phân tích câu hỏi, trích xuất danh sách các từ khóa / khái niệm cốt lõi mà độc giả nhấn mạnh vào 'tu_khoa_nhan_manh'.\n"
        "2. Đọc kỹ phần 'tom_tat' của từng cuốn sách trên, so sánh đối chiếu với các từ khóa và nhu cầu của độc giả.\n"
        "3. Chọn lọc những cuốn sách THỰC SỰ phù hợp hoặc liên quan, chỉ ra các từ khóa khớp ('khop_voi_tu_khoa') và giải thích rõ trong 'ly_do_goi_y' dựa trên nội dung tóm tắt thực tế của sách.\n"
        "4. Trả về đúng định dạng JSON đã quy định trong system prompt."
    )

    return user_prompt
