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