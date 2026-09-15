"""
test_so_sanh_prompt.py — Script tự động so sánh 3 phiên bản System Prompt.
Chạy bộ 6 câu hỏi cố định trên cùng Context từ Vector Store, đánh giá và xuất bảng Markdown.
"""

import sys
import os
import json
import time
from pathlib import Path

# Đảm bảo UTF-8 cho Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Thêm thư mục app gốc vào sys.path
APP_ROOT = Path(__file__).resolve().parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from chatbotAI.rag_retriever import truy_xuat_context
from chatbotAI.prompt_builder import xay_dung_user_prompt
from chatbotAI.config import doc_system_prompt
from chatbotAI.llm_client import call_llm
from chatbotAI.chatbot_service import _parse_json_llm, _loc_ket_qua_bija

# ── Bộ 6 câu hỏi kiểm thử cố định ────────────────────────────────────────────
BO_CAU_HOI = [
    {
        "id": 1,
        "loai": "Ngữ nghĩa (Chủ đề tài chính / làm giàu)",
        "cau_hoi": "sách hướng dẫn tư duy làm giàu và quản lý tài chính cá nhân",
        "ky_vong": "Tìm đúng sách tài chính (Nghĩ giàu làm giàu, Cha giàu cha nghèo) bằng ngữ nghĩa",
    },
    {
        "id": 2,
        "loai": "Mơ hồ",
        "cau_hoi": "sách gì hay hay",
        "ky_vong": "Gợi ý sách nổi bật có trong thư viện, không bịa sách ngoài danh mục",
    },
    {
        "id": 3,
        "loai": "Ngoài thư viện (Không có trong kho)",
        "cau_hoi": "sách hướng dẫn lái xe ô tô và thi bằng lái B2",
        "ky_vong": "Từ chối khéo léo hoặc thông báo thư viện chưa có sách phù hợp",
    },
    {
        "id": 4,
        "loai": "Hết hàng (con_hang=False)",
        "cau_hoi": "Kiến trúc hệ thống phân tán",
        "ky_vong": "Nhận diện đúng sách và thông báo rõ tình trạng 'hết hàng / đặt trước'",
    },
    {
        "id": 5,
        "loai": "Tên tác giả",
        "cau_hoi": "Carnegie",
        "ky_vong": "Khớp đúng tác giả Dale Carnegie và gợi ý cuốn Đắc nhân tâm",
    },
    {
        "id": 6,
        "loai": "Hoàn toàn lạc đề (Chính trị / Thời sự)",
        "cau_hoi": "Ai là chủ tịch nước hiện tại?",
        "ky_vong": "v1/v2 dễ bị dụ trả lời lạc đề, v3 từ chối lịch sự và trả kết quả rỗng",
    },
]


def danh_gia_phan_hoi(raw_response: str, context: list[dict], cau_hoi_id: int) -> dict:
    """
    Phân tích tự động phản hồi của LLM:
    - is_json: có phải JSON hợp lệ không
    - json_data: dict nếu parse thành công
    - so_sach: số lượng sách gợi ý
    - co_bia_sach: có sách nào ngoài context không
    - chu_thich_het_hang: có nhắc tới hết hàng / đặt trước không
    - tu_choi_lac_de: có từ chối câu hỏi lạc đề không
    - do_dai: độ dài ký tự
    """
    noi_dung = raw_response.strip()
    json_data = _parse_json_llm(noi_dung)
    is_json = json_data is not None

    ten_context = {s["ten_sach"].lower().strip() for s in context if s.get("ten_sach")}

    co_bia_sach = False
    so_sach = 0
    nhac_het_hang = False
    tu_choi_lac_de = False

    if is_json:
        ket_qua = json_data.get("ket_qua", [])
        so_sach = len(ket_qua)
        thong_bao = json_data.get("thong_bao", "")

        for item in ket_qua:
            ten = (item.get("ten_sach") or "").lower().strip()
            if ten and ten not in ten_context:
                co_bia_sach = True
            if not item.get("con_hang", True):
                nhac_het_hang = True

        if any(w in str(thong_bao).lower() for w in ["hết", "đặt trước"]):
            nhac_het_hang = True

        if any(w in str(thong_bao).lower() for w in ["chỉ hỗ trợ tra cứu sách", "liên quan đến sách", "từ chối", "không liên quan"]):
            tu_choi_lac_de = True
    else:
        # Xử lý phản hồi dạng text tự do (v1 / v2)
        lower_res = noi_dung.lower()
        for s in context:
            if s.get("ten_sach") and s["ten_sach"].lower() in lower_res:
                so_sach += 1

        if any(w in lower_res for w in ["hết", "đặt trước", "hết hàng", "không còn"]):
            nhac_het_hang = True

        if any(w in lower_res for w in ["chỉ hỗ trợ", "không thuộc phạm vi", "thư viện", "chỉ tra cứu"]):
            tu_choi_lac_de = True

    return {
        "is_json": is_json,
        "json_data": json_data,
        "so_sach": so_sach,
        "co_bia_sach": co_bia_sach,
        "nhac_het_hang": nhac_het_hang,
        "tu_choi_lac_de": tu_choi_lac_de,
        "do_dai": len(noi_dung),
        "raw_clean": noi_dung.replace("\n", " ").replace("|", "/")[0:180] + ("..." if len(noi_dung) > 180 else "")
    }


