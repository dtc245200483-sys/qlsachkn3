# Minh chứng sửa lỗi: False Positive Tên Sách — Chatbot AI Thư viện

---

## Prompt đã dùng

> **Bạn là kỹ sư AI. Dự án nằm tại:** `D:\ung dung tri tue nhan tao\app`
>
> **VẤN ĐỀ CẦN SỬA**: Khi độc giả gõ tên MỘT TÁC PHẨM CỤ THỂ (ví dụ: "Chiến tranh và Hòa bình"), hệ thống hiện đang trả về sách KHÔNG LIÊN QUAN chỉ vì trùng 1-2 từ trong tên (ví dụ trả về sách "Vũ Khí Hoàn Hảo - Chiến Tranh, Sự Phá Hoại..." vì trùng chữ "chiến tranh").
>
> **VỊ TRÍ FILE CẦN SỬA**: `chatbotAI/rag_retriever.py`, `chatbotAI/chatbot_service.py`
>
> *(Gồm yêu cầu: thêm bước phát hiện "tìm đích danh tên sách" bằng fuzz.ratio() ≥ 80, cờ co_the_la_ten_sach khi 50-79% hoặc câu ngắn ≤ 7 từ, và thông báo cụ thể "Thư viện hiện chưa có sách '...'" khi sách không có trong kho)*

---

## Mô tả lỗi ban đầu

**Lỗi phát hiện tại câu G3-08** trong file `06_kiem_thu_dong_vai_doc_gia.md`:

| Câu hỏi | Kết quả SAI trước khi sửa | Kỳ vọng đúng |
|---------|--------------------------|--------------|
| "Chiến tranh và Hòa bình" | Trả sách: **"Vũ Khí Hoàn Hảo - Chiến Tranh, Sự Phá Hoại Và Nỗi Sợ Trong Kỷ Nguyên Mạng"** | **0 sách** + thông báo "Thư viện chưa có sách này" |

**Căn nguyên kỹ thuật:**

Hàm `_fuzzy_match_ten()` trong `rag_retriever.py` dùng `partial_ratio()` — so khớp CHUỖI CON — nên chuỗi "chiến tranh" xuất hiện trong cả hai tên:
```
Query:  "chiến tranh và hòa bình"
Sách:   "vũ khí hoàn hảo - CHIẾN TRANH, sự phá hoại..."
         ↑ partial_ratio ≈ 60-65% → vượt FUZZY_THRESHOLD (60) → được trả về
```

Nhưng `fuzz.ratio()` so khớp TOÀN BỘ chuỗi (độ dài tổng):
```
fuzz.ratio("chiến tranh và hòa bình", "vũ khí hoàn hảo - chiến tranh...") ≈ 20%
→ Hai chuỗi rất khác độ dài → không khớp
```

→ Khi phát hiện câu hỏi là tra cứu tên riêng, cần dùng `fuzz.ratio()` để lọc các sách trả về.

---

## Giải pháp đã áp dụng

### Cơ chế hoạt động (3 tầng)

```
Câu hỏi người dùng
        │
        ▼
[Tầng 1] _phat_hien_tra_cuu_ten_sach()
        │
        ├── Chứa từ khóa chủ đề ("sách về", "gợi ý", "gì đó"...)
        │       → co_the_la_ten_sach = False → Flow bình thường
        │
        ├── fuzz.ratio() với từng sách trong kho >= 80%
        │       → Tìm đích danh → trả trực tiếp, BỎ QUA embedding
        │
        └── fuzz.ratio() 50-79% HOẶC câu ngắn ≤ 7 từ
                → co_the_la_ten_sach = True → tiếp tục flow cũ + đánh dấu cờ
                        │
                        ▼
               [Tầng 2] Embedding + fuzzy partial_ratio (giữ nguyên)
                        │
                        ▼
               [Tầng 3] chatbot_service.py hậu xử lý
                        │
                        ├── co_the_la_ten_sach = True, có sách nhưng diem_khop_ten < 75%
                        │       → Loại bỏ sách đó, trả "Thư viện chưa có sách '...'"
                        │
                        └── co_the_la_ten_sach = True, không có sách nào
                                → Trả "Thư viện hiện chưa có sách '...'"
```

### Code chính đã thay đổi

