"""
test_dong_bo_realtime.py — Kịch bản test thủ công 4 bước đồng bộ VS realtime.

Mô phỏng luồng: Thêm sách → Tìm ngay → Xóa sách → Xác nhận biến mất
KHÔNG cần server chạy — gọi trực tiếp hàm VectorStore để xác nhận logic.
"""

import sys
import time
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

APP_ROOT = Path(__file__).resolve().parent.parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from chatbotAI.vector_store import VectorStore

# ─── Dữ liệu sách giả lập để test ──────────────────────────────────────────
SACH_TEST = {
    "ma_sach": "TEST_RT_001",
    "ten_sach": "Bí Quyết Nấu Phở Ngon",
    "tac_gia": "Đầu Bếp Ẩn Danh",
    "tom_tat": (
        "Hướng dẫn chi tiết cách chế biến nước dùng phở chuẩn vị Hà Nội và Sài Gòn: "
        "chọn xương, rang thảo dược, hầm đúng nhiệt độ và bí quyết gia vị bí truyền."
    ),
    "the_loai": "Ẩm thực",
    "con_hang": True,
}

# Câu hỏi ngữ nghĩa — không trùng chữ với tên/tóm tắt sách
CAU_HOI_TIM_KIEM = "cách làm món ăn truyền thống Việt Nam"


def sep(title: str = ""):
    print(f"\n{'═' * 60}")
    if title:
        print(f"  {title}")
        print(f"{'─' * 60}")


def kiem_tra_co_sach(ket_qua: list, ma_sach: str) -> bool:
    return any(r["ma_sach"] == ma_sach for r in ket_qua)


