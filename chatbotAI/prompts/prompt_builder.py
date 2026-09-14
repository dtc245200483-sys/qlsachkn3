"""
prompt_builder.py — Module xây dựng prompt và luồng tra cứu sách AI.

Cung cấp:
    - xay_dung_user_prompt(): Ghép câu hỏi + dữ liệu sách đã lọc thành user prompt.
    - tra_cuu_sach():          Luồng đầy đủ: fuzzy search → xây prompt → gọi LLM → parse JSON.
"""

import json
import sys
from pathlib import Path
from typing import Optional

# Đảm bảo hiển thị đúng tiếng Việt trên Windows console
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

# Đường dẫn tương đối từ file này đến system_prompt.txt
PROMPTS_DIR = Path(__file__).resolve().parent
SYSTEM_PROMPT_FILE = PROMPTS_DIR / "system_prompt.txt"

# Đường dẫn đến thư mục chatbotAI (cha của prompts/) để import các module khác
CHATBOT_DIR = PROMPTS_DIR.parent
import sys as _sys
if str(CHATBOT_DIR.parent) not in _sys.path:
    _sys.path.insert(0, str(CHATBOT_DIR.parent))

# Import từ các module trong chatbotAI/
from chatbotAI.llm_client import call_llm          # noqa: E402
from chatbotAI.search_engine import tim_kiem_so_bo  # noqa: E402


# ---------------------------------------------------------------------------
# Hàm 1: Đọc system prompt từ file .txt
# ---------------------------------------------------------------------------

def _doc_system_prompt() -> str:
    """
    Đọc nội dung system prompt từ file system_prompt.txt.
    Tách biệt hoàn toàn khỏi code Python (không hardcode trong .py).

    Trả về:
        str: Nội dung file system_prompt.txt.

    Lỗi:
        FileNotFoundError nếu file không tồn tại.
        IOError nếu không đọc được file.
    """
    if not SYSTEM_PROMPT_FILE.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file system prompt tại: {SYSTEM_PROMPT_FILE}\n"
            "Hãy đảm bảo file 'chatbotAI/prompts/system_prompt.txt' đã được tạo."
        )
    try:
        return SYSTEM_PROMPT_FILE.read_text(encoding="utf-8").strip()
    except IOError as e:
        raise IOError(f"Không thể đọc file system prompt: {e}") from e


# ---------------------------------------------------------------------------
# Hàm 2: Xây dựng user prompt từ câu hỏi + danh sách sách đã lọc
# ---------------------------------------------------------------------------

def xay_dung_user_prompt(cau_hoi: str, ket_qua_loc: list[dict]) -> str:
    """
    Ghép câu hỏi của độc giả và danh sách sách đã lọc sơ bộ thành user prompt
    hoàn chỉnh để gửi cho LLM.

    Danh sách sách được rút gọn — chỉ giữ các trường cần thiết để tránh gửi
    thông tin cá nhân hay dữ liệu nội bộ thừa cho LLM:
        - ten_sach
        - tac_gia
        - tom_tat_noi_dung (tối đa 300 ký tự để tiết kiệm token)
        - so_luong_con
        - ly_do_khop_so_bo (từ bước tìm kiếm sơ bộ)

    Tham số:
        cau_hoi (str):           Câu hỏi gốc của độc giả.
        ket_qua_loc (list[dict]): Danh sách sách đã qua bước fuzzy search,
                                  có trường "ly_do_khop_so_bo" và "diem_khop".

    Trả về:
        str: Nội dung user prompt hoàn chỉnh, sẵn sàng gửi cho LLM.
    """
    if not cau_hoi or not isinstance(cau_hoi, str):
        cau_hoi = "(Không có câu hỏi)"

    # Rút gọn thông tin sách để bảo vệ dữ liệu nội bộ và tiết kiệm token
    sach_rut_gon: list[dict] = []
    for sach in (ket_qua_loc or []):
        if not isinstance(sach, dict):
            continue

        tom_tat_goc = sach.get("tom_tat_noi_dung", "")
        tom_tat_rut = (tom_tat_goc[:300] + "...") if len(tom_tat_goc) > 300 else tom_tat_goc

        sach_rut_gon.append({
            "ten_sach": sach.get("ten_sach", ""),
            "tac_gia": sach.get("tac_gia", ""),
            "tom_tat": tom_tat_rut,
            "so_luong_con": sach.get("so_luong_con", 0),
            "ly_do_khop_so_bo": sach.get("ly_do_khop_so_bo", ""),
        })

    # Tạo phần JSON danh sách sách (đọc được, có indent)
    du_lieu_json = json.dumps(sach_rut_gon, ensure_ascii=False, indent=2)

    user_prompt = (
        f"CÂU HỎI CỦA ĐỘC GIẢ:\n{cau_hoi.strip()}\n\n"
        f"DANH SÁCH SÁCH CÓ TRONG THƯ VIỆN (dữ liệu tra cứu — chỉ dùng những sách này):\n"
        f"{du_lieu_json}\n\n"
        "Hãy phân tích câu hỏi và gợi ý sách phù hợp từ danh sách trên. "
        "Trả về kết quả theo đúng định dạng JSON đã được quy định trong system prompt."
    )

    return user_prompt


