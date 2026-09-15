"""
test_chan_lac_de.py — Kiểm thử 2 lớp bảo vệ chống câu hỏi lạc đề và phân nhánh retrieval.

Kiểm thử bắt buộc:
1. 3 câu hỏi hoàn toàn lạc đề:
   - "Ai là chủ tịch nước hiện tại?"
   - "Cho tôi công thức nấu phở"
   - "1 với 1 bằng mấy?"
   -> Xác nhận bị chặn ở bước similarity threshold (KHÔNG gọi LLM, điểm < 0.15),
      in ra log xác nhận "đã chặn ở tầng retrieval, không tốn API call".
2. 1 câu hỏi thực sự về sách nhưng thư viện không có:
   - "sách Harry Potter"
   -> Xác nhận KHÔNG bị nhầm sang "lạc đề hoàn toàn" mà đi đúng nhánh "không có sách phù hợp"
      (điểm trong [0.15, 0.35], KHÔNG gọi LLM).
3. 1 câu hỏi về sách CÓ trong thư viện:
   - "Carnegie"
   -> Xác nhận context >= 0.35, đi tiếp vào luồng LLM bình thường.
"""

import json
import logging
import sys
from pathlib import Path

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

APP_ROOT = Path(__file__).resolve().parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from chatbotAI.rag_retriever import truy_xuat_context
from chatbotAI.chatbot_service import tra_cuu_sach

# Cấu hình log ra console
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def sep(title: str):
    print("\n" + "═" * 70)
    print(f"  {title}")
    print("─" * 70)

print("=" * 70)
print("  KIỂM THỬ 2 LỚP BẢO VỆ CHỐNG CÂU HỎI LẠC ĐỀ")
print("=" * 70)

ket_qua_kiem_thu = []

# ── TEST 1, 2, 3: CÂU HỎI HOÀN TOÀN LẠC ĐỀ ─────────────────────────────────
cau_hoi_lac_de = [
    ("Ai là chủ tịch nước hiện tại?", "Chính trị / Thời sự / Lãnh đạo"),
    ("Cho tôi công thức nấu phở", "Nấu ăn / Ẩm thực đời sống"),
    ("1 với 1 bằng mấy?", "Toán đố cơ bản / Chat nhảm / Spam"),
]

for idx, (q, chu_de) in enumerate(cau_hoi_lac_de, 1):
    sep(f"TEST {idx}: [LẠC ĐỀ HOÀN TOÀN] \"{q}\" ({chu_de})")
    context = truy_xuat_context(q)
    diem_cao_nhat = getattr(context, "diem_cao_nhat_truoc_loc", 0.0)
    print(f"  📋 Số sách đạt ngưỡng context (>= 0.35): {len(context)}")
    print(f"  🎯 Điểm cao nhất trước khi lọc: {diem_cao_nhat:.4f}")
    
    res = tra_cuu_sach(q)
    print(f"  💬 Thông báo trả về: \"{res.get('thong_bao')}\"")
    
    # Kiểm tra điều kiện PASS
    pass_context = len(context) == 0
    pass_score = diem_cao_nhat < 0.15
    pass_msg = "Tôi chỉ hỗ trợ tra cứu sách trong thư viện" in res.get("thong_bao", "")
    
    is_ok = pass_context and pass_score and pass_msg
    trang_thai = "✅ PASS" if is_ok else "❌ FAIL"
    print(f"  Kết luận: {trang_thai} (Chặn tầng retrieval: {pass_context}, Điểm < 0.15: {pass_score}, Thông báo đúng: {pass_msg})")
    
    ket_qua_kiem_thu.append({
        "stt": idx,
        "cau_hoi": q,
        "chu_de": chu_de,
        "nhanh_ky_vong": "Lạc đề hoàn toàn (< 0.15)",
        "diem_cao_nhat": diem_cao_nhat,
        "context_len": len(context),
        "thong_bao": res.get("thong_bao"),
        "ket_qua": trang_thai,
    })

# ── TEST 4: HỎI VỀ SÁCH NHƯNG THƯ VIỆN CHƯA CÓ ──────────────────────────────
sep("TEST 4: [CÂU HỎI VỀ SÁCH - KHÔNG CÓ TRONG THƯ VIỆN] \"sách Harry Potter\"")
q4 = "sách Harry Potter"
context4 = truy_xuat_context(q4)
diem_cao_nhat_4 = getattr(context4, "diem_cao_nhat_truoc_loc", 0.0)
print(f"  📋 Số sách đạt ngưỡng context (>= 0.35): {len(context4)}")
print(f"  🎯 Điểm cao nhất trước khi lọc: {diem_cao_nhat_4:.4f}")

res4 = tra_cuu_sach(q4)
print(f"  💬 Thông báo trả về: \"{res4.get('thong_bao')}\"")

pass_context_4 = len(context4) == 0
pass_score_4 = 0.15 <= diem_cao_nhat_4 < 0.35
pass_msg_4 = res4.get("thong_bao") == "Không tìm thấy sách phù hợp trong thư viện."

is_ok_4 = pass_context_4 and pass_score_4 and pass_msg_4
trang_thai_4 = "✅ PASS" if is_ok_4 else "❌ FAIL"
print(f"  Kết luận: {trang_thai_4} (Chặn tầng retrieval: {pass_context_4}, Điểm trong [0.15, 0.35]: {pass_score_4}, Thông báo đúng: {pass_msg_4})")

ket_qua_kiem_thu.append({
    "stt": 4,
    "cau_hoi": q4,
    "chu_de": "Hỏi sách ngoài thư viện",
    "nhanh_ky_vong": "Không có sách phù hợp [0.15 - 0.35]",
    "diem_cao_nhat": diem_cao_nhat_4,
    "context_len": len(context4),
    "thong_bao": res4.get("thong_bao"),
    "ket_qua": trang_thai_4,
})

# ── TEST 5 (Bổ sung): SÁCH CÓ TRONG THƯ VIỆN (đảm bảo không bị ảnh hưởng) ────
sep("TEST 5: [KIỂM TRA ĐỐI CHỨNG] Sách có trong thư viện: \"Carnegie\"")
q5 = "Carnegie"
context5 = truy_xuat_context(q5)
diem_cao_nhat_5 = getattr(context5, "diem_cao_nhat_truoc_loc", 0.0)
print(f"  📋 Số sách đạt ngưỡng context (>= 0.35): {len(context5)}")
print(f"  🎯 Điểm cao nhất: {diem_cao_nhat_5:.4f}")
if context5:
    print(f"  Top 1 sách: {context5[0]['ten_sach']} — {context5[0]['tac_gia']} (điểm: {context5[0]['diem_lien_quan']})")

pass_5 = len(context5) > 0 and diem_cao_nhat_5 >= 0.35
print(f"  Kết luận: {'✅ PASS (Context hợp lệ, sẵn sàng chuyển LLM)' if pass_5 else '❌ FAIL'}")

print("\n" + "═" * 70)
print("  TỔNG KẾT KIỂM THỬ HOÀN THÀNH")
print("═" * 70)
print(json.dumps(ket_qua_kiem_thu, ensure_ascii=False, indent=2))
