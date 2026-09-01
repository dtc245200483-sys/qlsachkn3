# Minh chứng 2.9 (Phần 4): Năng lực kiểm soát, phản biện và điều khiển AI

Đây là phần minh chứng **quan trọng nhất**, mang tính chất "chốt điểm". Nó chứng minh tôi không sử dụng công cụ AI một cách bị động hay mù quáng copy-paste. Trong suốt quá trình phát triển, AI (Agent) thường xuyên mắc các sai lầm nghiêm trọng về nghiệp vụ, "lệch pha" giữa Frontend - Backend, hoặc đưa ra các giải pháp bề nổi. 

Với vai trò là người làm chủ hệ thống, tôi liên tục đóng vai trò **Người kiểm duyệt (Code Reviewer) và Kiến trúc sư (Software Architect)**: phát hiện lỗi của AI, phân tích nguyên nhân tận gốc, bác bỏ các đề xuất sai lệch và **ra lệnh/điều hướng nghiêm ngặt** buộc AI phải sửa lại code đúng chuẩn.

Dưới đây là 23 minh chứng tiêu biểu (được sắp xếp theo đúng trình tự thời gian phát triển dự án) khẳng định năng lực điều khiển AI của tôi:

## GIAI ĐOẠN 1: KHỞI TẠO NỀN TẢNG & PHÂN QUYỀN (09/08 - 10/08/2026)

### 1. Phát hiện và ép AI sửa lỗi thiếu biến `so_ngay_muon` (Lệch pha Hệ thống)
Vào lúc `18:01:49` ngày 09/08, AI Frontend tự ý thiết kế thêm ô "Số ngày mượn" trên UI, nhưng AI Backend lại không có trường dữ liệu này trong API.
**Cách tôi điều khiển AI:** Tôi lập tức ra lệnh cho AI Backend khai báo biến `so_ngay_muon` vào `RequestCreate`, đồng thời vạch ra nghiệp vụ: *"Khi duyệt đơn, phải ưu tiên lấy số ngày do độc giả đề xuất nhưng cấm vượt mức `max_borrow_days`"*. AI mới sinh ra đoạn code xử lý chính xác.

### 2. Bác bỏ API "Xóa" mù quáng – Bắt buộc lập trình phòng thủ
Ngày 09/08, AI sinh ra API `DELETE` cơ bản xóa thẳng phiếu mượn.
**Cách tôi điều khiển AI:** Tôi bác bỏ đoạn code nguy hiểm này và lệnh cho AI phải cài đặt 2 chốt chặn: Kiểm tra `reader_id` (Cấm xóa phiếu người khác) và Kiểm tra `da_tra == True` (Tuyệt đối không được xóa phiếu ĐANG MƯỢN).

### 3. Nhập vai Admin: Bắt lỗi bảo mật thiếu Audit Log
Đóng vai một quản trị viên khó tính (09/08), tôi thấy AI cho phép Thủ thư tự do thao tác mà không lưu dấu vết.
**Cách tôi điều khiển AI:** Tôi bắt AI xây dựng hệ thống **Audit Log (Lưu vết thao tác)** chạy ngầm. Mọi hành động Create, Update, Delete đều phải được ghi thẳng vào CSDL.

### 4. Điều chỉnh phân quyền - Không nghe theo cấu hình mặc định
Ngày 10/08, AI gộp chung quyền `["admin", "librarian"]` cho mọi thao tác.
**Cách tôi điều khiển AI:** Tôi review và chỉ thị AI phải bóc tách: Thủ thư chỉ vận hành mượn/trả, tuyệt đối cấm xóa tài khoản/cấu hình. Tôi ép AI thay chuỗi quyền sang `@require_role(["admin"])` tại các điểm nhạy cảm.

### 5. Phân quyền Hiển thị động (Dynamic Navbar)
Giai đoạn 10/08, AI để tất cả các nút (Quản lý, Thống kê) hiển thị cho mọi người, bấm vào mới báo lỗi.
**Cách tôi điều khiển AI:** Tôi chỉ đạo: *"Frontend phải đọc Role sau khi đăng nhập. Dùng JS để `display: none` các menu theo Role. Sinh viên không được nhìn thấy nút Admin."* AI buộc cập nhật `layout.js`.

### 6. Bắt quả tang AI làm giả dữ liệu (Mock Data) - Ép gọi API thật
Khi yêu cầu làm "Chuông thông báo" (10/08), AI đối phó bằng cách tạo thông báo giả lưu bằng `localStorage`.
**Cách tôi điều khiển AI:** Kiểm tra Network, tôi phát hiện trò bịp này. Tôi lệnh: *"Xóa logic Mock Data. Tạo bảng `Notifications` và gọi API thật (`/api/notifications`)."* AI phải làm lại toàn bộ.

