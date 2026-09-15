"""
rag_retriever.py — Tầng Retrieval cho hệ thống RAG tra cứu sách.

Kết hợp 2 chiến lược tìm kiếm bù trừ nhau:
  - Embedding (Vector Store): tìm theo Ý NGHĨA / chủ đề / nội dung
  - Fuzzy match (rapidfuzz):  tìm theo TÊN RIÊNG (tên sách, tác giả)

Lý do cần cả 2:
  * Embedding rất mạnh khi hỏi theo nhu cầu ("sách dạy nấu ăn"),
    nhưng yếu với tên riêng vì tên riêng ít mang "nghĩa" ngữ nghĩa.
  * Fuzzy match bù đắp đúng lúc người dùng gõ tên sách/tác giả —
    kể cả khi gõ sai chính tả hoặc chỉ gõ một phần.

Hàm chính: truy_xuat_context(cau_hoi, top_k=8) -> list[dict]
"""

import logging
import sys
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

# Thêm thư mục app gốc vào sys.path
APP_ROOT = Path(__file__).resolve().parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from chatbotAI.vector_store import VectorStore  # noqa: E402

_logger = logging.getLogger("ai_calls")

# Ngưỡng fuzzy match — partial_ratio >= 60 mới tính là khớp
FUZZY_THRESHOLD = 60


# ─────────────────────────────────────────────────────────────────────────────
# Hàm lấy toàn bộ metadata sách từ Vector Store (dùng cho fuzzy match)
# ─────────────────────────────────────────────────────────────────────────────

def _lay_tat_ca_sach_tu_vs(vs: VectorStore) -> list[dict]:
    """
    Lấy toàn bộ sách đang có trong Vector Store để fuzzy match.
    Dùng collection.get() — lấy tất cả documents và metadata.

    Trả về list[dict] với: ma_sach, ten_sach, tac_gia, the_loai, con_hang, tom_tat
    """
    try:
        ket_qua_raw = vs._collection.get(
            include=["documents", "metadatas"],
        )
        ids = ket_qua_raw.get("ids", [])
        documents = ket_qua_raw.get("documents", [])
        metadatas = ket_qua_raw.get("metadatas", [])

        danh_sach = []
        for ma_sach, doc, meta in zip(ids, documents, metadatas):
            con_hang_val = str(meta.get("con_hang", "True")).lower() == "true"
            danh_sach.append({
                "ma_sach": ma_sach,
                "ten_sach": meta.get("ten_sach", ""),
                "tac_gia": meta.get("tac_gia", ""),
                "the_loai": meta.get("the_loai", ""),
                "con_hang": con_hang_val,
                "tom_tat": doc or "",
            })
        return danh_sach
    except Exception as e:
        _logger.warning(f"[RAG_RETRIEVER] Không lấy được danh sách sách từ VS: {e}")
        return []


# ─────────────────────────────────────────────────────────────────────────────
# Hàm fuzzy match tên riêng
# ─────────────────────────────────────────────────────────────────────────────

def _fuzzy_match_ten(cau_hoi: str, tat_ca_sach: list[dict]) -> list[dict]:
    """
    Dùng rapidfuzz.fuzz.partial_ratio so khớp câu hỏi với ten_sach và tac_gia.
    Ngưỡng: partial_ratio >= FUZZY_THRESHOLD (60).

    Trả về list[dict] với thêm trường diem_khop_ten (0–100).
    """
    try:
        from rapidfuzz import fuzz
    except ImportError:
        _logger.error(
            "[RAG_RETRIEVER] 'rapidfuzz' chưa cài. Chạy: pip install rapidfuzz"
        )
        return []

    ket_qua = []
    cau_hoi_lower = cau_hoi.lower().strip()

    for sach in tat_ca_sach:
        diem_ten = fuzz.partial_ratio(cau_hoi_lower, sach["ten_sach"].lower())
        diem_tac_gia = fuzz.partial_ratio(cau_hoi_lower, sach["tac_gia"].lower())
        diem_cao_nhat = max(diem_ten, diem_tac_gia)

        if diem_cao_nhat >= FUZZY_THRESHOLD:
            entry = dict(sach)
            entry["diem_khop_ten"] = diem_cao_nhat
            entry["ly_do_fuzzy"] = (
                f"Tên sách khớp {diem_ten}%" if diem_ten >= diem_tac_gia
                else f"Tác giả khớp {diem_tac_gia}%"
            )
            ket_qua.append(entry)

    # Sắp xếp theo điểm giảm dần
    ket_qua.sort(key=lambda x: x["diem_khop_ten"], reverse=True)
    return ket_qua


# ─────────────────────────────────────────────────────────────────────────────
# Hàm tổng hợp — Retrieval chính
# ─────────────────────────────────────────────────────────────────────────────