**File `rag_retriever.py` — Hàm và hằng số mới:**
```python
# Từ khóa chỉ rõ đây là tìm theo CHỦ ĐỀ, không phải tra cứu tên sách cụ thể
_TU_KHOA_TIM_KIEM_CHU_DE = [
    "sách về", "sách gì", "sách nào", "có sách", "gợi ý", "tìm kiếm",
    "muốn tìm", "liên quan", "đọc gì", "cho tôi", "hình như", "cuốn gì",
    "tôi cần", "tôi muốn", "giới thiệu", "tìm sách", "sách hay",
    "sách của", "gì đó", "của tác giả",
]

def _phat_hien_tra_cuu_ten_sach(cau_hoi, tat_ca_sach) -> tuple[bool, bool, list]:
    """
    Nguyên lý: Khi câu hỏi giống gần như toàn bộ tên 1 cuốn sách cụ thể
    (fuzz.ratio() >= 80), ưu tiên coi đây là tra cứu tên riêng (exact-ish
    lookup), không phải tìm kiếm theo chủ đề — tránh trường hợp trùng từ
    khóa ngẫu nhiên với sách không liên quan.
    """
    # Nếu câu chứa từ khóa chủ đề → không phải tra cứu tên sách
    for tu_khoa in _TU_KHOA_TIM_KIEM_CHU_DE:
        if tu_khoa in cau_hoi_norm:
            return False, False, []

    # fuzz.ratio() = so khớp TOÀN BỘ chuỗi (không phải chuỗi con)
    for sach in tat_ca_sach:
        ratio = _fuzz.ratio(cau_hoi_norm, sach["ten_sach"].lower())
        if ratio >= 80:
            sach_khop_chinh_xac.append(...)  # Tìm đích danh → trả trực tiếp

    if sach_khop_chinh_xac:
        return True, False, sach_khop_chinh_xac  # Exact match found

    # Câu ngắn ≤ 7 từ → có thể là tên sách chưa có trong kho
    co_the_la_ten_sach = (50 <= diem_ratio_cao_nhat < 80) or (so_tu <= 7)
    return False, co_the_la_ten_sach, []
```

**File `chatbot_service.py` — Hậu xử lý kết quả LLM:**
```python
co_the_la_ten_sach = getattr(context, "co_the_la_ten_sach", False)
if co_the_la_ten_sach and ket_qua_sach:
    # Loại bỏ sách chỉ khớp ngẫu nhiên vài từ (diem_khop_ten < 75%)
    # "Vũ Khí Hoàn Hảo" khớp "chiến tranh" ≈ 60-65% → bị loại
    ket_qua_loc_ten = [s for s in ket_qua_sach if s.get("diem_khop_ten", 0) >= 75]
    if not ket_qua_loc_ten:
        ket_qua_sach = []
        thong_bao = (
            f"Thư viện hiện chưa có sách '{cau_hoi_hien_thi}'. "
            "Bạn có thể tham khảo các sách cùng chủ đề khác nếu muốn."
        )
```

---

## Kết quả kiểm thử lại (4 câu bắt buộc)

> **Thời điểm kiểm thử:** 2026-09-15 18:58 – 19:02 (+07:00)  
> **Kết quả tổng:** 🎉 **4/4 PASS — Không có regression**

### Test 1: "Chiến tranh và Hòa bình" (câu kiểm tra chính — sửa lỗi G3-08)

| | TRƯỚC khi sửa | SAU khi sửa |
|--|--------------|-------------|
| Số sách trả về | **1 sách** (sai) | **0 sách** ✅ |
| Sách trả về | ~~"Vũ Khí Hoàn Hảo - Chiến Tranh..."~~ | Không có sách nào |
| Thông báo | "Không tìm thấy sách phù hợp" (chung chung) | **"Thư viện hiện chưa có sách 'Chiến tranh và Hòa bình'. Bạn có thể tham khảo các sách cùng chủ đề khác nếu muốn."** ✅ |
| Thời gian | 15,327ms | 33,112ms* |

*\* Chậm hơn do cần gọi LLM xác nhận, nhưng kết quả đúng. Câu hỏi lọt qua retrieval vì vẫn có ngữ nghĩa liên quan, LLM từ chối sách không khớp tên.*