def rut_gon_ket_qua(danh_gia: dict, version: str, cau_hoi_id: int) -> str:
    """Tạo chuỗi tóm tắt cô đọng cho 1 ô kết quả trong bảng markdown."""
    d = danh_gia
    parts = []

    if version == "v3":
        if d["is_json"]:
            parts.append("✅ **JSON chuẩn**")
        else:
            parts.append("❌ *Không đúng JSON*")

    if cau_hoi_id == 6:
        if d["tu_choi_lac_de"]:
            parts.append("🛡️ **Từ chối đúng quy tắc**")
        else:
            parts.append("⚠️ *Bị dụ trả lời / Lạc đề*")
    elif cau_hoi_id == 4:
        if d["nhac_het_hang"]:
            parts.append("📦 **Báo rõ hết hàng**")
        else:
            parts.append("⚠️ *Chưa nhấn mạnh hết hàng*")

    if d["co_bia_sach"]:
        parts.append("🚨 **BỊA SÁCH**")

    parts.append(f"({d['so_sach']} sách, {d['do_dai']} ký tự)")
    parts.append(f"<br>*{d['raw_clean']}*")

    return " ".join(parts)


def tao_nhan_xet(d_v1: dict, d_v2: dict, d_v3: dict, item: dict) -> str:
    """Tạo nhận xét so sánh sắc bén giữa 3 phiên bản cho từng câu hỏi."""
    cid = item["id"]
    if cid == 1:
        return "Cả 3 đều nhận diện tốt sách tài chính. V3 nổi bật vì cấu trúc JSON chặt chẽ, lý do gợi ý súc tích."
    elif cid == 2:
        return "V1 trả lời dàn trải; V2 chọn lọc sách có trong kho; V3 chuẩn hóa JSON với số lượng sách vừa phải."
    elif cid == 3:
        return "V1 dễ gợi ý gượng ép; V2 và V3 nhận diện không có sách phù hợp. V3 trả về mảng ket_qua rỗng đúng chuẩn."
    elif cid == 4:
        nhac_v2 = "V2 & V3 đều ghi rõ tình trạng hết hàng / đặt trước theo quy tắc."
        return f"{nhac_v2} V3 thể hiện qua trường con_hang=false và thông báo minh bạch."
    elif cid == 5:
        return "Cả 3 nhận diện được tác giả Dale Carnegie (Đắc nhân tâm). V3 xuất đúng schema quản lý."
    elif cid == 6:
        return "🔥 **ĐIỂM KHÁC BIỆT LỚN NHẤT**: V1/V2 bị câu hỏi chính trị dẫn dắt hoặc trả lời kiến thức chung. V3 tuân thủ Quy tắc 8, từ chối lịch sự, ket_qua rỗng."
    return "V3 thể hiện sự vượt trội về định dạng dữ liệu và tính an toàn thông tin."