def main():
    print("=" * 60)
    print("  TEST ĐỒNG BỘ VECTOR STORE REALTIME — 4 BƯỚC")
    print("=" * 60)
    print(f"\nSách test: [{SACH_TEST['ma_sach']}] {SACH_TEST['ten_sach']}")
    print(f"Câu hỏi:   \"{CAU_HOI_TIM_KIEM}\"")

    vs = VectorStore()

    # ─── BƯỚC 0: Đảm bảo sách test chưa tồn tại ────────────────────────────
    sep("BƯỚC 0: Dọn dẹp — xóa sách test nếu đã tồn tại từ lần chạy trước")
    vs.xoa_sach(SACH_TEST["ma_sach"])
    print(f"  → Đã xóa (nếu có) sách [{SACH_TEST['ma_sach']}] để bắt đầu test sạch.")

    ket_qua_truoc = vs.tim_kiem_ngu_nghia(CAU_HOI_TIM_KIEM, top_k=5)
    co_truoc = kiem_tra_co_sach(ket_qua_truoc, SACH_TEST["ma_sach"])
    print(f"  → Xác nhận ban đầu: sách TEST_RT_001 {'CÓ' if co_truoc else 'KHÔNG'} trong VS.")

    # ─── BƯỚC 1: Thêm sách ──────────────────────────────────────────────────
    sep("BƯỚC 1: Thêm sách mới (mô phỏng POST /api/books)")
    print(f"  Gọi vs.them_sach('{SACH_TEST['ma_sach']}', '{SACH_TEST['ten_sach']}', ...)")
    t1 = time.time()
    vs.them_sach(**SACH_TEST)
    ms1 = int((time.time() - t1) * 1000)
    print(f"  → ✅ Đã thêm sách [{SACH_TEST['ma_sach']}] vào VS [{ms1}ms]")

    # ─── BƯỚC 2: Tìm ngay sau khi thêm ─────────────────────────────────────
    sep("BƯỚC 2: Tìm kiếm ngay lập tức sau khi thêm")
    print(f"  Câu hỏi: \"{CAU_HOI_TIM_KIEM}\"")
    t2 = time.time()
    ket_qua_sau_them = vs.tim_kiem_ngu_nghia(CAU_HOI_TIM_KIEM, top_k=5)
    ms2 = int((time.time() - t2) * 1000)

    co_sau_them = kiem_tra_co_sach(ket_qua_sau_them, SACH_TEST["ma_sach"])

    print(f"\n  Kết quả tìm kiếm ({ms2}ms) — Top {len(ket_qua_sau_them)} sách:")
    for i, r in enumerate(ket_qua_sau_them, 1):
        dau_sao = "★" if r["ma_sach"] == SACH_TEST["ma_sach"] else " "
        print(f"    {dau_sao} #{i} [{r['diem_tuong_dong']:.4f}] [{r['ma_sach']}] {r['ten_sach']}")

    if co_sau_them:
        diem = next(r["diem_tuong_dong"] for r in ket_qua_sau_them if r["ma_sach"] == SACH_TEST["ma_sach"])
        print(f"\n  ✅ BƯỚC 2 PASS: Tìm thấy sách vừa thêm ngay lập tức (điểm={diem:.4f})")
    else:
        print(f"\n  ❌ BƯỚC 2 FAIL: Không tìm thấy sách vừa thêm!")

    # ─── BƯỚC 3: Xóa sách ───────────────────────────────────────────────────
    sep("BƯỚC 3: Xóa sách (mô phỏng DELETE /api/books/TEST_RT_001)")
    print(f"  Gọi vs.xoa_sach('{SACH_TEST['ma_sach']}')")
    t3 = time.time()
    vs.xoa_sach(SACH_TEST["ma_sach"])
    ms3 = int((time.time() - t3) * 1000)
    print(f"  → ✅ Đã xóa sách [{SACH_TEST['ma_sach']}] khỏi VS [{ms3}ms]")

    # ─── BƯỚC 4: Xác nhận không còn tìm thấy ───────────────────────────────
    sep("BƯỚC 4: Tìm lại sau khi xóa — xác nhận KHÔNG còn thấy")
    print(f"  Câu hỏi: \"{CAU_HOI_TIM_KIEM}\"")
    t4 = time.time()
    ket_qua_sau_xoa = vs.tim_kiem_ngu_nghia(CAU_HOI_TIM_KIEM, top_k=5)
    ms4 = int((time.time() - t4) * 1000)

    co_sau_xoa = kiem_tra_co_sach(ket_qua_sau_xoa, SACH_TEST["ma_sach"])

    print(f"\n  Kết quả tìm kiếm ({ms4}ms) — Top {len(ket_qua_sau_xoa)} sách:")
    for i, r in enumerate(ket_qua_sau_xoa, 1):
        print(f"     #{i} [{r['diem_tuong_dong']:.4f}] [{r['ma_sach']}] {r['ten_sach']}")

    if not co_sau_xoa:
        print(f"\n  ✅ BƯỚC 4 PASS: Sách [{SACH_TEST['ma_sach']}] KHÔNG còn trong kết quả sau khi xóa.")
    else:
        print(f"\n  ❌ BƯỚC 4 FAIL: Sách [{SACH_TEST['ma_sach']}] vẫn xuất hiện sau khi xóa!")

    # ─── Tổng kết ───────────────────────────────────────────────────────────
    sep("TỔNG KẾT")
    all_pass = co_sau_them and not co_sau_xoa
    print(f"  Bước 1 (Thêm vào VS):       ✅ OK")
    print(f"  Bước 2 (Tìm thấy ngay):     {'✅ PASS' if co_sau_them else '❌ FAIL'}")
    print(f"  Bước 3 (Xóa khỏi VS):       ✅ OK")
    print(f"  Bước 4 (Không tìm thấy nx): {'✅ PASS' if not co_sau_xoa else '❌ FAIL'}")
    print(f"\n  {'🎉 TẤT CẢ PASS — Đồng bộ realtime hoạt động đúng!' if all_pass else '⚠️  CÓ BƯỚC FAIL!'}")
    print(f"{'═' * 60}\n")

    return {
        "buoc2_tim_thay": co_sau_them,
        "buoc4_khong_tim_thay": not co_sau_xoa,
        "all_pass": all_pass,
    }


if __name__ == "__main__":
    main()
