# Minh Chứng Kỹ Thuật: Vector Store & Embedding cho Hệ Thống RAG

## Prompt đã dùng
```text
Bạn là kỹ sư AI. Dự án nằm tại: D:\ung dung tri tue nhan tao\app

Hãy xây dựng lớp Vector Store cho hệ thống RAG tra cứu sách, dùng 
ChromaDB để lưu trữ và tìm kiếm embedding, kết hợp với module 
embedding_client.py đã có tại 
D:\ung dung tri tue nhan tao\app\chatbotAI\embedding_client.py

VỊ TRÍ FILE CẦN TẠO:
- D:\ung dung tri tue nhan tao\app\chatbotAI\vector_store.py
- D:\ung dung tri tue nhan tao\app\chatbotAI\index_sach.py
- D:\ung dung tri tue nhan tao\app\chatbotAI\vector_db\

[... phần còn lại xem nguyên văn prompt đã gửi cho AI ...]
```

---

## Phản hồi/Kết quả của AI

### 1. Danh sách file đã tạo

| File | Mô tả |
|------|-------|
| `chatbotAI/vector_store.py` | Lớp `VectorStore` — ChromaDB PersistentClient, cosine distance |
| `chatbotAI/index_sach.py` | Script đồng bộ batch + demo dữ liệu giả lập 10 sách |
| `chatbotAI/vector_db/` | Thư mục lưu dữ liệu ChromaDB persistent (tự tạo khi chạy) |

---

### 2. Cấu trúc lớp VectorStore

```python
class VectorStore:
    def __init__(self):
        """PersistentClient → lưu vào chatbotAI/vector_db/ (không mất khi restart)"""
        # Collection: "sach_thu_vien", metadata={"hnsw:space": "cosine"}

    def them_sach(ma_sach, ten_sach, tac_gia, tom_tat, the_loai, con_hang) -> None:
        """Upsert (thêm mới hoặc cập nhật) 1 sách. Embed tom_tat, fallback ten_sach."""

    def tim_kiem_ngu_nghia(cau_hoi, top_k=10) -> list[dict]:
        """Query cosine similarity. Trả về diem_tuong_dong = 1 - dist/2 ∈ [0,1]"""

    def xoa_sach(ma_sach) -> None:
        """Xóa 1 sách khi bị xóa khỏi CSDL chính."""

    def dem_so_luong() -> int:
        """Kiểm tra nhanh tổng số sách đã index."""
```

**ChromaDB metadata:** Lưu `ten_sach`, `tac_gia`, `the_loai`, `con_hang` (dưới dạng string vì ChromaDB không nhận bool). Trường `con_hang` được chuyển đổi lại khi đọc.

---

### 3. Kết quả kiểm thử Phần 3 — RAG Semantic Search thực tế

**Môi trường:** 10 sách giả lập đã index | ChromaDB 1.5.9 | paraphrase-multilingual-MiniLM-L12-v2

> **Lưu ý quan trọng:** Tất cả 4 câu hỏi test dưới đây dùng từ KHÔNG TRÙNG chữ với tên sách hay tóm tắt, chứng minh hệ thống tìm theo nghĩa chứ không phải khớp ký tự.

---

#### 📌 Test 1: `"muốn học cách viết code cho người chưa biết gì"`
*Dùng "viết code" thay vì "lập trình", "chưa biết gì" thay vì "cơ bản"*

| # | Điểm tương đồng | Tên sách | Tác giả | Thể loại | Tình trạng |
|---|----------------|----------|---------|---------|-----------|
| 1 | **0.7790** | Lập trình Python từ cơ bản đến nâng cao | Nguyễn Thành Nam | CNTT | Còn hàng ✅ |
| 2 | 0.6594 | Trí tuệ nhân tạo: Tiếp cận hiện đại | Stuart Russell | CNTT | Còn hàng |
| 3 | 0.6297 | Đắc nhân tâm | Dale Carnegie | Kỹ năng sống | Còn hàng |

