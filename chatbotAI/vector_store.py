"""
vector_store.py — Lớp quản lý Vector Store cho hệ thống RAG tra cứu sách.

Dùng ChromaDB (PersistentClient) để lưu embedding sách và tìm kiếm ngữ nghĩa.
Kết hợp với embedding_client.py (sentence-transformers, local, offline).

Collection: "sach_thu_vien"
  - id:        ma_sach (string duy nhất)
  - embedding: vector 384 chiều từ paraphrase-multilingual-MiniLM-L12-v2
  - document:  tom_tat (nội dung dùng để embedding)
  - metadata:  {ten_sach, tac_gia, the_loai, con_hang}

Distance metric: cosine — phù hợp so sánh ngữ nghĩa văn bản.
Dữ liệu lưu tại: chatbotAI/vector_db/ (persistent, không mất khi restart).
"""

import logging
import sys
import time
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

# ─── Thêm thư mục chatbotAI vào sys.path để import nội bộ ───────────────────
CURRENT_DIR = Path(__file__).resolve().parent
APP_DIR = CURRENT_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

# ─── Import embedding_client (local, offline) ────────────────────────────────
from chatbotAI.embedding_client import get_embedding, get_embeddings_batch  # noqa: E402

# ─── Cấu hình logging (dùng chung logs/ai_calls.log) ────────────────────────
LOGS_DIR = CURRENT_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