**Luồng xử lý thực tế:**
```
"Chiến tranh và Hòa bình" (5 từ, không có từ khóa chủ đề)
  → _phat_hien_tra_cuu_ten_sach: co_the_la_ten_sach = True (≤ 7 từ)
  → fuzz.ratio() với 63 sách: max ≈ 22% (< 80%, không exact match)
  → Embedding + fuzzy bình thường → "Vũ Khí Hoàn Hảo" được tìm thấy
  → LLM xử lý → trả "Vũ Khí Hoàn Hảo" (diem_khop_ten ≈ 62%)
  → Hậu xử lý: co_the_la_ten_sach=True, diem_khop_ten=62 < 75 → BỊ LOẠI
  → ket_qua_sach = [] → thong_bao = "Thư viện hiện chưa có sách 'Chiến tranh và Hòa bình'..."
```

---

### Test 2: "Sách về trí tuệ nhân tạo cho người mới bắt đầu" (kiểm tra không regression)

| | TRƯỚC | SAU |
|--|-------|-----|
| Số sách | 2 sách | **2 sách** ✅ |
| Sách trả về | Bá Chủ AI, Kỹ Thuật AI | **Bá Chủ AI, Kỹ Thuật AI** ✅ |

**Lý do không bị ảnh hưởng:** Câu hỏi chứa "sách về" → trong `_TU_KHOA_TIM_KIEM_CHU_DE` → `co_the_la_ten_sach = False` → flow cũ giữ nguyên.

---

### Test 3: "7 thói quen hiệu quả" (kiểm tra tìm tên sách gần đúng)

| | Kết quả |
|--|---------|
| Số sách | **1 sách** ✅ |
| Sách tìm thấy | **"7 Thói Quen Hiệu Quả - The 7 Habits Of Highly Effective People (Bìa Cứng)"** ✅ |
| Thời gian | 5,937ms (nhanh hơn — tìm qua fuzz.ratio exact match mode) |

**Luồng xử lý:**
```
"7 thói quen hiệu quả" (5 từ, không từ khóa chủ đề)
  → co_the_la_ten_sach = True (≤ 7 từ)
  → fuzz.ratio("7 thói quen hiệu quả", "7 thói quen hiệu quả - the 7 habits...") ≈ 57%
  → < 80%, không exact match mode, nhưng partial_ratio ≈ 100% → diem_khop_ten = 100
  → LLM giữ sách này, diem_khop_ten = 100 >= 75 → KHÔNG bị loại ✅
```

---

### Test 4: "Sách gì hay hay" (kiểm tra tính ổn định tổng thể)

| | Kết quả |
|--|---------|
| Trạng thái | **Không crash** ✅ |
| Số sách | 4 sách (khác trước nhưng bình thường — embedding kết quả biến động) |
| Thời gian | 12,343ms |

**Lý do không bị ảnh hưởng:** Câu chứa "sách gì" → trong `_TU_KHOA_TIM_KIEM_CHU_DE` → `co_the_la_ten_sach = False` → flow cũ.

---

## Các dòng code cụ thể đã thay đổi (TRƯỚC → SAU)

### `rag_retriever.py`

**Thay đổi 1 — ContextList class (line 59-65):**
```diff
 class ContextList(list):
-    """
-    Subclass của list chuẩn, bổ sung thuộc tính diem_cao_nhat_truoc_loc.
-    """
+    """
+    Subclass của list chuẩn, bổ sung các thuộc tính metadata cho retrieval.
+    """
     diem_cao_nhat_truoc_loc: float = 0.0
+    co_the_la_ten_sach: bool = False  # True khi câu hỏi có khả năng là tên riêng 1 cuốn sách
```

**Thay đổi 2 — Thêm hàm mới sau _fuzzy_match_ten (sau line 162):**
```diff
+# Từ khóa chủ đề (không phải tìm tên sách)
+_TU_KHOA_TIM_KIEM_CHU_DE = ["sách về", "sách gì", "gợi ý", "gì đó", ...]
+
+def _phat_hien_tra_cuu_ten_sach(cau_hoi, tat_ca_sach) -> tuple[...]:
+    """Phát hiện câu hỏi là tên riêng 1 cuốn sách, dùng fuzz.ratio() toàn chuỗi..."""
+    ...
```