**✅ Kết luận:** Dù hỏi "viết code" + "chưa biết gì", hệ thống tìm đúng sách lập trình Python dành cho người mới.

---

#### 📌 Test 2: `"sách giúp tôi kiếm tiền và quản lý túi tiền tốt hơn"`
*Dùng "túi tiền" thay vì "tài chính", "kiếm tiền" thay vì "làm giàu"*

| # | Điểm tương đồng | Tên sách | Tác giả | Thể loại | Tình trạng |
|---|----------------|----------|---------|---------|-----------|
| 1 | **0.7761** | Nghĩ giàu làm giàu | Napoleon Hill | Kinh tế | Còn hàng ✅ |
| 2 | 0.7172 | Cha giàu cha nghèo | Robert T. Kiyosaki | Kinh tế | Còn hàng ✅ |
| 3 | 0.6427 | Tắt đèn | Ngô Tất Tố | Văn học | Còn hàng |

**✅ Kết luận:** Dù hỏi "túi tiền" + "kiếm tiền", hệ thống tìm đúng 2 cuốn sách tài chính cá nhân liên quan nhất.

---

#### 📌 Test 3: `"làm sao để chinh phục lòng người và được mọi người yêu quý"`
*Dùng "chinh phục lòng người" thay vì "giao tiếp", "đắc nhân tâm"*

| # | Điểm tương đồng | Tên sách | Tác giả | Thể loại | Tình trạng |
|---|----------------|----------|---------|---------|-----------|
| 1 | **0.7446** | Đắc nhân tâm | Dale Carnegie | Kỹ năng sống | Còn hàng ✅ |
| 2 | 0.6815 | 7 Thói quen của người hiệu quả | Stephen R. Covey | Kỹ năng sống | **Hết hàng** |
| 3 | 0.6518 | Nghĩ giàu làm giàu | Napoleon Hill | Kinh tế | Còn hàng |

**✅ Kết luận:** Câu hỏi không có từ "đắc nhân tâm" nhưng hệ thống xếp sách này #1 nhờ hiểu ngữ nghĩa.

---

#### 📌 Test 4: `"khám phá vũ trụ và bí ẩn không gian bao la"`
*Dùng "bí ẩn không gian" thay vì "vũ trụ học", "thời gian"*

| # | Điểm tương đồng | Tên sách | Tác giả | Thể loại | Tình trạng |
|---|----------------|----------|---------|---------|-----------|
| 1 | **0.7946** | Lược sử thời gian | Nguyễn Thành Nam | Khoa học | Còn hàng ✅ |
| 2 | 0.6114 | Số đỏ | Vũ Trọng Phụng | Văn học | Còn hàng |
| 3 | 0.6083 | Kiến trúc hệ thống phân tán | Martin Kleppmann | CNTT | Hết hàng |

**✅ Kết luận:** Dù không nhắc tên sách hay từ "thời gian", hệ thống tìm đúng "Lược sử thời gian" với điểm 0.7946.

---

### 4. Log đầu ra thực tế từ ChromaDB

```
════════════════════════════════════════════════════════════
  KẾT QUẢ ĐỒNG BỘ
  ✅ Thành công: 10/10 sách
  📚 Tổng trong DB: 10 sách
  ⏱  Tổng thời gian: 25268ms
  → Batch embedding 10 văn bản trong 23419ms (trung bình 2341ms/cuốn)
════════════════════════════════════════════════════════════

✅ Xác nhận: Đã index 10/10 sách trong ChromaDB.
════════════════════════════════════════════════════════════
  Kiểm thử hoàn thành. RAG Semantic Search hoạt động đúng!
════════════════════════════════════════════════════════════
```

---

## Phần sinh viên đã kiểm tra/chỉnh sửa
(sinh viên tự điền sau khi review code)

---

## Ngày thực hiện
15/09/2026 10:35