# ---------------------------------------------------------------------------
# Hàm 3: Luồng tra cứu sách đầy đủ
# ---------------------------------------------------------------------------

def tra_cuu_sach(cau_hoi: str, danh_sach_sach: list[dict]) -> dict:
    """
    Hàm chính điều phối toàn bộ luồng tra cứu sách thông minh:
        1. Tìm kiếm sơ bộ (fuzzy search) trên danh_sach_sach.
        2. Xây dựng user prompt từ kết quả lọc.
        3. Đọc system prompt từ file system_prompt.txt.
        4. Gọi LLM (call_llm) để AI phân tích và gợi ý.
        5. Parse JSON kết quả trả về từ LLM.

    Tham số:
        cau_hoi (str):            Câu hỏi tra cứu của độc giả.
        danh_sach_sach (list[dict]): Danh sách toàn bộ sách trong thư viện.

    Trả về:
        dict: Kết quả parse JSON từ LLM theo schema:
              {
                "ket_qua": [{"ten_sach": ..., "tac_gia": ...,
                             "ly_do_goi_y": ..., "con_hang": ...}],
                "tong_so_ket_qua": int
              }
              Hoặc trả về {"loi": "Mô tả lỗi"} nếu có lỗi xảy ra.
    """
    # Bước 1: Tìm kiếm sơ bộ bằng fuzzy match
    try:
        ket_qua_loc = tim_kiem_so_bo(cau_hoi, danh_sach_sach)
    except Exception as e:
        return {"loi": f"[Lỗi Tìm Kiếm Sơ Bộ] Fuzzy search thất bại: {str(e)}"}

    # Bước 2: Xây dựng user prompt từ câu hỏi + kết quả lọc
    try:
        user_prompt = xay_dung_user_prompt(cau_hoi, ket_qua_loc)
    except Exception as e:
        return {"loi": f"[Lỗi Xây Dựng Prompt] Không thể tạo user prompt: {str(e)}"}

    # Bước 3: Đọc system prompt từ file
    try:
        system_prompt = _doc_system_prompt()
    except (FileNotFoundError, IOError) as e:
        return {"loi": f"[Lỗi Cấu Hình] {str(e)}"}

    # Nếu không có kết quả lọc sơ bộ, trả về ngay mà không cần gọi LLM
    if not ket_qua_loc:
        return {"ket_qua": [], "tong_so_ket_qua": 0}

    # Bước 4: Gọi LLM qua call_llm()
    try:
        phan_hoi_llm = call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
    except Exception as e:
        return {"loi": f"[Lỗi Gọi LLM] Không thể liên lạc với LLM API: {str(e)}"}

    # Kiểm tra phản hồi LLM có phải thông báo lỗi không
    if isinstance(phan_hoi_llm, str) and phan_hoi_llm.startswith("[Lỗi"):
        return {"loi": f"[Lỗi LLM] {phan_hoi_llm}"}

    # Bước 5: Parse kết quả JSON từ LLM
    try:
        # Cố gắng trích xuất JSON từ phản hồi LLM (phòng khi LLM thêm text thừa)
        noi_dung = phan_hoi_llm.strip()

        # Tìm kiếm khối JSON trong phản hồi nếu LLM trả về text kèm JSON
        bat_dau = noi_dung.find("{")
        ket_thuc = noi_dung.rfind("}") + 1
        if bat_dau != -1 and ket_thuc > bat_dau:
            noi_dung = noi_dung[bat_dau:ket_thuc]

        ket_qua_dict = json.loads(noi_dung)

        # Validate cơ bản schema trả về
        if "ket_qua" not in ket_qua_dict:
            return {"loi": "[Lỗi Parse JSON] Phản hồi LLM thiếu trường 'ket_qua'."}
        if "tong_so_ket_qua" not in ket_qua_dict:
            # Tự tính nếu LLM quên trả về
            ket_qua_dict["tong_so_ket_qua"] = len(ket_qua_dict["ket_qua"])

        return ket_qua_dict

    except json.JSONDecodeError as json_err:
        return {
            "loi": (
                f"[Lỗi Parse JSON] Không thể đọc phản hồi JSON từ LLM: {str(json_err)}. "
                f"Phản hồi gốc (100 ký tự đầu): {phan_hoi_llm[:100]!r}"
            )
        }
    except Exception as e:
        return {"loi": f"[Lỗi Không Xác Định] {str(e)}"}