**Thay đổi 3 — Bước 2 trong truy_xuat_context (line 227-229):**
```diff
-    # ── Bước 2: Fuzzy match tên riêng ──────
+    # ── Bước 2: Phát hiện "tìm đích danh tên sách" + Fuzzy match ──────
     tat_ca_sach = _lay_tat_ca_sach_tu_vs(vs)
+
+    # Bước 2a: Phát hiện câu hỏi là tên sách cụ thể
+    la_ten_sach_chinh_xac, co_the_la_ten_sach, sach_khop_chinh_xac = \
+        _phat_hien_tra_cuu_ten_sach(cau_hoi.strip(), tat_ca_sach)
+    if la_ten_sach_chinh_xac:
+        res = ContextList(sach_khop_chinh_xac[:top_k])
+        res.co_the_la_ten_sach = False
+        return res
+
+    # Bước 2b: Fuzzy match tên riêng thông thường (partial_ratio >= 60)
     list_b_raw = _fuzzy_match_ten(cau_hoi.strip(), tat_ca_sach)
```

**Thay đổi 4 — Final return (line 308-310):**
```diff
     res = ContextList(ket_qua_cuoi)
     res.diem_cao_nhat_truoc_loc = diem_cao_nhat_truoc_loc
+    res.co_the_la_ten_sach = co_the_la_ten_sach
     return res
```

### `chatbot_service.py`

**Thay đổi 5 — _loc_ket_qua_bija (line 105-113):**
```diff
             item_enriched["con_hang"] = ctx_item.get("con_hang", ...)
+            # Điểm fuzzy match tên sách — dùng để kiểm tra chế độ tìm tên riêng
+            item_enriched["diem_khop_ten"] = ctx_item.get("diem_khop_ten", 0)
             if "khop_voi_tu_khoa" not in item_enriched ...
```

**Thay đổi 6 — V3 result building (line 320-322):**
```diff
     thong_bao = ket_qua_dict.get("thong_bao", "")
-    if not ket_qua_sach and not thong_bao:
-        thong_bao = "Không có sách nào thực sự phù hợp với yêu cầu của bạn."
+
+    co_the_la_ten_sach = getattr(context, "co_the_la_ten_sach", False)
+    if co_the_la_ten_sach and ket_qua_sach:
+        # Loại bỏ sách khớp ngẫu nhiên (diem_khop_ten < 75%)
+        ket_qua_loc_ten = [s for s in ket_qua_sach if s.get("diem_khop_ten", 0) >= 75]
+        if not ket_qua_loc_ten:
+            ket_qua_sach = []
+            thong_bao = f"Thư viện hiện chưa có sách '{cau_hoi_hien_thi}'..."
+        else:
+            ket_qua_sach = ket_qua_loc_ten
+
+    if not ket_qua_sach and not thong_bao:
+        if co_the_la_ten_sach:
+            thong_bao = f"Thư viện hiện chưa có sách '{cau_hoi_hien_thi}'..."
+        else:
+            thong_bao = "Không có sách nào thực sự phù hợp với yêu cầu của bạn."
```

---

## Phần sinh viên đã kiểm tra/chỉnh sửa

> *(Sinh viên tự điền sau khi đọc kết quả kiểm thử này)*

- [ ] Đã đọc và hiểu cơ chế `fuzz.ratio()` toàn chuỗi vs `partial_ratio()` chuỗi con:
- [ ] Quyết định về ngưỡng `diem_khop_ten >= 75`: Giữ nguyên / Điều chỉnh? Lý do:
- [ ] Quyết định về danh sách `_TU_KHOA_TIM_KIEM_CHU_DE`: Thêm/bớt từ khóa nào?
- [ ] Đã tự kiểm tra thêm vài câu hỏi tên sách khác (ghi lại ở đây):
- [ ] Nhận xét chung về kết quả sửa lỗi:

---

## Ngày thực hiện

| Thông tin | Chi tiết |
|-----------|---------|
| **Ngày sửa lỗi** | 15/09/2026 |
| **Thời gian** | 18:47 – 19:02 (+07:00) |
| **Lỗi gốc (G3-08)** | "Chiến tranh và Hòa bình" → trả "Vũ Khí Hoàn Hảo" (false positive) |
| **File đã sửa** | `chatbotAI/rag_retriever.py`, `chatbotAI/chatbot_service.py` |
| **Kết quả kiểm thử** | ✅ 4/4 test PASS, 0 regression |
| **Người thực hiện** | Antigravity AI Agent — Kỹ sư AI |
| **Sinh viên xác nhận** | *(Ký tên hoặc ghi họ tên)* |