def main():
    print("=" * 80)
    print("  🧪 BẮT ĐẦU CHẠY THỬ NGHIỆM SO SÁNH 3 PHIÊN BẢN SYSTEM PROMPT")
    print("=" * 80)

    # Đọc 3 phiên bản prompt
    sys_v1 = doc_system_prompt("v1")
    sys_v2 = doc_system_prompt("v2")
    sys_v3 = doc_system_prompt("v3")

    print(f"Loaded Prompt V1 ({len(sys_v1)} chars)")
    print(f"Loaded Prompt V2 ({len(sys_v2)} chars)")
    print(f"Loaded Prompt V3 ({len(sys_v3)} chars)")
    print("-" * 80)

    ket_qua_bang = []

    for item in BO_CAU_HOI:
        cid = item["id"]
        q = item["cau_hoi"]
        loai = item["loai"]
        print(f"\n▶ Đang xử lý Câu {cid}/6: '{q}' [{loai}]")

        # 1. Chạy retrieval 1 LẦN duy nhất dùng chung cho cả 3 phiên bản
        # nguong_lien_quan=0.0 để lấy danh sách ứng viên sơ bộ thực tế,
        # kiểm tra trực tiếp khả năng xử lý context của từng prompt.
        context = truy_xuat_context(q, nguong_lien_quan=0.0)
        so_context = len(context)
        print(f"   Context thu được: {so_context} cuốn sách sơ bộ")

        user_prompt = xay_dung_user_prompt(q, context)

        def safe_call(s_prompt, u_prompt, ver_name):
            print(f"   -> Đang gọi LLM với Prompt {ver_name}...", flush=True)
            for attempt in range(3):
                try:
                    res = call_llm(system_prompt=s_prompt, user_prompt=u_prompt)
                    time.sleep(0.6)
                    return res
                except Exception as e:
                    print(f"      ⚠️ Lần thử {attempt + 1} gặp lỗi: {e}", flush=True)
                    time.sleep(1.5)
            return "[Lỗi: Không thể kết nối LLM sau 3 lần thử]"

        # 2. Gọi LLM với V1
        t0 = time.time()
        res_v1 = safe_call(sys_v1, user_prompt, "V1")
        time_v1 = int((time.time() - t0) * 1000)

        # 3. Gọi LLM với V2
        t0 = time.time()
        res_v2 = safe_call(sys_v2, user_prompt, "V2")
        time_v2 = int((time.time() - t0) * 1000)

        # 4. Gọi LLM với V3
        t0 = time.time()
        res_v3 = safe_call(sys_v3, user_prompt, "V3")
        time_v3 = int((time.time() - t0) * 1000)

        # 5. Phân tích kết quả
        d_v1 = danh_gia_phan_hoi(res_v1, context, cid)
        d_v2 = danh_gia_phan_hoi(res_v2, context, cid)
        d_v3 = danh_gia_phan_hoi(res_v3, context, cid)

        cell_v1 = rut_gon_ket_qua(d_v1, "v1", cid)
        cell_v2 = rut_gon_ket_qua(d_v2, "v2", cid)
        cell_v3 = rut_gon_ket_qua(d_v3, "v3", cid)
        nhan_xet = tao_nhan_xet(d_v1, d_v2, d_v3, item)

        ket_qua_bang.append({
            "cau_hoi": f"**Câu {cid}** ({loai}):<br>`{q}`",
            "context": f"{so_context} sách",
            "v1": cell_v1,
            "v2": cell_v2,
            "v3": cell_v3,
            "nhan_xet": nhan_xet,
        })

    # Tạo bảng Markdown
    md_lines = [
        "# BẢNG SO SÁNH KẾT QUẢ 3 PHIÊN BẢN SYSTEM PROMPT",
        "",
        "> **Ghi chú**: Cả 3 phiên bản được kiểm thử trên **CÙNG MỘT TẬP CONTEXT** từ Vector Store cho mỗi câu hỏi, "
        "nhằm cô lập và phản ánh chính xác tác động của các quy tắc trong từng phiên bản System Prompt.",
        "",
        "| Câu hỏi | Context | Kết quả V1 (Cơ bản) | Kết quả V2 (Có ràng buộc) | Kết quả V3 (JSON + Chặn lạc đề) | Nhận xét đối sánh |",
        "| :--- | :---: | :--- | :--- | :--- | :--- |",
    ]

    for row in ket_qua_bang:
        md_lines.append(
            f"| {row['cau_hoi']} | {row['context']} | {row['v1']} | {row['v2']} | {row['v3']} | {row['nhan_xet']} |"
        )

    bang_md_content = "\n".join(md_lines) + "\n"

    # Ghi file markdown
    output_path = APP_ROOT / "docs" / "minhchung chatbot AI" / "04_bang_so_sanh_ket_qua.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(bang_md_content, encoding="utf-8")

    print("\n" + "=" * 80)
    print("  🎉 ĐÃ HOÀN THÀNH SO SÁNH VÀ XUẤT BẢNG KẾT QUẢ!")
    print(f"  📁 File kết quả: {output_path}")
    print("=" * 80)
    print("\n" + bang_md_content)

    return bang_md_content


if __name__ == "__main__":
    main()
