# 1. Các câu lệnh (Prompt) gửi cho AI

## Prompt điều khiển Backend Agent

> "BẮT BUỘC:
> 1. Không cho mượn khi số lượng sách còn = 0; số lượng không được âm.
> 2. Tự động tính phạt trễ hạn theo công thức người dùng xác nhận.
> 3. Đặt trước chỉ áp dụng khi sách đang hết/đang mượn hết.
> 4. Phân quyền chặt: độc giả không gọi được API quản trị.
> 5. API cấp cho AI Engine PHẢI lọc bỏ dữ liệu cá nhân độc giả (chỉ giữ những gì AI thật sự cần — đúng mục 5: 'đã ẩn thông tin nhạy cảm').
> 6. Có unit test/integration test cho: mượn/trả, tính quá hạn/phạt (đúng yêu cầu kỹ thuật mục 4). Không tự tạo dữ liệu mẫu nếu không được yêu cầu.
> 7. Mọi thay đổi schema phải có migration, không sửa tay DB."

## Prompt điều khiển Frontend Agent

> "PHẠM VI: Chỉ code trong thư mục Frontend. Công nghệ: React/Vue/HTML‑CSS‑JS/template engine theo lựa chọn người dùng khi bắt đầu, không tự đổi...
> BẮT BUỘC:
> 1. Chỉ làm đúng phần UI được giao trong lượt, không tự thêm màn hình ngoài phạm vi.
> 2. Khi Backend chưa có API, dùng dữ liệu mock tạm và ghi rõ chỗ sẽ nối API.
> 3. Phân quyền ở màn hình: độc giả không nhìn thấy/không dùng được chức năng quản trị.
> 4. Hiển thị rõ lỗi API: sách hết, thẻ khóa, quá hạn, không có kết quả tra cứu.
> 5. Tự chạy checklist trước khi báo xong."

## Prompt điều khiển AI Engine Agent

> "PROMPT TEMPLATE BẮT BUỘC DÙNG LÀM GỐC:
> System: 'Bạn là trợ lý tra cứu thư viện. Chỉ gợi ý sách có trong dữ liệu được cung cấp. Không bịa mã sách hoặc tình trạng sách.'
> User mẫu: 'Tôi muốn tìm sách dễ đọc về <chủ đề> cho người mới bắt đầu. Dữ liệu sách: {{book_list}}. Hãy gợi ý tối đa 5 cuốn, kèm lý do.'
> BẮT BUỘC:
> 1. Không bịa mã sách hoặc tình trạng sách ngoài dữ liệu Backend cung cấp.
> 2. Không gửi dữ liệu cá nhân độc giả cho AI nếu chức năng chỉ cần dữ liệu sách.
> 3. Có test case cho: câu hỏi mơ hồ, sách không tồn tại, sách hết."

## Prompt chuẩn hóa và thay máu CSDL Sách (2026‑08‑28)

> "Quy tắc:
> - Kiểm tra bảng Thể loại đã có mã TL_OTO chưa, chưa có thì tạo mới.
> - Kiểm tra sách trùng tên trong DB trước khi thêm; nếu trùng, liệt kê và hỏi xác nhận, không tự động ghi đè hoặc tạo trùng.
> - Mỗi sách sinh book_id theo đúng quy tắc mã hiện có của hệ thống.
> - Số lượng mặc định 5 nếu chưa có thông tin khác, tự tạo BookCopy tương ứng.
> - KHÔNG bịa thêm sách ngoài danh sách dưới đây."