def truy_xuat_context(cau_hoi: str, top_k: int = 8) -> list[dict]:
    """
    Tầng Retrieval RAG: kết hợp Embedding + Fuzzy match → context tối ưu.

    Luồng xử lý:
    1. Embedding search → list A (tìm theo ngữ nghĩa/chủ đề)
    2. Fuzzy match tên riêng → list B (khớp tên sách/tác giả)
    3. Gộp A + B, loại trùng theo ma_sach, cộng gộp thông tin
    4. Sắp xếp: ưu tiên khớp cả 2 nguồn, rồi theo điểm cao nhất
    5. Giới hạn top_k kết quả cuối cùng

    Tham số:
        cau_hoi (str): Câu hỏi tra cứu của độc giả.
        top_k (int):   Số kết quả tối đa trả về (mặc định 8).

    Trả về:
        list[dict]: Danh sách sách đã lọc, mỗi phần tử gồm:
            ma_sach, ten_sach, tac_gia, the_loai, con_hang, tom_tat,
            diem_tuong_dong (float, 0–1, chỉ có nếu khớp embedding),
            diem_khop_ten (int, 0–100, chỉ có nếu khớp fuzzy),
            diem_lien_quan (float, điểm tổng hợp để sắp xếp),
            nguon_khop (list[str]: ["ngu_nghia"] | ["ten_rieng"] | cả 2)
    """
    if not cau_hoi or not isinstance(cau_hoi, str) or not cau_hoi.strip():
        return []

    vs = VectorStore()

    # ── Bước 1: Embedding search ──────────────────────────────────────────────
    list_a_raw = vs.tim_kiem_ngu_nghia(cau_hoi.strip(), top_k=10)

    # Chuyển thành dict dễ gộp: key = ma_sach
    map_ket_qua: dict[str, dict] = {}

    for item in list_a_raw:
        ma = item["ma_sach"]
        map_ket_qua[ma] = {
            "ma_sach": ma,
            "ten_sach": item["ten_sach"],
            "tac_gia": item["tac_gia"],
            "the_loai": item["the_loai"],
            "con_hang": item["con_hang"],
            "tom_tat": item["tom_tat"],
            "diem_tuong_dong": item["diem_tuong_dong"],
            "diem_khop_ten": 0,
            "nguon_khop": ["ngu_nghia"],
        }

    # ── Bước 2: Fuzzy match tên riêng ─────────────────────────────────────────
    tat_ca_sach = _lay_tat_ca_sach_tu_vs(vs)
    list_b_raw = _fuzzy_match_ten(cau_hoi.strip(), tat_ca_sach)

    for item in list_b_raw:
        ma = item["ma_sach"]
        if ma in map_ket_qua:
            # ── Sách xuất hiện ở CẢ 2 nguồn → gộp thông tin ──────────────
            map_ket_qua[ma]["diem_khop_ten"] = item["diem_khop_ten"]
            if "ten_rieng" not in map_ket_qua[ma]["nguon_khop"]:
                map_ket_qua[ma]["nguon_khop"].append("ten_rieng")
        else:
            # ── Sách chỉ khớp fuzzy, không có trong embedding results ────
            map_ket_qua[ma] = {
                "ma_sach": ma,
                "ten_sach": item["ten_sach"],
                "tac_gia": item["tac_gia"],
                "the_loai": item["the_loai"],
                "con_hang": item["con_hang"],
                "tom_tat": item["tom_tat"],
                "diem_tuong_dong": 0.0,
                "diem_khop_ten": item["diem_khop_ten"],
                "nguon_khop": ["ten_rieng"],
            }

    # ── Bước 3: Không có kết quả → trả về rỗng ────────────────────────────────
    if not map_ket_qua:
        _logger.info(f"[RAG_RETRIEVER] '{cau_hoi[:50]}' → 0 kết quả")
        return []

    # ── Bước 4: Tính diem_lien_quan và sắp xếp ────────────────────────────────
    # Công thức: ưu tiên khớp 2 nguồn (bonus +0.3), rồi theo embedding score
    # Fuzzy score 0–100 → chuẩn hóa /100 để cùng scale với embedding (0–1)
    danh_sach = list(map_ket_qua.values())

    for item in danh_sach:
        co_ca_hai = len(item["nguon_khop"]) == 2
        bonus = 0.3 if co_ca_hai else 0.0
        diem_fuzzy_chuan = item["diem_khop_ten"] / 100.0
        # Lấy max của 2 điểm rồi cộng bonus khớp 2 nguồn
        item["diem_lien_quan"] = round(
            max(item["diem_tuong_dong"], diem_fuzzy_chuan) + bonus, 4
        )

    # Sắp xếp: khớp cả 2 nguồn lên đầu, rồi theo điểm giảm dần
    danh_sach.sort(
        key=lambda x: (len(x["nguon_khop"]) == 2, x["diem_lien_quan"]),
        reverse=True,
    )

    # ── Bước 5: Giới hạn top_k ────────────────────────────────────────────────
    ket_qua_cuoi = danh_sach[:top_k]

    _logger.info(
        f"[RAG_RETRIEVER] '{cau_hoi[:50]}' → "
        f"{len(ket_qua_cuoi)} kết quả "
        f"(embedding: {len(list_a_raw)}, fuzzy: {len(list_b_raw)}, "
        f"khớp cả 2: {sum(1 for x in ket_qua_cuoi if len(x['nguon_khop'])==2)})"
    )

    return ket_qua_cuoi
