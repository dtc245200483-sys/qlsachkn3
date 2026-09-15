"""
test_rag_full.py — Kiểm thử luồng RAG đầy đủ với 3 câu hỏi.

Test 1: Câu hỏi ngữ nghĩa (không trùng chữ với sách nào)
Test 2: Gõ đúng tên tác giả → fuzzy match
Test 3: Chủ đề chắc chắn không có sách phù hợp
"""

import json
import sys
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

APP_ROOT = Path(__file__).resolve().parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from chatbotAI.rag_retriever import truy_xuat_context
from chatbotAI.chatbot_service import tra_cuu_sach


def in_context(context: list, title: str):
    print(f"\n  📋 Context tìm được ({len(context)} sách):")
    for i, s in enumerate(context, 1):
        nguon = "+".join(s.get("nguon_khop", []))
        diem = s.get("diem_lien_quan", 0)
        print(f"     [{i}] ({nguon}, {diem:.3f}) {s['ten_sach']} — {s['tac_gia']}")


def in_ket_qua(ket_qua: dict):
    if "loi" in ket_qua:
        print(f"\n  ⚠️  Lỗi hệ thống: {ket_qua['loi']}")
        return
    ds = ket_qua.get("ket_qua", [])
    thong_bao = ket_qua.get("thong_bao", "")
    print(f"\n  🤖 Câu trả lời LLM ({len(ds)} sách gợi ý):")
    if thong_bao:
        print(f"     Thông báo: {thong_bao}")
    for i, s in enumerate(ds, 1):
        con_hang = "Còn hàng" if s.get("con_hang") else "Hết hàng"
        print(f"     [{i}] {s['ten_sach']} — {s['tac_gia']} ({con_hang})")
        print(f"          Lý do: {s.get('ly_do_goi_y', '')}")


def sep(n: int, title: str):
    print(f"\n{'═' * 60}")
    print(f"  TEST {n}: {title}")
    print(f"{'─' * 60}")


print("=" * 60)
print("  KIỂM THỬ LUỒNG RAG HOÀN CHỈNH — 3 CÂU HỎI")
print("=" * 60)

# ── TEST 1: Câu hỏi ngữ nghĩa ─────────────────────────────────────────────
sep(1, "Ngữ nghĩa — không trùng chữ với sách nào")
cau_hoi_1 = "sách dạy làm bếp và chế biến thức ăn"
print(f"\n  Câu hỏi: \"{cau_hoi_1}\"")
print(f"  (Từ 'làm bếp', 'chế biến' không xuất hiện trong tên/tóm tắt sách)")
context_1 = truy_xuat_context(cau_hoi_1)
in_context(context_1, "TEST 1")
ket_qua_1 = tra_cuu_sach(cau_hoi_1)
in_ket_qua(ket_qua_1)

# ── TEST 2: Gõ tên tác giả (fuzzy match) ─────────────────────────────────
sep(2, "Tên riêng — gõ đúng một phần tên tác giả")
cau_hoi_2 = "Carnegie"
print(f"\n  Câu hỏi: \"{cau_hoi_2}\"")
print(f"  (Tác giả 'Dale Carnegie' có trong dữ liệu — test fuzzy match tên)")
context_2 = truy_xuat_context(cau_hoi_2)
in_context(context_2, "TEST 2")
ket_qua_2 = tra_cuu_sach(cau_hoi_2)
in_ket_qua(ket_qua_2)

# ── TEST 3: Chủ đề không có sách phù hợp ────────────────────────────────
sep(3, "Không có sách — chủ đề ngoài phạm vi thư viện")
cau_hoi_3 = "sách dạy lái xe hơi và thi bằng lái"
print(f"\n  Câu hỏi: \"{cau_hoi_3}\"")
print(f"  (Không có sách nào về lái xe trong dữ liệu)")
context_3 = truy_xuat_context(cau_hoi_3)
in_context(context_3, "TEST 3")
ket_qua_3 = tra_cuu_sach(cau_hoi_3)
in_ket_qua(ket_qua_3)

print(f"\n{'═' * 60}")
print("  Kiểm thử hoàn thành!")
print(f"{'═' * 60}\n")

# Export kết quả để ghi vào minh chứng
_export = {
    "test1": {"cau_hoi": cau_hoi_1, "context_so_luong": len(context_1), "ket_qua": ket_qua_1},
    "test2": {"cau_hoi": cau_hoi_2, "context_so_luong": len(context_2), "ket_qua": ket_qua_2},
    "test3": {"cau_hoi": cau_hoi_3, "context_so_luong": len(context_3), "ket_qua": ket_qua_3},
}
print("\n[RAW JSON kết quả — dùng để ghi minh chứng]")
print(json.dumps(_export, ensure_ascii=False, indent=2))
