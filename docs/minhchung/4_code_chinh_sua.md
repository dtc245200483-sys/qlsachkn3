# Minh chứng 2.9 (Phần 4): Phần mã nguồn sinh viên tự kiểm tra và chỉnh sửa

Đây là phần minh chứng **quan trọng nhất**, mang tính chất "chốt điểm". Nó chứng minh tôi không sử dụng công cụ AI một cách bị động. Khi các Agent code độc lập với nhau, chúng thường sinh ra lỗi "lệch pha" (Frontend có giao diện nhưng Backend không có API xử lý) hoặc lỗi logic nghiệp vụ.

Dưới đây là các lần tôi trực tiếp nhảy vào đọc code, debug và tự tay chỉnh sửa lại logic cốt lõi. Dữ liệu trích xuất từ log hệ thống.

## 1. Phát hiện và sửa lỗi thiếu biến `so_ngay_muon` (Lệch pha Frontend - Backend)

Vào lúc `18:01:49` ngày 2026-08-09, Frontend Agent tự ý đưa thêm ô nhập "Số ngày mượn" vào trang Độc giả gửi yêu cầu mượn sách. Tuy nhiên, Backend Agent lúc đó đang chạy ở phiên bản 0.6.0 hoàn toàn không biết đến trường dữ liệu này (vì trong thiết kế ban đầu, thư viện tự ấn định số ngày mượn cố định).

**Log cảnh báo lệch pha ghi nhận được:**
> `[FRONTEND] 2026-08-09 18:01:49 - Thay đổi: Chuyển luồng nhập số ngày mượn về phía reader... Backend 0.6.0 chưa lưu/trả so_ngay_muon nên cần bổ sung vào RequestCreate/RequestOut và dùng khi approve...`

**Hành động chỉnh sửa của tôi:**
Tôi đã tự mở mã nguồn Backend (`Backend/app/schemas.py` và `Backend/app/routers/requests.py`), tự khai báo thêm biến `so_ngay_muon` và can thiệp sâu vào hàm "Duyệt mượn sách" (Approve) của Thủ thư. Tôi lập trình logic: ưu tiên lấy số ngày do độc giả đề xuất, nếu độc giả nhập lố số ngày tối đa thì gán bằng `max_borrow_days`.

```python
# Đoạn code do TÔI tự viết thêm vào hàm approve_request (requests.py)
# Tính hạn trả dựa trên số ngày mượn độc giả yêu cầu (ưu tiên) hoặc thư viện quy định
borrow_days = req.so_ngay_muon if req.so_ngay_muon and req.so_ngay_muon > 0 else config.max_borrow_days
# Ràng buộc không cho vượt quá quy định
if borrow_days > config.max_borrow_days:
    borrow_days = config.max_borrow_days
    
han_tra = datetime.utcnow() + timedelta(days=borrow_days)
```

## 2. Phát hiện và rào lỗi logic khi Độc giả Xóa lịch sử mượn

Vào lúc `18:17:43`, Frontend Agent thêm nút "Xóa lịch sử" ở trang hồ sơ cá nhân. Tuy nhiên Backend lại chưa cung cấp hàm `DELETE`. Nếu để AI tự viết, AI có xu hướng viết API xóa (DELETE) một cách mù quáng (xóa mất cả sách đang mượn).

**Hành động chỉnh sửa của tôi:**
Tôi đã nhảy vào Backend (`routers/borrows.py`) tự tay viết 2 endpoint mới: `DELETE /api/borrows/me` và `DELETE /api/borrows/me/{ma_phieu}`. 
Tôi đã rào logic cực kỳ cẩn thận:
- Chặn không cho xóa phiếu của người khác (kiểm tra `borrow.reader_id`).
- Chặn tuyệt đối **KHÔNG ĐƯỢC XÓA PHIẾU ĐANG MƯỢN** (chưa trả sách), vì nếu xóa sẽ gây mất dấu cuốn sách. Chỉ được xóa lịch sử phiếu ĐÃ TRẢ (`da_tra = True`).

```python
# Đoạn code bảo vệ CSDL do TÔI tự viết vào API DELETE Borrow
@router.delete("/me/{ma_phieu}")
def delete_my_borrow(ma_phieu: int, db: Session = Depends(get_db), current_user = Depends(require_role(["reader"]))):
    # Lấy thông tin phiếu mượn
    borrow = db.query(BorrowSlips).filter(BorrowSlips.ma_phieu == ma_phieu).first()
    
    # 1. Rào lỗi bảo mật: Cấm xóa phiếu của người khác
    if borrow.reader_id != current_user.reader_id:
        raise HTTPException(status_code=404, detail="Phiếu mượn không tồn tại hoặc không thuộc quyền")
        
    # 2. Rào lỗi kế toán: Cấm xóa sách đang cầm về nhà chưa trả
    if not borrow.da_tra:
        raise HTTPException(status_code=400, detail="Không thể xóa phiếu mượn chưa hoàn tất (đang mượn sách)")
        
    # Sau khi qua 2 chốt chặn mới cho phép db.delete()
    db.delete(borrow)
    db.commit()
```