# ---------------------------------------------------------------------------
# Chạy thử khi gọi trực tiếp file này
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    DU_LIEU_MAU = [
        {
            "ten_sach": "Trí tuệ nhân tạo: Tiếp cận hiện đại",
            "tac_gia": "Stuart Russell & Peter Norvig",
            "tom_tat_noi_dung": (
                "Giáo trình kinh điển và toàn diện nhất về AI, bao gồm tìm kiếm, "
                "suy luận logic, học máy, mạng nơ-ron và ứng dụng trong thực tế."
            ),
            "so_luong_con": 3,
        },
        {
            "ten_sach": "Học sâu (Deep Learning)",
            "tac_gia": "Ian Goodfellow, Yoshua Bengio, Aaron Courville",
            "tom_tat_noi_dung": (
                "Sách chuyên sâu về học sâu, mạng nơ-ron nhân tạo, CNN, RNN "
                "và các kỹ thuật hiện đại trong học máy."
            ),
            "so_luong_con": 1,
        },
        {
            "ten_sach": "Python Machine Learning",
            "tac_gia": "Sebastian Raschka",
            "tom_tat_noi_dung": (
                "Hướng dẫn toàn diện học máy với Python và scikit-learn, "
                "phù hợp cho người mới bắt đầu và trung cấp."
            ),
            "so_luong_con": 2,
        },
        {
            "ten_sach": "Nhập môn trí tuệ nhân tạo",
            "tac_gia": "Nguyễn Thanh Thủy",
            "tom_tat_noi_dung": (
                "Sách tiếng Việt nhập môn AI dành cho sinh viên đại học, "
                "trình bày các khái niệm cơ bản rõ ràng và dễ hiểu."
            ),
            "so_luong_con": 0,
        },
        {
            "ten_sach": "Cấu trúc dữ liệu và giải thuật",
            "tac_gia": "Thomas H. Cormen",
            "tom_tat_noi_dung": (
                "Giáo trình nền tảng về cấu trúc dữ liệu, thuật toán sắp xếp, "
                "tìm kiếm và phân tích độ phức tạp."
            ),
            "so_luong_con": 4,
        },
        {
            "ten_sach": "Văn học Việt Nam hiện đại",
            "tac_gia": "Phan Cự Đệ",
            "tom_tat_noi_dung": (
                "Tổng quan về lịch sử và các tác phẩm văn học Việt Nam "
                "giai đoạn hiện đại từ đầu thế kỷ 20 đến nay."
            ),
            "so_luong_con": 7,
        },
    ]

    CAU_HOI = "sách về trí tuệ nhân tạo cho người mới bắt đầu"
    print("=" * 60)
    print(f"CÂU HỎI: {CAU_HOI}")
    print("=" * 60)

    # Bước 1: Tìm kiếm sơ bộ
    from chatbotAI.search_engine import tim_kiem_so_bo
    ket_qua_loc = tim_kiem_so_bo(CAU_HOI, DU_LIEU_MAU)
    print(f"\n[Bước 1] Fuzzy Search — Tìm thấy {len(ket_qua_loc)} kết quả sơ bộ:")
    for s in ket_qua_loc:
        print(f"  • {s['ten_sach']} | Điểm: {s['diem_khop']} | Khớp qua: {s['ly_do_khop_so_bo']}")

    # Bước 2: Xây dựng user prompt
    user_prompt_demo = xay_dung_user_prompt(CAU_HOI, ket_qua_loc)
    print(f"\n[Bước 2] User Prompt (200 ký tự đầu):\n  {user_prompt_demo[:200]}...")

    # Bước 3-5: Gọi LLM (cần API key thật)
    print("\n[Bước 3-5] Gọi tra_cuu_sach() — cần cấu hình OPENROUTER_API_KEY trong chatbotAI/.env")
    ket_qua_cuoi = tra_cuu_sach(CAU_HOI, DU_LIEU_MAU)
    print("\n[Kết quả cuối]:")
    print(json.dumps(ket_qua_cuoi, ensure_ascii=False, indent=2))
