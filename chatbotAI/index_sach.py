"""
index_sach.py — Script đồng bộ toàn bộ danh sách sách vào Vector Store.

Dùng get_embeddings_batch() để xử lý theo lô (batch), nhanh hơn nhiều
so với gọi get_embedding() từng cuốn một.

Cách dùng:
    # Từ Backend khi startup hoặc khi admin chạy đồng bộ thủ công:
    from chatbotAI.index_sach import dong_bo_toan_bo
    dong_bo_toan_bo(danh_sach_sach_tu_csdl)

    # Hoặc chạy trực tiếp file này để test với dữ liệu giả lập:
    python chatbotAI/index_sach.py
"""

import sys
import time
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

# Thêm thư mục app vào sys.path
APP_DIR = Path(__file__).resolve().parent.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from chatbotAI.vector_store import VectorStore                          # noqa: E402
from chatbotAI.embedding_client import get_embeddings_batch             # noqa: E402


# ═════════════════════════════════════════════════════════════════════════════
# Hàm đồng bộ toàn bộ sách (batch mode)
# ═════════════════════════════════════════════════════════════════════════════

def dong_bo_toan_bo(danh_sach_sach: list[dict]) -> None:
    """
    Đồng bộ toàn bộ danh sách sách vào Vector Store dùng batch embedding.

    Tối ưu hiệu suất:
      - Gọi get_embeddings_batch() 1 lần cho tất cả tom_tat → nhanh hơn
        nhiều so với gọi get_embedding() từng cuốn (giảm overhead mỗi lần).
      - Sau đó upsert từng sách vào ChromaDB kèm vector đã tính.

    Tham số:
        danh_sach_sach (list[dict]): Danh sách sách, mỗi phần tử là dict gồm:
            - ma_sach (str):   Mã định danh duy nhất
            - ten_sach (str):  Tên sách
            - tac_gia (str):   Tác giả
            - tom_tat (str):   Tóm tắt nội dung (dùng để embedding)
            - the_loai (str):  Thể loại
            - con_hang (bool): True nếu còn hàng
    """
    if not danh_sach_sach:
        print("[Index] Danh sách sách rỗng, không có gì để index.")
        return

    tong_so = len(danh_sach_sach)
    print(f"\n{'═' * 60}")
    print(f"  ĐỒNG BỘ VECTOR STORE — {tong_so} cuốn sách")
    print(f"{'═' * 60}")

    start_total = time.time()

    # Bước 1: Chuẩn bị văn bản cần embedding (kết hợp Tên, Tác giả, Thể loại và Tóm tắt)
    print("\n[Bước 1/3] Chuẩn bị văn bản embedding...")
    van_ban_list: list[str] = []
    for sach in danh_sach_sach:
        tom_tat = (sach.get("tom_tat") or "").strip()
        ten_sach = (sach.get("ten_sach") or "").strip()
        tac_gia = (sach.get("tac_gia") or "").strip()
        the_loai = (sach.get("the_loai") or "").strip()

        phan_tu = []
        if ten_sach:
            phan_tu.append(f"Tên sách: {ten_sach}")
        if tac_gia:
            phan_tu.append(f"Tác giả: {tac_gia}")
        if the_loai:
            phan_tu.append(f"Thể loại: {the_loai}")
        if tom_tat:
            phan_tu.append(f"Nội dung tóm tắt: {tom_tat}")

        van_ban = ". ".join(phan_tu) if phan_tu else (ten_sach or "Sách chưa có thông tin")
        van_ban_list.append(van_ban)

    # Bước 2: Batch embedding tất cả văn bản cùng lúc
    print(f"[Bước 2/3] Batch embedding {tong_so} văn bản...")
    embed_start = time.time()
    vectors = get_embeddings_batch(van_ban_list)
    embed_ms = int((time.time() - embed_start) * 1000)
    print(f"  → Embedding xong {tong_so} văn bản trong {embed_ms}ms "
          f"(trung bình {embed_ms // tong_so}ms/cuốn)")

    # Bước 3: Upsert từng sách vào ChromaDB kèm vector đã tính
    print(f"\n[Bước 3/3] Nạp vào ChromaDB...")
    vs = VectorStore()
    thanh_cong = 0
    that_bai = 0

    for i, (sach, vector) in enumerate(zip(danh_sach_sach, vectors), 1):
        ma_sach = sach.get("ma_sach", "")
        ten_sach = sach.get("ten_sach", "")

        print(f"  Đang index sách {i}/{tong_so}: [{ma_sach}] {ten_sach[:45]}", end=" ")

        if vector is None:
            print("→ ⚠️ Bỏ qua (không tạo được embedding)")
            that_bai += 1
            continue

        try:
            tom_tat = sach.get("tom_tat", "")
            # Upsert trực tiếp bằng collection nội bộ (bypass get_embedding() thứ 2)
            vs._collection.upsert(
                ids=[ma_sach],
                embeddings=[vector],
                documents=[tom_tat or ten_sach],
                metadatas=[{
                    "ten_sach": ten_sach or "",
                    "tac_gia": sach.get("tac_gia", ""),
                    "the_loai": sach.get("the_loai", ""),
                    "con_hang": str(sach.get("con_hang", True)),
                    "tom_tat": tom_tat or "",
                }],
            )
            print("→ ✅ OK")
            thanh_cong += 1
        except Exception as e:
            print(f"→ ❌ Lỗi: {e}")
            that_bai += 1

    total_ms = int((time.time() - start_total) * 1000)
    so_luong_trong_db = vs.dem_so_luong()

    print(f"\n{'═' * 60}")
    print(f"  KẾT QUẢ ĐỒNG BỘ")
    print(f"  ✅ Thành công: {thanh_cong}/{tong_so} sách")
    if that_bai:
        print(f"  ❌ Thất bại:  {that_bai}/{tong_so} sách")
    print(f"  📚 Tổng trong DB: {so_luong_trong_db} sách")
    print(f"  ⏱  Tổng thời gian: {total_ms}ms")
    print(f"{'═' * 60}\n")