### 7. Gạt bỏ những tính năng rườm rà (Thừa thãi)
AI tự ý đẻ ra hàng loạt nút "Xuất CSV" ở mọi bảng (10/08) để khoe kỹ năng.
**Cách tôi điều khiển AI:** Tôi lệnh cứng rắn: *"Bỏ ngay toàn bộ nút Xuất CSV ở tất cả các trang. Giữ UI gọn gàng, bám sát luồng cốt lõi."*

### 8. Chuẩn hóa Giao diện theo bản sắc Trường học (Localization)
AI sinh giao diện chung chung kiểu "Library System" và báo lỗi tiếng Anh (10/08).
**Cách tôi điều khiển AI:** Tôi yêu cầu đổi Banner khớp với **Trường ĐH CNTT & Truyền thông (ICTU)** và bắt Validation form phải 100% tiếng Việt.

### 9. Thanh lọc Jargon (Từ lóng kỹ thuật) trên UI
AI in thẳng mã Use Case ra màn hình (VD: `Quản lý sách UC01`).
**Cách tôi điều khiển AI:** Tôi dạy AI: *"Người dùng không cần biết UC là gì. Xóa mọi hậu tố UC trên điều hướng và tiêu đề."*

---

## GIAI ĐOẠN 2: HOÀN THIỆN UX/UI & ĐỊNH DẠNG (27/08/2026)

### 10. Bác bỏ Alert rác - Ép dùng Inline Validation
Mọi lỗi xác thực form, AI đều văng hộp thoại `alert("Lỗi...")` rất nghiệp dư.
**Cách tôi điều khiển AI:** Tôi lệnh cấm dùng `window.alert()`. Ép tạo các thẻ `div` ẩn (Inline Validation) để render chữ màu đỏ dưới ô nhập bị sai.

### 11. Nhập vai Thủ thư "Hải Yến": Chỉnh đốn thái độ giao tiếp
Khi độc giả mượn lố 3 cuốn, AI văng lỗi robot: *"Vượt quá số lượng... User: 4 > Max: 3"*.
**Cách tôi ép AI sửa:** Nhập vai thủ thư thân thiện, tôi lệnh đổi văn phong thành: *"Rất tiếc, độc giả đã đạt giới hạn... Vui lòng trả sách cũ để mượn thêm"*.

### 12. Chê bai giao diện Upload thô kệch - Ép thiết kế UX nâng cao
AI làm tính năng tải ảnh bìa bằng thẻ `<input type="file">` xấu xí.
**Cách tôi điều khiển AI:** Tôi bắt AI bỏ thẻ mặc định, thiết kế khu vực Dropzone hỗ trợ sự kiện kéo thả (Drag-and-Drop) kết hợp `FileReader` để Preview ảnh bìa.

### 13. Chuẩn hóa định dạng thẻ sinh viên (DTC)
AI sinh mã độc giả lung tung.
**Cách tôi điều khiển AI:** Tôi đưa ra quy luật bắt buộc: *"Mã sinh viên: 'DTC' + 9 số. Giảng viên: 'GV' + 4 số."* Tôi bắt AI bổ sung Regex vào cả Frontend và Backend để chặn lỗi.

---

## GIAI ĐOẠN 3: XÂY DỰNG DỮ LIỆU LỚN & PHÂN TRANG (28/08/2026)

### 14. Cấu trúc lại Kiến trúc Phân trang (Pagination) & Tìm kiếm
Ngày 28/08, AI tải toàn bộ 64 cuốn sách trong 1 lần gọi API, gây nghẽn trình duyệt.
**Cách tôi điều khiển AI:** Tôi ép AI viết lại API `GET /api/books` hỗ trợ `skip` và `limit`, kết hợp filter. Ở Frontend, bắt buộc vẽ thanh điều hướng phân trang và đồng bộ trạng thái `currentPage` vào URL.

### 15. Bắt lỗi AI sinh mã ID trùng lặp (Cái bẫy vòng lặp)
Khi sinh 64 sách, AI đặt bộ đếm reset theo thể loại khiến đuôi ID bị trùng (`BMTM0001`, `CNTT0001`...).
**Cách tôi điều khiển AI:** Tôi chỉ thẳng lỗi thuật toán: *"Đưa biến `global_counter` ra ngoài cục bộ, duyệt 1 vòng để đảm bảo ID cuối cùng không bao giờ trùng."* AI phải viết lại script sinh mã.

---

## GIAI ĐOẠN 4: KTR2 - KIẾN TRÚC SÂU & XỬ LÝ LỖI HỆ THỐNG (30/08 - 31/08/2026)