_logger = logging.getLogger("ai_calls")
_logger.setLevel(logging.INFO)
if not _logger.handlers:
    _fh = logging.FileHandler(LOGS_DIR / "ai_calls.log", encoding="utf-8")
    _fh.setFormatter(logging.Formatter(
        "[%(asctime)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    _logger.addHandler(_fh)

# ─── Hằng số ─────────────────────────────────────────────────────────────────
VECTOR_DB_DIR = CURRENT_DIR / "vector_db"
COLLECTION_NAME = "sach_thu_vien"


# ═════════════════════════════════════════════════════════════════════════════
# Lớp VectorStore
# ═════════════════════════════════════════════════════════════════════════════

class VectorStore:
    """
    Lớp quản lý ChromaDB Vector Store cho hệ thống RAG tra cứu sách.

    Khởi tạo PersistentClient → dữ liệu lưu tại chatbotAI/vector_db/
    và tồn tại qua các lần restart chương trình.

    Sử dụng:
        vs = VectorStore()
        vs.them_sach("S001", "Python cơ bản", "Tác giả", "Tóm tắt...", "CNTT", True)
        results = vs.tim_kiem_ngu_nghia("học lập trình")
    """

    def __init__(self):
        """
        Khởi tạo ChromaDB PersistentClient và lấy/tạo collection "sach_thu_vien".
        Collection được cấu hình dùng cosine distance để đo độ tương đồng ngữ nghĩa.
        """
        try:
            import chromadb
            from chromadb.config import Settings

            # Tạo thư mục lưu DB nếu chưa có
            VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

            # PersistentClient: tự động lưu và đọc từ disk
            self._client = chromadb.PersistentClient(
                path=str(VECTOR_DB_DIR),
                settings=Settings(anonymized_telemetry=False),
            )

            # Lấy hoặc tạo collection với cosine distance
            self._collection = self._client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},  # Cosine similarity
            )

            so_luong = self._collection.count()
            _logger.info(
                f"[VECTORSTORE] [INIT] Collection '{COLLECTION_NAME}' sẵn sàng. "
                f"Hiện có {so_luong} sách đã index. DB: {VECTOR_DB_DIR}"
            )

        except ImportError as e:
            raise ImportError(
                "Thư viện 'chromadb' chưa được cài đặt.\n"
                "Hãy chạy: pip install chromadb"
            ) from e
        except Exception as e:
            _logger.error(f"[VECTORSTORE] [INIT_ERROR] Không thể khởi tạo ChromaDB: {e}")
            raise

    # ─────────────────────────────────────────────────────────────────────────
    # Phương thức 1: Thêm / cập nhật sách (upsert)
    # ─────────────────────────────────────────────────────────────────────────

    def them_sach(
        self,
        ma_sach: str,
        ten_sach: str,
        tac_gia: str,
        tom_tat: str,
        the_loai: str,
        con_hang: bool,
    ) -> None:
        """
        Thêm hoặc CẬP NHẬT (upsert) 1 cuốn sách vào vector store.

        Logic embedding:
          - Dùng tom_tat để embedding nếu tom_tat không rỗng
          - Nếu tom_tat rỗng → embedding ten_sach thay thế
          - Nếu cả hai rỗng → bỏ qua và ghi log warning

        Tham số:
            ma_sach (str):  Mã định danh duy nhất của sách (PK từ CSDL chính).
            ten_sach (str): Tên sách.
            tac_gia (str):  Tên tác giả.
            tom_tat (str):  Tóm tắt nội dung sách (văn bản dùng để embedding).
            the_loai (str): Thể loại sách.
            con_hang (bool): True nếu còn sách trên kệ, False nếu hết.
        """
        if not ma_sach or not isinstance(ma_sach, str):
            _logger.warning("[VECTORSTORE] [SKIP] ma_sach rỗng hoặc không hợp lệ.")
            return

        start = time.time()

        # Chuẩn hóa văn bản embedding kết hợp Tên sách, Tác giả, Thể loại và Tóm tắt nội dung
        phan_tu = []
        if ten_sach and ten_sach.strip():
            phan_tu.append(f"Tên sách: {ten_sach.strip()}")
        if tac_gia and tac_gia.strip():
            phan_tu.append(f"Tác giả: {tac_gia.strip()}")
        if the_loai and the_loai.strip():
            phan_tu.append(f"Thể loại: {the_loai.strip()}")
        if tom_tat and tom_tat.strip():
            phan_tu.append(f"Nội dung tóm tắt: {tom_tat.strip()}")

        van_ban_embed = ". ".join(phan_tu) if phan_tu else None

        if van_ban_embed is None:
            _logger.warning(
                f"[VECTORSTORE] [SKIP] Sách '{ma_sach}': cả tom_tat và ten_sach đều rỗng."
            )
            return

        vector = get_embedding(van_ban_embed)
        if vector is None:
            _logger.error(
                f"[VECTORSTORE] [SKIP] Sách '{ma_sach}': không tạo được embedding."
            )
            return

        # Upsert vào ChromaDB (thêm mới hoặc cập nhật nếu id đã tồn tại)
        self._collection.upsert(
            ids=[ma_sach],
            embeddings=[vector],
            documents=[tom_tat or ten_sach],
            metadatas=[{
                "ten_sach": ten_sach or "",
                "tac_gia": tac_gia or "",
                "the_loai": the_loai or "",
                "con_hang": str(con_hang),  # ChromaDB metadata chỉ nhận str/int/float
                "tom_tat": tom_tat or "",
            }],
        )

        elapsed_ms = int((time.time() - start) * 1000)
        _logger.info(
            f"[VECTORSTORE] [UPSERT] '{ma_sach}' — '{ten_sach[:40]}' "
            f"[{elapsed_ms}ms] | embed từ: {'tom_tat' if tom_tat and tom_tat.strip() else 'ten_sach'}"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Phương thức 2: Tìm kiếm ngữ nghĩa
    # ─────────────────────────────────────────────────────────────────────────

    def tim_kiem_ngu_nghia(
        self,
        cau_hoi: str,
        top_k: int = 10,
    ) -> list[dict]:
        """
        Tìm kiếm sách theo ngữ nghĩa dùng cosine similarity.

        Luồng:
          1. Vector hóa cau_hoi → query_vector
          2. ChromaDB tìm top_k sách có embedding gần nhất (cosine)
          3. Chuyển đổi kết quả sang list[dict] thân thiện

        Tham số:
            cau_hoi (str): Câu hỏi hoặc từ khóa tìm kiếm của độc giả.
            top_k (int):   Số kết quả tối đa trả về (mặc định 10).

        Trả về:
            list[dict]: Danh sách sách khớp, sắp xếp theo độ tương đồng giảm dần.
              Mỗi phần tử gồm: ma_sach, ten_sach, tac_gia, the_loai,
                               con_hang, tom_tat, diem_tuong_dong

        Ghi chú về diem_tuong_dong:
            ChromaDB với cosine space trả về "distance" (0=giống hệt, 2=hoàn toàn khác).
            Công thức: diem_tuong_dong = 1 - (distance / 2) → kết quả trong [0, 1]
            Điểm càng gần 1.0 → càng liên quan.
        """
        if not cau_hoi or not isinstance(cau_hoi, str) or not cau_hoi.strip():
            _logger.warning("[VECTORSTORE] [SEARCH] Câu hỏi rỗng, bỏ qua tìm kiếm.")
            return []

        so_luong = self._collection.count()
        if so_luong == 0:
            _logger.warning("[VECTORSTORE] [SEARCH] Collection rỗng, chưa có sách nào được index.")
            return []

        # Giới hạn top_k không vượt quá số sách hiện có
        top_k = min(top_k, so_luong)

        start = time.time()
        query_vector = get_embedding(cau_hoi.strip())
        if query_vector is None:
            _logger.error("[VECTORSTORE] [SEARCH] Không tạo được embedding cho câu hỏi.")
            return []

        # Query ChromaDB
        ket_qua_chroma = self._collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        elapsed_ms = int((time.time() - start) * 1000)

        # Parse kết quả
        danh_sach_ket_qua: list[dict] = []
        ids = ket_qua_chroma.get("ids", [[]])[0]
        documents = ket_qua_chroma.get("documents", [[]])[0]
        metadatas = ket_qua_chroma.get("metadatas", [[]])[0]
        distances = ket_qua_chroma.get("distances", [[]])[0]

        for ma_sach, doc, meta, dist in zip(ids, documents, metadatas, distances):
            # Cosine space: distance ∈ [0, 2] → chuyển sang similarity ∈ [0, 1]
            diem_tuong_dong = round(1.0 - dist / 2.0, 4)
            con_hang_val = str(meta.get("con_hang", "True")).lower() == "true"

            danh_sach_ket_qua.append({
                "ma_sach": ma_sach,
                "ten_sach": meta.get("ten_sach", ""),
                "tac_gia": meta.get("tac_gia", ""),
                "the_loai": meta.get("the_loai", ""),
                "con_hang": con_hang_val,
                "tom_tat": doc,
                "diem_tuong_dong": diem_tuong_dong,
            })

        _logger.info(
            f"[VECTORSTORE] [SEARCH] '{cau_hoi[:50]}' → {len(danh_sach_ket_qua)} kết quả "
            f"[{elapsed_ms}ms] | Top-1: {danh_sach_ket_qua[0]['ten_sach'][:30] if danh_sach_ket_qua else 'N/A'} "
            f"({danh_sach_ket_qua[0]['diem_tuong_dong'] if danh_sach_ket_qua else 'N/A'})"
        )

        return danh_sach_ket_qua

    # ─────────────────────────────────────────────────────────────────────────
    # Phương thức 3: Xóa sách khỏi vector store
    # ─────────────────────────────────────────────────────────────────────────

    def xoa_sach(self, ma_sach: str) -> None:
        """
        Xóa 1 sách khỏi vector store theo ma_sach.
        Dùng khi sách bị xóa khỏi CSDL chính (đồng bộ hóa).

        Tham số:
            ma_sach (str): Mã định danh sách cần xóa.
        """
        if not ma_sach:
            _logger.warning("[VECTORSTORE] [DELETE] ma_sach rỗng, bỏ qua.")
            return
        try:
            self._collection.delete(ids=[ma_sach])
            _logger.info(f"[VECTORSTORE] [DELETE] Đã xóa sách '{ma_sach}'.")
        except Exception as e:
            _logger.error(f"[VECTORSTORE] [DELETE_ERROR] Không thể xóa '{ma_sach}': {e}")

    # ─────────────────────────────────────────────────────────────────────────
    # Phương thức 4: Đếm số lượng sách đã index
    # ─────────────────────────────────────────────────────────────────────────

    def dem_so_luong(self) -> int:
        """
        Đếm tổng số sách đã được index trong vector store.
        Dùng để kiểm tra nhanh sau khi chạy đồng bộ.

        Trả về:
            int: Tổng số document trong collection.
        """
        count = self._collection.count()
        _logger.info(f"[VECTORSTORE] [COUNT] Tổng số sách đã index: {count}")
        return count
