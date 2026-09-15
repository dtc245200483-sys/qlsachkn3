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
# Nạp danh sách sách chuẩn từ CSDL thực tế (hoặc file catalog kèm tóm tắt)
# ═════════════════════════════════════════════════════════════════════════════

def lay_danh_sach_sach_chuan() -> list[dict]:
    """
    Lấy danh sách sách chuẩn từ CSDL hoặc file books_catalog.json.
    Đảm bảo 100% sách thực tế, không có sách giả lập.
    """
    # 1. Thử đọc trực tiếp từ CSDL
    try:
        from app.database import SessionLocal
        from app.models import Book
        db = SessionLocal()
        books = db.query(Book).all()
        if books:
            return [
                {
                    "ma_sach": b.ma,
                    "ten_sach": b.ten,
                    "tac_gia": b.tacGia or "",
                    "tom_tat": (b.tomTat or "").strip(),
                    "the_loai": b.theLoai or "",
                    "con_hang": (b.soLuong > 0),
                }
                for b in books
            ]
    except Exception:
        pass

    # 2. Fallback đọc từ Backend/scripts/books_catalog.json
    catalog_path = APP_DIR / "Backend" / "scripts" / "books_catalog.json"
    if catalog_path.exists():
        import json
        with open(catalog_path, encoding="utf-8") as f:
            catalog = json.load(f)
            return [
                {
                    "ma_sach": item["ma"],
                    "ten_sach": item["ten"],
                    "tac_gia": item.get("tacGia", ""),
                    "tom_tat": item.get("tomTat", "").strip(),
                    "the_loai": item.get("theLoai", ""),
                    "con_hang": item.get("soLuong", 0) > 0,
                }
                for item in catalog
            ]

    return []


# ═════════════════════════════════════════════════════════════════════════════
# Chạy đồng bộ toàn bộ sách thực tế vào ChromaDB
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  ĐỒNG BỘ VECTOR STORE CHÍNH THỨC TỪ CSDL THỰC TẾ")
    print("=" * 60)

    danh_sach = lay_danh_sach_sach_chuan()
    print(f"\nTìm thấy {len(danh_sach)} cuốn sách thực tế.")

    # Dọn dẹp sách ma / sách thử nghiệm cũ nếu có
    vs = VectorStore()
    current_data = vs._collection.get()
    current_ids = set(current_data["ids"])
    real_ids = {s["ma_sach"] for s in danh_sach}
    ghost_ids = list(current_ids - real_ids)
    if ghost_ids:
        print(f"🧹 Đang xóa {len(ghost_ids)} sách ma/thử nghiệm cũ khỏi ChromaDB: {ghost_ids}")
        vs._collection.delete(ids=ghost_ids)

    # Đồng bộ toàn bộ sách thật
    dong_bo_toan_bo(danh_sach)

    so_luong = vs.dem_so_luong()
    print(f"\n✅ Hoàn tất: Đã index {so_luong} cuốn sách thực tế vào ChromaDB.")