### 16. Nhập vai Thủ thư Kho: Đập đi làm lại sang quản lý bản vật lý
Ngày 30/08, tôi thấy AI quản lý sách bằng 1 con số chung chung (VD: 5 cuốn). Tôi chỉ ra: làm sao biết cuốn nào rách để bắt đền?
**Cách tôi ép AI sửa:** Tôi yêu cầu đập đi làm lại toàn bộ hệ thống lõi sang quản lý **Từng bản vật lý (BookCopy)** có mã vạch riêng (`KT-2D182B-1`).

### 17. Giải quyết xung đột Khóa Ngoại (Foreign Key) trên SQL Server
Trong đợt nâng cấp BookCopy, AI đề xuất SQL `ALTER TABLE` thuần túy nhưng bị SQL Server chặn vì vướng khóa ngoại `FK_BorrowDetails_Books`.
**Cách tôi điều khiển AI:** Tôi lệnh: *"Bỏ dùng SQL chay. Viết script Python dùng `pyodbc` kết hợp Raw SQL thực hiện đúng quy trình: Drop Constraint -> Drop PK -> Add copy_id -> Make New PK -> Re-add Constraint."*

### 18. Dạy AI cách bắt lỗi Dữ liệu toàn vẹn (Cascade Delete & IntegrityError)
Khi Thủ thư xóa sách, Backend trả lỗi 500 `IntegrityError` vì các bản `BookCopies` vật lý vẫn tồn tại.
**Cách tôi điều khiển AI:** AI đề xuất cấu hình Database `ON DELETE CASCADE` cực nguy hiểm. Tôi chặn lại và chỉ thị: *"Sửa hàm DELETE, xóa thủ công tất cả `BookCopies` trước, sau đó mới xóa `Book`."*

### 19. Bắt và rào lỗi UnboundLocalError cực hiểm hóc
Nếu độc giả mượn sách vừa hết hàng, code AI văng `UnboundLocalError`. AI khai báo biến trong `if` nhưng gọi ở `else`.
**Cách tôi điều khiển AI:** Tôi đọc Traceback, bắt AI khởi tạo giá trị mặc định `None` ở đầu hàm, dạy lại AI về phạm vi biến (Scope) trong Python.

### 20. Sửa lỗi nghiêm trọng (HTTP 500) do xung đột Múi giờ
Cronjob hủy đơn AI dùng `datetime.utcnow()` so sánh với giờ Local (GMT+7) của DB, khiến đơn vừa đặt bị xóa ngay lập tức.
**Cách tôi điều khiển AI:** Tôi yêu cầu AI: *"Tuyệt đối cấm dùng utcnow(). Sửa toàn bộ hàm `cleanup-expired` về `datetime.now()`."*

### 21. Nhập vai Độc giả: Sự bức xúc vì cột Vị trí hàng đợi vô dụng
Ngày 31/08, tôi test tính năng đặt trước. Dù sách về trạng thái `Sẵn sàng`, vị trí vẫn hiện dấu `-`.
**Cách tôi ép AI sửa:** Tôi chỉ ra lỗ hổng: Backend hàm đếm `queue_pos` bỏ quên trạng thái `SAN_SANG`, và Frontend lọc mất trường dữ liệu API. Tôi buộc AI sửa cả 2 đầu để độc giả thấy vị trí số 1.

### 22. Can thiệp trực tiếp cứu dữ liệu (Database) bị hỏng do Test
Đợt chạy Unit Tests tự động, AI viết kịch bản giả lập "Hết sách", ép 5 cuốn thật sang "Đang mượn" nhưng quên trả về cũ, khiến user không mượn được.
**Cách tôi điều khiển AI:** Tôi truy vấn DB, ra lệnh AI viết script Python chạy thẳng SQLAlchemy quét lại các "bản copy ma" này và ép `status` về 'Có sẵn'.

### 23. Quản trị vòng đời dự án & Dọn dẹp Rác (Clean Code)
Trước khi nghiệm thu bản cuối, AI vứt rải rác rất nhiều script rác test DB (`fix_db.py`, v.v.).
**Cách tôi điều khiển AI:** Đóng vai QA, tôi lệnh dọn dẹp toàn bộ thư mục thừa, rà soát lại 111/111 Unit Test phải PASS 100%, sau đó đích thân tôi mới duyệt lệnh `git push` đưa bản hoàn thiện lên nhánh `master`.

---
**KẾT LUẬN CUỐI CÙNG:** Bằng sự bao quát từ Data, Backend, Frontend cho tới Trải nghiệm người dùng, tôi đã bổ khuyết hoàn hảo cho sự máy móc của AI. Phần mềm cuối cùng không chỉ sạch bug về mặt kỹ thuật, mà còn cực kỳ **Thấu hiểu nghiệp vụ và Tôn trọng người dùng**.
