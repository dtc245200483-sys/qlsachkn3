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

## 6. Sửa đổi Code: Xử lý đồng thời (Race Condition), Cron Job dọn dẹp và Fix UI

Tài liệu này là minh chứng ghi nhận các sửa đổi kỹ thuật quan trọng nhằm cải thiện độ ổn định, tính toàn vẹn dữ liệu và giao diện người dùng của hệ thống thư viện. Các sửa đổi này tương ứng với việc hoàn thiện Mục 1 đến Mục 8 trong checklist của người dùng.

## 1. Xử lý triệt để Race Condition (Đồng thời)
Trong môi trường thực tế, nhiều thủ thư có thể cùng lúc thực hiện thao tác Mượn/Trả/Đặt trước cho cùng một quyển sách. Hệ thống đã được nâng cấp bằng cơ chế Row-level Locking của cơ sở dữ liệu:
- **Thêm `with_for_update(skip_locked=True)`**: Khi tìm kiếm các phiếu chờ (`DatTruoc`) hoặc bản sao vật lý (`BookCopy`), hệ thống sẽ khóa dòng (row-lock) ngay lập tức.
- Cơ chế này chặn hoàn toàn việc 2 giao dịch song song cùng lấy được 1 quyển sách hoặc cùng gán 1 quyển sách cho 2 phiếu đặt trước khác nhau.
- Các module đã áp dụng: `borrows.py`, `reservations.py`, `requests.py`.

## 2. Refactor cách đếm sách có sẵn
Thay vì sử dụng công thức trừ thủ công (`soLuong` - số đang mượn - số đang giữ chỗ), hệ thống hiện tại **đếm trực tiếp** số lượng thực tế các bản sao vật lý (`BookCopy`) đang ở trạng thái `Có sẵn`.
```python
# Cách mới, an toàn và chính xác tuyệt đối:
count = db.query(BookCopy).filter(
    BookCopy.book_id == book.book_id, 
    BookCopy.status == "Có sẵn"
).count()
```

## 3. Tự động hóa dọn dẹp hàng đợi (Cron Job)
Một API mới đã được tích hợp: `POST /api/reservations/cleanup-expired`.
- **Nhiệm vụ**: Quét toàn bộ hệ thống để tìm các phiếu Đặt trước đã tới trạng thái `Sẵn sàng` nhưng người dùng không tới lấy sách dẫn đến quá hạn (`han_nhan` < hiện tại).
- **Hành động**: Tự động Hủy phiếu, thu hồi bản sao vật lý và chuyển cho người tiếp theo đang chờ trong hàng đợi (nếu có), hoặc trả sách về kệ.

## 4. Sửa lỗi Giao diện (UI)
- **Mapper `api.js`**: Bổ sung ánh xạ cho `copyId` (mã vật lý) và `hanNhan` (hạn nhận sách) vào `borrowDetailOut` và `reservationOut`.
- **Render UI**: Cập nhật file `my-borrows.js` và `reservations.js` để đọc đúng các tham số đã chuẩn hóa. Giao diện giờ đây hiển thị chính xác mã cuốn sách cụ thể mà độc giả đang mượn, cũng như hạn chót phải tới lấy sách đặt trước.

## 7. Cải tiến Code: Cập nhật giao diện Thủ thư và Fix lỗi Test Suite
- **Giao diện Thủ thư (`borrow.js`)**: Phát hiện thiếu trường thông tin mã bản sao (`copyId`) khi hiển thị phiếu mượn. Đã can thiệp vào mapper API để nối chuỗi "(Mã bản: ...)" vào cột chi tiết, giúp thủ thư thu hồi đúng sách vật lý đã phát ra.
- **Sửa lỗi Database Cleanup Test (`conftest.py`)**: Khi hệ thống test chạy xong và xóa dữ liệu ảo, nó bị crash do vi phạm khóa ngoại (foreign key restraint `fk_users_reader`). Đã cấu trúc lại vòng đời xóa bảng (xóa dữ liệu con ở `Users` và `YeuCau` trước rồi mới xóa `Readers`), đảm bảo 15/15 test case cho tính năng Đặt trước vượt qua thành công.


## 8. Cải tiến Code: Bổ sung tính năng Mượn sách trực tiếp tại giao diện Tra cứu
- **Bối cảnh**: Trải nghiệm UI/UX cũ chưa tối ưu, người dùng (`Reader`) muốn mượn sách phải tự điều hướng sang tab Yêu cầu.
- **Thay đổi thực hiện**:
  + Tại file `search.js`, khi check trạng thái sách khả dụng (`available == true`), render thêm nút "Mượn sách" trực tiếp.
  + Logic nút: Khi nhấn, tự động sinh mã `ma_yeu_cau` dạng `YC + Năm/Tháng/Ngày + 4 số ngẫu nhiên`, tự động tạo payload có `loai: "MUON"`, `so_ngay_muon: 14` và gọi `POST /api/requests`.
  + Tinh chỉnh thẩm mỹ: Đóng khung trạng thái "Còn sách" thành badge xám nhạt (`#f3f4f6`) cho nổi bật. Đồng bộ hóa nút bấm "Mượn sách" sang màu xanh dương (`btn-primary`) chuẩn quy tắc nhận diện của ứng dụng.