## 3. Sửa lỗi Xóa độc giả (Phân quyền Admin vs Librarian)
Như đã cảnh báo ở Phần trước, thủ thư không được phép xóa tài khoản. Tuy nhiên code AI thường cấp quyền chung chung là "Nhân viên". Tôi đã tự thay thế chuỗi quyền từ `@require_role(["admin", "librarian"])` thành `@require_role(["admin"])` cho tất cả các endpoint mang tính sát thương cao như Xóa tài khoản, Xóa sách, Cấu hình hệ thống.

---
**Tổng kết Phần 4:**
Thông qua 3 ví dụ thực chiến trên, tôi đã chứng minh được việc mình hoàn toàn đọc hiểu cấu trúc dự án (FastAPI, JWT, SQLAlchemy) và đủ năng lực viết code đè lên code của AI để bảo vệ tính đúng đắn của dữ liệu. AI chỉ là công cụ hỗ trợ gõ code nhanh, còn **tư duy nghiệp vụ (business logic)** do chính sinh viên kiểm soát.

## 4. Phát hiện và sửa lỗi: AI để trống ID Sách, sinh ID trùng nhau (2026-08-28)

Sau khi AI chèn 64 cuốn sách vào Database, tôi kiểm tra và phát hiện lỗi nghiêm trọng: **tất cả 64 sách đều có 4 số giống nhau ở đuôi** (VD: `BMTM0001`, `CNTT0001`, `KTODO0001`...). Nguyên nhân là AI dùng counter riêng biệt cho từng thể loại thay vì dùng một bộ đếm toàn cục.

**Hành động sửa lỗi của tôi:**
Tôi đã tự viết lại script `update_book_ids.py`, ép tất cả sách phải chạy qua một vòng lặp **duy nhất** với biến `counter` toàn cục, đảm bảo con số cuối cùng không bao giờ trùng nhau dù thuộc thể loại nào:

```python
# Tôi tự viết logic sửa lỗi ID trùng — duyệt tất cả sách 1 lần duy nhất
all_books = db.query(Book).all()
global_counter = 1  # Bộ đếm TOÀN CỤC, không reset theo thể loại

for book in all_books:
    acronym = generate_acronym(book.ten_sach)
    book.ma = f"{acronym}{str(global_counter).zfill(4)}"
    global_counter += 1   # Luôn tăng, không bao giờ reset

db.commit()
```
Kết quả: 64 sách mang mã hoàn toàn phân biệt (từ `...0001` đến `...0064`).

## 5. Phát hiện lỗi Xóa Độc giả không kiểm tra ràng buộc (2026-08-27)

AI đã sinh ra API `DELETE /api/readers/{ma}` nhưng **không kiểm tra** xem độc giả đó có đang mượn sách, đang nợ phạt, hay có đặt trước chưa. Điều này cực kỳ nguy hiểm: một cú click "Xóa" có thể xóa mất hồ sơ độc giả đang cầm sách về nhà.

**Hành động sửa lỗi của tôi:**
Tôi tự thêm 3 chốt chặn bảo vệ nghiệp vụ vào trước khi cho phép xóa:

```python
# Chốt 1: Kiểm tra đang mượn sách chưa trả
active_borrows = db.query(BorrowSlips).filter(
    BorrowSlips.reader_id == reader.ma,
    BorrowSlips.da_tra == False
).count()
if active_borrows > 0:
    raise HTTPException(400, "Độc giả đang mượn sách, không thể xóa")

# Chốt 2: Kiểm tra còn nợ phạt chưa thu
unpaid_fines = db.query(FineHistory).filter(
    FineHistory.reader_id == reader.ma,
    FineHistory.da_thu == False
).count()
if unpaid_fines > 0:
    raise HTTPException(400, "Độc giả còn nợ phạt, không thể xóa")

# Chốt 3: Kiểm tra còn phiếu đặt trước đang chờ
pending_reservations = db.query(DatTruoc).filter(
    DatTruoc.reader_id == reader.ma,
    DatTruoc.trang_thai.in_(["CHO_XU_LY", "SAN_SANG"])
).count()
if pending_reservations > 0:
    raise HTTPException(400, "Độc giả có đặt trước đang chờ xử lý, không thể xóa")
```
Đây là tư duy phòng thủ (defensive programming) mà AI không tự động áp dụng trừ khi được chỉ đích danh trong Prompt.