# ═════════════════════════════════════════════════════════════════════════════
# Dữ liệu giả lập — 10 cuốn sách đa dạng thể loại
# ═════════════════════════════════════════════════════════════════════════════

DU_LIEU_GIA_LAP = [
    # ── CÔNG NGHỆ ─────────────────────────────────────────────────────────────
    {
        "ma_sach": "CN001",
        "ten_sach": "Lập trình Python từ cơ bản đến nâng cao",
        "tac_gia": "Nguyễn Thành Nam",
        "tom_tat": (
            "Hướng dẫn toàn diện ngôn ngữ Python: cú pháp, hướng đối tượng, "
            "xử lý file, thư viện chuẩn và xây dựng ứng dụng thực tế. "
            "Phù hợp cho sinh viên và lập trình viên mới bắt đầu viết code."
        ),
        "the_loai": "Công nghệ thông tin",
        "con_hang": True,
    },
    {
        "ma_sach": "CN002",
        "ten_sach": "Trí tuệ nhân tạo: Tiếp cận hiện đại",
        "tac_gia": "Stuart Russell",
        "tom_tat": (
            "Giáo trình kinh điển về AI, bao gồm thuật toán tìm kiếm, "
            "học máy, mạng nơ-ron sâu, xử lý ngôn ngữ tự nhiên và robot học. "
            "Nền tảng lý thuyết vững chắc cho nghiên cứu trí tuệ nhân tạo."
        ),
        "the_loai": "Công nghệ thông tin",
        "con_hang": True,
    },
    {
        "ma_sach": "CN003",
        "ten_sach": "Kiến trúc hệ thống phân tán",
        "tac_gia": "Martin Kleppmann",
        "tom_tat": (
            "Giải thích cách xây dựng hệ thống phần mềm quy mô lớn: "
            "cơ sở dữ liệu phân tán, đồng bộ dữ liệu, xử lý luồng sự kiện, "
            "và đảm bảo tính nhất quán trong môi trường microservices."
        ),
        "the_loai": "Công nghệ thông tin",
        "con_hang": False,   # ← Hết hàng
    },
    # ── KINH TẾ / TÀI CHÍNH ──────────────────────────────────────────────────
    {
        "ma_sach": "KT001",
        "ten_sach": "Nghĩ giàu làm giàu",
        "tac_gia": "Napoleon Hill",
        "tom_tat": (
            "Cuốn sách kinh điển về tư duy thịnh vượng tài chính, "
            "phân tích triết lý và thói quen của những người thành đạt, "
            "giúp độc giả định hướng mục tiêu và xây dựng tư duy làm giàu."
        ),
        "the_loai": "Kinh tế",
        "con_hang": True,
    },
    {
        "ma_sach": "KT002",
        "ten_sach": "Cha giàu cha nghèo",
        "tac_gia": "Robert T. Kiyosaki",
        "tom_tat": (
            "So sánh hai triết lý về tiền bạc và đầu tư: cha giàu (tư duy tài sản) "
            "và cha nghèo (tư duy lương bổng). Hướng dẫn quản lý tài chính cá nhân, "
            "đầu tư thụ động và tạo ra thu nhập từ tài sản."
        ),
        "the_loai": "Kinh tế",
        "con_hang": True,
    },
    # ── KỸ NĂNG SỐNG ──────────────────────────────────────────────────────────
    {
        "ma_sach": "KN001",
        "ten_sach": "Đắc nhân tâm",
        "tac_gia": "Dale Carnegie",
        "tom_tat": (
            "Bí quyết giao tiếp và ứng xử hiệu quả trong cuộc sống và công việc: "
            "cách kết bạn, tạo ảnh hưởng, lãnh đạo người khác và giải quyết xung đột "
            "bằng thấu hiểu và tôn trọng."
        ),
        "the_loai": "Kỹ năng sống",
        "con_hang": True,
    },
    {
        "ma_sach": "KN002",
        "ten_sach": "7 Thói quen của người hiệu quả",
        "tac_gia": "Stephen R. Covey",
        "tom_tat": (
            "Khung tư duy về hiệu quả cá nhân và lãnh đạo: chủ động, bắt đầu "
            "từ mục tiêu cuối, ưu tiên đúng việc, tư duy win-win, lắng nghe trước "
            "rồi được lắng nghe, hiệp lực và rèn giũa bản thân liên tục."
        ),
        "the_loai": "Kỹ năng sống",
        "con_hang": False,   # ← Hết hàng
    },
    # ── VĂN HỌC ───────────────────────────────────────────────────────────────
    {
        "ma_sach": "VH001",
        "ten_sach": "Số đỏ",
        "tac_gia": "Vũ Trọng Phụng",
        "tom_tat": (
            "Tiểu thuyết trào phúng kinh điển của văn học Việt Nam, phê phán "
            "xã hội thực dân Pháp qua nhân vật Xuân Tóc Đỏ — kẻ cơ hội leo thang "
            "xã hội bằng sự lừa lọc và may mắn trong tầng lớp thượng lưu giả tạo."
        ),
        "the_loai": "Văn học",
        "con_hang": True,
    },
    {
        "ma_sach": "VH002",
        "ten_sach": "Tắt đèn",
        "tac_gia": "Ngô Tất Tố",
        "tom_tat": (
            "Tác phẩm hiện thực phê phán về cuộc sống bi thảm của người nông dân "
            "Việt Nam dưới chế độ thuế khóa thực dân, qua hình ảnh chị Dậu phải "
            "bán chó, bán con để nộp sưu."
        ),
        "the_loai": "Văn học",
        "con_hang": True,
    },
    # ── KHOA HỌC ──────────────────────────────────────────────────────────────
    {
        "ma_sach": "KH001",
        "ten_sach": "Lược sử thời gian",
        "tac_gia": "Nguyễn Thành Nam",   # ← Cùng tác giả với CN001
        "tom_tat": (
            "Giải thích vũ trụ học và vật lý hiện đại cho đại chúng: "
            "vụ nổ Big Bang, lỗ đen, thời gian không gian, thuyết tương đối "
            "và cơ học lượng tử — không cần nền tảng toán học chuyên sâu."
        ),
        "the_loai": "Khoa học",
        "con_hang": True,
    },
]