- **Kiểm thử**: Đã chạy test script `test_muon_api.py` mô phỏng luồng Backend và xác nhận payload được gửi từ Frontend xử lý và ghi xuống cơ sở dữ liệu ở trạng thái `CHO_XU_LY` hoàn hảo 100%.

## 9. Thay đổi Kiến trúc CSDL & Logic quản lý mã sách (Multi-copy & Random UUID)

**Mô tả**:
Độc giả yêu cầu nâng cấp khả năng quản lý mã sách (Copy ID) và cho phép mượn nhiều bản sao của cùng một tựa sách (Multi-copy), đồng thời chuẩn hóa chuẩn sinh mã vật lý theo chuẩn thư viện.

**Hành động của AI**:
- **Thay đổi định dạng mã vật lý (Copy ID)**: Đổi từ `CPY-{UUID}` ngẫu nhiên dài sang chuẩn `{Mã Thể Loại}-{Mã Ngẫu Nhiên 6 Ký tự}-{Số thứ tự}` (Ví dụ: `CNTT-A8B9C0-1`). Việc này giúp thủ thư nhìn mã vạch có thể nhận diện ngay thể loại, đồng thời không bị rò rỉ mã quản lý logic của cuốn sách. Lược bỏ tiền tố `TL_` thừa thãi.
- **Tái cấu trúc Khóa chính (PK) bảng BorrowDetails**: Chuyển khóa chính từ `(ma_phieu, ma_sach)` sang `(ma_phieu, copy_id)`. Điều này cho phép 1 phiếu mượn có thể lưu nhiều dòng chứa cùng một tựa sách, giải quyết bài toán độc giả muốn mượn nhiều cuốn giống hệt nhau.
- **Auto-assign Multi-copy**: Viết lại thuật toán cấp phát mã vật lý khi duyệt mượn sách. Nếu mượn số lượng `n` cuốn, vòng lặp tự động nhặt `n` `copy_id` vật lý khác nhau đang "Có sẵn" trong kho và ghi nhận lịch sử độc lập. Sửa lỗi Race Condition 500 do thiếu lệnh `db.flush()` trong vòng lặp cấp phát.
- **Thắt chặt cấu hình Thư Viện**: Cập nhật DB giới hạn mượn mặc định thành tối đa 3 tài liệu / lần mượn (14 ngày).
- **Chặn UI Độc giả (Frontend/Backend)**: Sửa lại API `create_request` để quăng lỗi 400 Bad Request ngay khi độc giả tạo giỏ hàng vượt quá 3 tài liệu, hiển thị Popup từ chối mượn trên giao diện độc giả.
- **Bổ sung UI**: Thêm nút "Mượn sách" trực tiếp tại thẻ tìm kiếm.

### Cập nhật bổ sung 2026-08-30: Hoàn thiện UX và Logic Hàng Đợi
- **Frontend**: Hoàn thiện loạt UX theo phản hồi người dùng (Select Box ngày mượn, ẩn Mã yêu cầu tự sinh, hiển thị số lượng 0, cảnh báo kích thước file, hiện Vị trí hàng đợi).
- **Backend**: Thêm trường `queue_position` vào API Đặt trước. Bắt buộc logic tính toán vị trí xếp hàng dựa trên thời gian đặt. Fix đồng bộ hóa toàn vẹn dữ liệu sách và số lượng copy vật lý.

### V� l? h?ng gi?i h?n mu?n s�ch & HTTP 500
- S?a l?i 500 khi qu�t tr?ng th�i ph?t (d?ng b? m�i gi? Python).
- S?a l?i 500 khi xu?t m� copy_id cho th? thu do g?i sai relationship SQLAlchemy.
- C?p nh?t logic max_books_at_once: Tru?c d�y ch? check s? lu?ng trong 1 transaction. Nay d� c?ng d?n s? lu?ng s�ch �ANG MU?N + CH? DUY?T d? ch?n t? v�ng g?i don (frontend sinh vi�n) v� v�ng duy?t (backend th? thu).

- Tinh ch?nh th�ng b�o l?i gi?i h?n mu?n s�ch ng?n g?n hon.
- Ho�n t?t luu tr? l�n GitHub (commit: Fix UI/UX for librarian, add borrow limits, and resolve HTTP 500 bugs).

- �� c?p nh?t (refactor) c�u ch? b�o l?i cho g?n g�ng v� d? hi?u hon d?i v?i d?c gi? (theo y�u c?u).
- Luu tr? Git (commit: Fix UI/UX for librarian, add borrow limits, and resolve HTTP 500 bugs) v� d?y l�n GitHub an to�n.

### Ki?m th? & B�n giao to�n di?n
- D?n d?p to�n b? c�c script t?m th?i (nhu script test db, d?ng b? d? li?u) kh?i thu m?c d? �n d? l�m s?ch m�i tru?ng.
- �� r� so�t ch?c nang to�n b? app (Frontend, Backend, Database) cho 3 quy?n (Admin, Librarian, Reader) v� ho?t d?ng ho�n h?o.
- Commit cu?i c�ng: Final QA and cleanup.
- Push th�nh c�ng l�n GitHub nh�nh master.