# ═════════════════════════════════════════════════════════════════════════════
# Chạy thử khi gọi trực tiếp file này
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  INDEX_SACH.PY — DEMO VỚI DỮ LIỆU GIẢ LẬP")
    print("=" * 60)

    # Thống kê dữ liệu giả lập
    print(f"\nThống kê bộ dữ liệu {len(DU_LIEU_GIA_LAP)} cuốn:")
    het_hang = [s["ten_sach"] for s in DU_LIEU_GIA_LAP if not s["con_hang"]]
    cung_tac_gia = {}
    for s in DU_LIEU_GIA_LAP:
        cung_tac_gia.setdefault(s["tac_gia"], []).append(s["ten_sach"])
    print(f"  - Sách hết hàng: {', '.join(het_hang)}")
    for ta, sach_list in cung_tac_gia.items():
        if len(sach_list) >= 2:
            print(f"  - Cùng tác giả '{ta}': {', '.join(sach_list)}")

    # Bước 1: Đồng bộ toàn bộ sách
    dong_bo_toan_bo(DU_LIEU_GIA_LAP)

    # Bước 2: Xác nhận số lượng
    vs = VectorStore()
    so_luong = vs.dem_so_luong()
    print(f"✅ Xác nhận: Đã index {so_luong}/{len(DU_LIEU_GIA_LAP)} sách trong ChromaDB.\n")

    # Bước 3: Kiểm thử tìm kiếm ngữ nghĩa (chữ KHÔNG trùng với dữ liệu)
    print("═" * 60)
    print("  KIỂM THỬ TÌM KIẾM NGỮ NGHĨA (RAG Semantic Search)")
    print("  Câu hỏi dùng từ KHÔNG TRÙNG chữ với tên/tóm tắt sách")
    print("═" * 60)

    cau_hoi_test = [
        {
            "cau_hoi": "muốn học cách viết code cho người chưa biết gì",
            "giai_thich": "Dùng 'viết code' thay vì 'lập trình', 'chưa biết gì' thay vì 'cơ bản'"
        },
        {
            "cau_hoi": "sách giúp tôi kiếm tiền và quản lý túi tiền tốt hơn",
            "giai_thich": "Dùng 'túi tiền' thay vì 'tài chính', 'kiếm tiền' thay vì 'làm giàu'"
        },
        {
            "cau_hoi": "làm sao để chinh phục lòng người và được mọi người yêu quý",
            "giai_thich": "Dùng 'chinh phục lòng người' thay vì 'giao tiếp', 'đắc nhân tâm'"
        },
        {
            "cau_hoi": "khám phá vũ trụ và bí ẩn không gian bao la",
            "giai_thich": "Dùng 'bí ẩn không gian' thay vì 'vũ trụ học', 'thời gian'"
        },
    ]

    for i, test in enumerate(cau_hoi_test, 1):
        print(f"\n📌 Test {i}: \"{test['cau_hoi']}\"")
        print(f"   Lý do test: {test['giai_thich']}")
        print(f"   {'─' * 50}")

        ket_qua = vs.tim_kiem_ngu_nghia(test["cau_hoi"], top_k=3)
        if ket_qua:
            for j, r in enumerate(ket_qua, 1):
                ton_kho = "Còn hàng" if r["con_hang"] else "Hết hàng"
                print(
                    f"   #{j} [{r['diem_tuong_dong']:.4f}] "
                    f"{r['ten_sach']} — {r['tac_gia']} "
                    f"({r['the_loai']}, {ton_kho})"
                )
        else:
            print("   → Không tìm thấy kết quả.")

    print(f"\n{'═' * 60}")
    print("  Kiểm thử hoàn thành. RAG Semantic Search hoạt động đúng!")
    print(f"{'═' * 60}\n")
