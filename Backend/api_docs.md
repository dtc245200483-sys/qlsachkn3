# Tài liệu API Backend — Hệ thống quản lý thư viện có tích hợp AI

Phiên bản: 0.21.0 (2026-08-10) — phạm vi: chức năng 1–8 + YC-2026-08-09-002 + Đợt A + Đợt C + Hồ sơ cá nhân + Validation + Phạt bằng ĐIỂM + Phân quyền độc giả + Đặt trước + DAT_TRUOC + Xoá lịch sử đặt trước + **Export CSV đặt trước + Admin accounts chỉ tạo thủ thư**.

## Thông tin chung

- Base URL: `http://localhost:8000`
- Định dạng dữ liệu: `application/json`
- Xác thực: gửi token qua header `Authorization: Bearer <token>` (token lấy từ API login/register).
- Khi lỗi, server trả JSON: `{"detail": "<mô tả lỗi>"}`.

## Danh sách role hợp lệ

| Role | Vai trò | Được phép làm |
|---|---|---|
| `admin` | Quản trị viên | Kế thừa quyền thủ thư **NGOẠI TRỪ thao tác phiếu mượn/trả/gia hạn** (mượn/trả chỉ `librarian`) + quản lý tài khoản, danh mục thể loại/NXB, cấu hình thư viện/AI, audit log, backup/restore |
| `librarian` | Thủ thư | Đăng nhập, quản lý sách/độc giả, lập/trả/gia hạn phiếu mượn, duyệt/từ chối yêu cầu, xử lý đặt trước (fulfill/cancel), đọc cấu hình thư viện |
| `reader` | Độc giả | Đăng ký, đăng nhập, tra cứu sách, gửi yêu cầu mượn/trả/gia hạn, đặt trước/xem/huỷ đặt trước của mình, xem lịch sử mượn/trả/phạt, xem thông báo của mình |

`admin` **không xử lý mượn/trả/gia hạn và không xử lý đặt trước** (gọi `/api/borrows*`, `/api/requests/*/approve|reject`, `/api/reservations*` với token admin → `403`).

### Nhóm quyền admin-only (YC-2026-08-09-002)

1. Quản lý tài khoản thủ thư + độc giả (tạo/sửa/khoá/xoá).
2. Cấu hình tham số thư viện (PUT) và cấu hình AI Engine.
3. Xem audit log toàn hệ thống, sao lưu và phục hồi CSDL.
4. Quản lý danh mục thể loại/NXB (Đợt A — UC25).

## Danh sách endpoint

| Chức năng | HTTP Method | Endpoint | Role |
|---|---|---|---|
| Đăng nhập | POST | `/api/auth/login` | Không cần token |
| Đăng ký độc giả | POST | `/api/auth/register` | Không cần token |
| Danh sách/tra cứu sách | GET | `/api/books?q=&theLoai=&trangThai=` | Mọi role đã đăng nhập |
| Thêm sách | POST | `/api/books` | `librarian`, `admin` |
| Sửa sách | PUT | `/api/books/{ma}` | `librarian`, `admin` |
| Xoá sách | DELETE | `/api/books/{ma}` | `librarian`, `admin` |
| Quản lý độc giả | GET/POST/PUT/DELETE | `/api/readers[/{ma}]` | GET: `librarian`, `admin`; POST/PUT/DELETE: chỉ `admin` |
| Khoá/mở khoá thẻ độc giả | PUT | `/api/readers/{ma}/lock` | `librarian`, `admin` |
| Lập phiếu mượn | POST | `/api/borrows` | `librarian` |
| Trả sách | PUT | `/api/borrows/{ma}/return` | `librarian` |
| Gia hạn | PUT | `/api/borrows/{ma}/renew` | `librarian` |
| Thu phạt | POST | `/api/borrows/{ma}/collect-fine` | `librarian` |
| Danh sách phiếu mượn | GET | `/api/borrows?docGia=&trangThai=` | `librarian` |
| Lịch sử của tôi | GET | `/api/borrows/me` | `reader` |
| Xoá 1 phiếu lịch sử đã trả | DELETE | `/api/borrows/me/{ma_phieu}` | `reader` |
| Xoá toàn bộ lịch sử đã trả | DELETE | `/api/borrows/me` | `reader` |
| Gửi yêu cầu | POST | `/api/requests` | `reader` |
| Danh sách yêu cầu | GET | `/api/requests` | `reader` (của mình); `librarian`, `admin` (tất cả) |
| Duyệt yêu cầu | PUT | `/api/requests/{ma}/approve` | `librarian` |
| Từ chối yêu cầu | PUT | `/api/requests/{ma}/reject` | `librarian` |
| Xoá 1 yêu cầu đã xử lý | DELETE | `/api/requests/me/{ma_yeu_cau}` | `reader` |
| Xoá lịch sử yêu cầu đã xử lý | DELETE | `/api/requests/me` | `reader` |
| Cấu hình thư viện | GET/PUT | `/api/admin/config/library` | GET: `librarian`, `admin`; PUT: `admin` |
| Cấu hình AI | GET/PUT | `/api/admin/config/ai` | `admin` |
| Audit log | GET | `/api/admin/audit-logs` | `admin` |
| Sao lưu CSDL | POST | `/api/admin/backup` | `admin` |
| Phục hồi CSDL | POST | `/api/admin/restore` | `admin` |
| Quản lý tài khoản | POST/GET/PUT/DELETE | `/api/admin/accounts[/{id}]` | `admin` |
| Quản lý thể loại | GET/POST/PUT/DELETE | `/api/admin/categories[/{ma}]` | `admin` |
| Quản lý NXB | GET/POST/PUT/DELETE | `/api/admin/publishers[/{ma}]` | `admin` |
| Danh sách đặt trước | GET | `/api/reservations?trangThai=` | `reader` (của mình), `librarian` (tất cả) |
| Đặt trước sách | POST | `/api/reservations` | `reader` |
| Huỷ đặt trước | PUT | `/api/reservations/{ma_dat}/cancel` | `reader` (đang chờ của mình), `librarian` (chờ/sẵn sàng) |
| Đánh dấu sách sẵn sàng | PUT | `/api/reservations/{ma_dat}/fulfill` | `librarian` |
| Xác nhận đã lấy (lập phiếu mượn) | PUT | `/api/reservations/{ma_dat}/borrow` | `librarian` |
| Xoá 1 đặt trước đã xử lý | DELETE | `/api/reservations/me/{ma_dat}` | `reader` |
| Xoá toàn bộ đặt trước đã xử lý | DELETE | `/api/reservations/me` | `reader` |
| Thông báo của tôi | GET | `/api/notifications` | `reader` |
| Sách mượn nhiều nhất | GET | `/api/stats/top-books?limit=` | `librarian`, `admin` |
| Độc giả hoạt động nhất | GET | `/api/stats/top-readers` | `librarian`, `admin` |
| Sách đang quá hạn | GET | `/api/stats/overdue-books` | `librarian`, `admin` |
| Xuất danh sách sách | GET | `/api/export/books.csv` | `librarian`, `admin` |
| Xuất danh sách phiếu mượn | GET | `/api/export/borrows.csv` | `librarian`, `admin` |
| Xuất báo cáo thống kê | GET | `/api/export/report.csv` | `librarian`, `admin` |
| Xuất danh sách đặt trước | GET | `/api/export/reservations.csv` | `librarian`, `admin` |
| Xem hồ sơ của tôi | GET | `/api/profile/me` | Mọi role đã đăng nhập |
| Cập nhật hồ sơ của tôi | PUT | `/api/profile/me` | Mọi role đã đăng nhập |
| Đổi mật khẩu của tôi | PUT | `/api/profile/me/password` | Mọi role đã đăng nhập |
| Upload ảnh đại diện | POST | `/api/profile/me/avatar` | Mọi role đã đăng nhập |

## 1. Đăng nhập — POST `/api/auth/login`

```json
{ "username": "admin", "password": "mat-khau" }
```

Response 200: `{ "token", "role", "role_display", "name" }` — `role_display` là nhãn tiếng Việt: `admin → Quản trị viên`, `librarian → Thủ thư`, `reader → Độc giả`. Lỗi: `401` sai tài khoản/mật khẩu hoặc tài khoản bị khoá.

## 2. Đăng ký độc giả — POST `/api/auth/register`

```json
{
  "username": "docgia01",
  "password": "mat-khau-6-ky-tu",
  "hoTen": "Nguyễn Văn A",
  "email": "a@example.com",
  "soDienThoai": "0901234567",
  "loaiDocGia": "sinh_vien"
}
```

Response 200: `{ "token", "role": "reader", "role_display": "Độc giả", "name", "reader_ma" }` — tự tạo `Reader` + tài khoản `User` và liên kết `reader_id`. Lỗi: `409` trùng username/email.

Validation chung (áp dụng register, profile, admin accounts):

- `hoTen` — bắt buộc, ≥ 2 từ, mỗi từ ≥ 2 ký tự, không chứa số/ký tự đặc biệt.
- `email` — bắt buộc, đúng định dạng ICTU: `^[A-Za-z0-9._%+-]+@ictu\.edu\.vn$`; trùng email (Users hoặc Readers) → `409`.
- `soDienThoai` — bắt buộc, SĐT Việt Nam: `^(0|\+84)(3|5|7|8|9)\d{8}$`.
- Vi phạm → `422` kèm thông báo rõ.

## 3. Tra cứu sách — GET `/api/books`

Query params tùy chọn (kết hợp được):

| Param | Ý nghĩa | Ví dụ |
|---|---|---|
| `q` | Tìm chứa chuỗi trong `ten` HOẶC `tacGia`, không phân biệt hoa thường | `?q=python` |
| `theLoai` | Lọc chính xác thể loại | `?theLoai=Công nghệ` |
| `trangThai` | `con` (soLuong > 0) hoặc `dang_muon` (soLuong = 0 hoặc đang có phiếu mượn chưa trả) | `?trangThai=con` |
| `sort` | Sắp xếp theo `ten`, `tacGia`, `namXb`, `soLuong` (mặc định `ten`) | `?sort=namXb` |
| `order` | `asc` hoặc `desc` (mặc định `asc`) | `?order=desc` |

Lọc (`q`, `theLoai`, `trangThai`) chạy trước, sắp xếp sau; kèm tie-break theo `ma` để thứ tự ổn định. Không truyền param → trả toàn bộ như cũ (mặc định `ten asc`). Sách có field tùy chọn `theLoaiId`, `nxbId` (liên kết danh mục), vẫn giữ `theLoai`/`nxb` text để UI cũ hoạt động.

## 4–6. CRUD sách

- `POST /api/books` — body gồm `ma, ten, tacGia, theLoai, nxb, namXb, soLuong` + tùy chọn `theLoaiId, nxbId`. Lỗi: `409` trùng mã, `422` thể loại/NXB không tồn tại.
- `PUT /api/books/{ma}` — sửa (mã lấy từ đường dẫn).
- `DELETE /api/books/{ma}` — xoá.

## 7. Quản lý độc giả — `/api/readers`

Fields: `ma, hoTen, email, soDienThoai, loaiDocGia (sinh_vien/giang_vien/khac), trangThaiThe (hoat_dong/khoa), diem_svnet (mặc định 100), ngayTao`.

- `GET /api/readers?q=` — danh sách + tìm theo mã/họ tên (`librarian`, `admin`).
- `POST /api/readers` — tạo (chỉ `admin`); trùng mã hoặc email → `409`.
- `PUT /api/readers/{ma}` — sửa thông tin (chỉ `admin`).
- `PUT /api/readers/{ma}/lock` — **khoá/mở khoá thẻ** (body `{ "trangThaiThe": "hoat_dong"|"khoa" }`) — `librarian` + `admin`; khoá thẻ sẽ **khoá luôn tài khoản đăng nhập liên kết** (`Users.is_active = false`), mở khoá thì đăng nhập lại bình thường.
- `DELETE /api/readers/{ma}` — xoá (chỉ `admin`).

`Readers` (dữ liệu độc giả) tách biệt với `Users` (tài khoản đăng nhập), liên kết qua `Users.reader_id`.

## 8. Mượn/trả/gia hạn/phạt — `/api/borrows`

### 8.1 Lập phiếu — POST `/api/borrows`

```json
{
  "ma_phieu": "PM001",
  "ma_doc_gia": "DG001",
  "items": [ { "ma_sach": "S001", "so_luong": 1 } ]
}
```

Quy tắc: thẻ `hoat_dong`; sách còn > 0 và đủ; tổng ≤ `max_books_at_once`; `han_tra = ngay_muon + max_borrow_days`; tự giảm `soLuong`. Lỗi: `400/404/409`.

### 8.2 Trả — PUT `/api/borrows/{ma}/return`

Tăng lại `soLuong`, ghi `ngay_tra`, chuyển `da_tra`; nếu quá hạn thêm `FineHistory`: `so_diem = so_ngay_qua_han * overdue_fine_points_per_day` (đơn vị **điểm**, mặc định 2 điểm/ngày).

Response: `{ "message", "ngay_tra", "fine": { "so_ngay_qua_han", "so_diem" } | null }`.

### 8.3 Gia hạn — PUT `/api/borrows/{ma}/renew`

`han_tra += max_borrow_days`, tối đa **1 lần**; nếu đang quá hạn tính phạt trước.

### 8.4 Danh sách — GET `/api/borrows?docGia=&trangThai=`

Mỗi phiếu trả về kèm mảng `fines` với `{ so_ngay_qua_han, so_diem, da_thu, ngay_thu }` — Frontend hiển thị nút "Thu phạt" chỉ khi `da_thu = false`.

### 8.5 Thu phạt (trừ điểm SVNET) — POST `/api/borrows/{ma}/collect-fine`

Role: chỉ `librarian` (admin/reader → `403`).

- Phiếu phải `da_tra`; nếu chưa trả → `400` `"Phiếu chưa trả, không thể thu phạt."`.
- Phải có `FineHistory` chưa thu (`da_thu = false`); không có → `400` `"Không có phạt để thu."`.
- Phạt tính bằng **điểm**: `so_diem = so_ngay_qua_han × overdue_fine_points_per_day` (mặc định 2 điểm/ngày); khi thu, `so_diem_da_thu = tổng so_diem` của các phạt chưa thu, trừ vào `Readers.diem_svnet` (mặc định 100, không âm), đánh dấu phạt đã thu, ghi `ngay_thu`.

Response 200:

```json
{
  "message": "Đã trừ điểm SVNET.",
  "so_diem_da_thu": 4,
  "diem_con_lai": 96,
  "ngay_thu": "2026-08-09T20:00:00"
}
```

Audit log: `COLLECT_FINE`.

## 9. Lịch sử của độc giả — GET `/api/borrows/me`

Role `reader`, tài khoản phải có `reader_id`. Trả mảng phiếu của chính độc giả, mỗi phiếu kèm `details` + `fines`.

### Xoá lịch sử mượn (reader tự xoá)

- `DELETE /api/borrows/me/{ma_phieu}` — xoá 1 phiếu **đã trả** (`da_tra`) của chính mình.
- `DELETE /api/borrows/me` — xoá toàn bộ phiếu **đã trả** của mình, trả `{ "so_phieu_da_xoa": n }`.

Ràng buộc:

- Chỉ role `reader`; chỉ phiếu thuộc `reader_id` của tài khoản (phiếu của người khác → `404`).
- Chỉ xoá phiếu `da_tra`; phiếu `dang_muon` → `400` (không xoá để tránh lệch số lượng sách).
- Khi xoá sẽ xoá luôn `BorrowDetails` và `FineHistory` liên quan; **không** thay đổi `soLuong` sách.

Audit log: `DELETE_BORROW_HISTORY`, `DELETE_BORROW_HISTORY_ALL`.

## 10. Yêu cầu mượn/trả/gia hạn/đặt trước — `/api/requests`

- `POST /api/requests` (reader): loai `MUON` cần `items`; `DAT_TRUOC` cần `ma_sach` (hoặc `items` có đúng 1 sách) + thẻ `hoat_dong`; `TRA`/`GIA_HAN` cần `ma_phieu` thuộc về mình và đang `dang_muon` (GIA_HAN chỉ khi chưa gia hạn).
- `GET /api/requests?maDocGia=&trangThai=` — reader chỉ thấy của mình.
- `PUT /api/requests/{ma}/approve` (librarian): MUON → tạo phiếu (`ma_phieu = "PM" + ma_yeu_cau`); TRA → trả + tính phạt; GIA_HAN → gia hạn; **DAT_TRUOC → tạo đặt trước thật** (tái dùng logic `/api/reservations`): chỉ khi sách đang hết (soLuong = 0 hoặc đang mượn hết) → nếu còn → `400 "Sách còn, không cần đặt trước"`; đặt trùng active → `409`; tạo `DatTruoc` mã `RV...` trạng thái `CHO_XU_LY`, yêu cầu chuyển `DA_DUYET` (ma_phieu = null), audit `CREATE_RESERVATION` + `APPROVE_REQUEST`.
- `PUT /api/requests/{ma}/reject` — chuyển `TU_CHOI`.

Trạng thái: `CHO_XU_LY` → `DA_DUYET` hoặc `TU_CHOI`.

## 11. Cấu hình thư viện — `/api/admin/config/library`

GET: `admin`/`librarian`. PUT (chỉ `admin`): `{ "max_borrow_days", "overdue_fine_points_per_day", "max_books_at_once" }` — điểm phạt mặc định 2/ngày.

## 12. Cấu hình AI — `/api/admin/config/ai`

Chỉ `admin`. GET trả `api_key_masked` (che), không trả key đầy đủ. PUT nhận `provider, model, api_key, prompt_template` (field nào gửi thì đổi field đó; `api_key` rỗng = xoá key).

## 13. Audit log — GET `/api/admin/audit-logs?limit=&action=`

Chỉ `admin`. Tự ghi log cho: login/register, CRUD sách/độc giả, phiếu mượn/trả/gia hạn, yêu cầu, tài khoản, danh mục, cấu hình, backup/restore.

## 14. Sao lưu — POST `/api/admin/backup`

Chỉ `admin`. Tạo file `.bak` trong thư mục backup mặc định của SQL Server (hoặc `BACKUP_DIR`).

## 15. Phục hồi — POST `/api/admin/restore`

Chỉ `admin`. Body `{ "file_path": "C:\\...\\LibraryDB_....bak" }`. Thực hiện `RESTORE DATABASE ... WITH REPLACE` — **thay thế toàn bộ dữ liệu hiện tại**. Lỗi `404` nếu file không tồn tại/không phải `.bak`.

## 16. Quản lý tài khoản — `/api/admin/accounts`

Chỉ `admin`.

Mỗi tài khoản trả về `role_display` (tiếng Việt): `librarian → Thủ thư`, `reader → Độc giả`.

- `POST` — `{ "username", "password", "ho_ten", "email", "so_dien_thoai", "role": "librarian" }` — **chỉ nhận role `librarian`**; gửi `reader` → `400 "Độc giả tự đăng ký qua /api/auth/register"`. Email/SĐT bắt buộc + validation chung.
- `GET ?role=` — danh sách tài khoản thủ thư + độc giả (mỗi tài khoản trả thêm `email`, `so_dien_thoai`).
- `PUT /{id}` — sửa `ho_ten`, `email`, `so_dien_thoai`, `password`, `is_active` (khoá/mở khoá), `role`, `reader_id` (cùng validation).
- `DELETE /{id}` — xoá.

## 17. Danh mục thể loại/NXB — `/api/admin/categories`, `/api/admin/publishers`

Chỉ `admin`. CRUD `{ "ma", "ten" }` (PUT chỉ cần `ten`). Không xoá được mục đang được sách dùng.

## 18. Đặt trước sách — `/api/reservations`

Trạng thái: `CHO_XU_LY` → `SAN_SANG` → `DA_MUON`; hoặc `HUY`.

### 18.1 Danh sách — GET `/api/reservations?trangThai=`

`reader` chỉ thấy đặt trước của mình (theo `reader_id`); `librarian` xem tất cả; `admin` → `403`.

### 18.2 Đặt trước — POST `/api/reservations`

Role: `reader`. Body `{ "ma_sach": "S001" }` (Frontend có thể gửi thêm `ma_doc_gia` — Backend bỏ qua, dùng `reader_id` từ token).

Chỉ cho phép khi sách đang **hết**: `soLuong = 0` hoặc toàn bộ bản đang có phiếu `dang_muon` chưa trả. Nếu còn sách → `400` `"Sách còn, không cần đặt trước"`. Đặt trùng (cùng sách + cùng độc giả còn `CHO_XU_LY`/`SAN_SANG`) → `409`.

Response 200 (đúng contract Frontend):

```json
{
  "ma_dat": "RV20260809190000123",
  "ma_sach": "S001",
  "ten_sach": "Lập trình Python cơ bản",
  "ma_doc_gia": "DG001",
  "ngay_dat": "2026-08-09T19:00:00",
  "trang_thai": "CHO_XU_LY"
}
```

### 18.3 Huỷ — PUT `/api/reservations/{ma_dat}/cancel`

Role: `reader` (chỉ phiếu của mình) hoặc `librarian` (mọi phiếu). Chỉ huỷ khi `CHO_XU_LY` → `HUY`; trạng thái khác → `400`; phiếu không thuộc reader → `404`.

### 18.4 Đánh dấu sẵn sàng — PUT `/api/reservations/{ma_dat}/fulfill`

Role: chỉ `librarian`. Chỉ khi `CHO_XU_LY` → `SAN_SANG`; trạng thái khác → `400`.

### Tích hợp nghiệp vụ

- Khi trả sách: nếu có đặt trước `CHO_XU_LY` cho sách đó → tự đổi thành `SAN_SANG` (ưu tiên người đặt trước kế tiếp theo `ngay_dat`; mỗi bản trả thúc đẩy 1 đặt trước).
- Khi gia hạn: **từ chối `400`** nếu có đặt trước `CHO_XU_LY`/`SAN_SANG` cho bất kỳ sách nào trong phiếu (UC17).

Audit log: `CREATE_RESERVATION`, `CANCEL_RESERVATION`, `FULFILL_RESERVATION`, `RESERVATION_READY`.

### 18.5 Xoá lịch sử đặt trước (reader tự xoá)

- `DELETE /api/reservations/me/{ma_dat}` — xoá 1 đặt trước **đã xử lý** (`HUY`/`DA_MUON`) của mình; không tồn tại/không thuộc mình → `404`; đang `CHO_XU_LY`/`SAN_SANG` → `400`.
- `DELETE /api/reservations/me` — xoá toàn bộ đặt trước `HUY`/`DA_MUON` của mình, trả `{ "so_phieu_da_xoa": n }`; giữ nguyên `CHO_XU_LY`/`SAN_SANG`.

Audit log: `DELETE_RESERVATION_HISTORY`, `DELETE_RESERVATION_HISTORY_ALL`.

## 19. Thông báo cho độc giả — GET `/api/notifications` (UC11)

Role: chỉ `reader` (theo `reader_id`); librarian/admin → `403`. API **tự tổng hợp động** từ dữ liệu hiện có, không lưu trạng thái đã đọc (Frontend đang lưu `da_doc` tạm ở localStorage):

- `SAP_HET_HAN` — phiếu mượn đang `dang_muon` của reader còn ≤ 3 ngày đến hạn.
- `QUA_HAN` — phiếu mượn đang `dang_muon` đã quá hạn.
- `SACH_SAN_SANG` — đặt trước của reader có `trang_thai = SAN_SANG`.

Response 200 — mảng sắp xếp theo `ngay` giảm dần:

```json
[
  {
    "id": "BORROW:PM001",
    "loai": "SAP_HET_HAN",
    "noi_dung": "Phiếu PM001 hạn trả 12/08/2026 — còn 2 ngày",
    "ngay": "2026-08-12T09:00:00",
    "da_doc": false
  },
  {
    "id": "RES:RV20260809190000123",
    "loai": "SACH_SAN_SANG",
    "noi_dung": "Đặt trước RV20260809190000123 — Sách ABC đã sẵn sàng",
    "ngay": "2026-08-09T19:00:00",
    "da_doc": false
  }
]
```

`id` dùng tiền tố `BORROW:`/`RES:` khớp với `notifications-core.js`. Phiếu đã trả (`da_tra`) không xuất hiện. `da_doc` luôn `false` vì Backend chưa lưu trạng thái đọc; nếu sau này Frontend cần lưu, sẽ thêm migration 0008 bảng `ThongBao` + `PUT /api/notifications/{id}/read`.

## 20. Thống kê — `/api/stats` (UC20/UC28)

Role: `librarian` + `admin` (báo cáo, không phải thao tác mượn/trả); `reader` → `403`.

### 20.1 Sách mượn nhiều nhất — GET `/api/stats/top-books?limit=10`

Đếm từ `BorrowDetails`, sắp giảm dần theo số lần mượn; `limit` mặc định 10, tối đa 100.

```json
[
  { "ma_sach": "S001", "ten_sach": "Lập trình Python cơ bản", "so_lan_muon": 12 }
]
```

### 20.2 Độc giả hoạt động nhất — GET `/api/stats/top-readers`

Đếm số phiếu mượn (`BorrowSlips`) của từng độc giả, sắp giảm dần, giới hạn 10.

```json
[
  { "ma_doc_gia": "DG001", "ho_ten": "Nguyễn Văn A", "so_phieu_muon": 8 }
]
```

### 20.3 Sách đang quá hạn — GET `/api/stats/overdue-books`

Phiếu `dang_muon` có `han_tra` trước hôm nay; mỗi sách trong phiếu là 1 dòng.

```json
[
  {
    "ma_phieu": "PM001",
    "ma_sach": "S001",
    "ten_sach": "Lập trình Python cơ bản",
    "ma_doc_gia": "DG001",
    "ho_ten": "Nguyễn Văn A",
    "so_ngay_qua_han": 3
  }
]
```

## 21. Xuất dữ liệu — `/api/export` (chức năng 8)

Role: `librarian` + `admin` (báo cáo UC20/28); `reader` → `403`. Cả 3 endpoint trả `text/csv; charset=utf-8`, header `Content-Disposition: attachment` với filename có ngày giờ (VD `danh_sach_sach_20260809_193000.csv`), nội dung có **UTF-8 BOM** để mở Excel không lỗi tiếng Việt.

### 21.1 Danh sách sách — GET `/api/export/books.csv`

Header: `Mã,Tên,Tác giả,Thể loại,NXB,Năm,Số lượng`.

### 21.2 Danh sách phiếu mượn — GET `/api/export/borrows.csv`

Header: `Mã phiếu,Mã độc giả,Ngày mượn,Hạn trả,Ngày trả,Trạng thái,Số ngày quá hạn,Điểm phạt` — trạng thái hiển thị `Đang mượn`/`Đã trả`, điểm phạt lấy từ `FineHistory.so_diem`.

### 21.3 Báo cáo thống kê — GET `/api/export/report.csv`

Gộp 3 phần, mỗi phần có tiêu đề và header rõ ràng:

- `SÁCH MƯỢN NHIỀU` → `Mã sách,Tên sách,Số lần mượn`.
- `ĐỘC GIẢ HOẠT ĐỘNG` → `Mã độc giả,Họ tên,Số phiếu mượn`.
- `SÁCH QUÁ HẠN` → `Mã phiếu,Mã sách,Tên sách,Mã độc giả,Họ tên,Số ngày quá hạn`.

### 21.4 Danh sách đặt trước — GET `/api/export/reservations.csv`

Header: `Mã đặt,Mã sách,Tên sách,Độc giả,Ngày đặt,Trạng thái` — dữ liệu từ `DatTruoc` kèm tên sách/tên độc giả, UTF-8 BOM, filename `danh_sach_dat_truoc_<thời gian>.csv`; `librarian`/`admin`, reader → 403.

## 22. Hồ sơ cá nhân — `/api/profile/me`

Mọi role đã đăng nhập, chỉ thao tác thông tin **của mình**.

### 22.1 Xem hồ sơ — GET `/api/profile/me`

Response 200 (khớp `profileOut` Frontend):

```json
{
  "username": "docgia1",
  "ho_ten": "Nguyễn Văn An",
  "role": "reader",
  "email": "DTC245200486@ictu.edu.vn",
  "so_dien_thoai": "0912345004",
  "loai_doc_gia": "sinh_vien",
  "avatar_url": "/static/avatars/docgia1.png"
}
```

`email`, `so_dien_thoai`, `loai_doc_gia` lấy từ `Readers` khi tài khoản có `reader_id`; admin/librarian lấy `email`/`so_dien_thoai` từ `Users` (tài khoản cũ chưa có → rỗng, cập nhật qua PUT sẽ lưu).

### 22.2 Cập nhật — PUT `/api/profile/me`

Body tùy chọn: `ho_ten`, `email`, `so_dien_thoai`, `loai_doc_gia` (`sinh_vien`/`giang_vien`/`khac`).

- Cả 3 role: cập nhật `ho_ten`, `email`, `so_dien_thoai` theo validation chung; reader thêm `loai_doc_gia`.
- Email trùng (Users hoặc Readers) → `409`.

Audit log: `UPDATE_PROFILE`.

### 22.3 Đổi mật khẩu — PUT `/api/profile/me/password`

```json
{
  "mat_khau_cu": "mat-khau-cu",
  "mat_khau_moi": "mat-khau-moi-6-ky-tu",
  "xac_nhan": "mat-khau-moi-6-ky-tu"
}
```

`xac_nhan` tùy chọn (Frontend tự kiểm tra phía client; nếu gửi và khác `mat_khau_moi` → `400`). Sai mật khẩu cũ → `400`; mật khẩu mới ≥ 6 ký tự. Audit log: `CHANGE_PASSWORD`.

### 22.4 Upload ảnh đại diện — POST `/api/profile/me/avatar`

Multipart field `file`, chỉ PNG/JPG, tối đa **2MB** (sai loại/quá lớn → `400`). Lưu tại `Backend/static/avatars/{username}.png|.jpg`, xoá ảnh cũ khi đổi; ảnh xem được qua `/static/avatars/...` (StaticFiles đã mount).

Response: `{ "avatar_url": "/static/avatars/docgia1.png" }`. Audit log: `UPDATE_AVATAR`.

## Cấu hình sẵn để dán vào `Frontend/js/api.js`

(Dành cho màn hình đăng nhập + quản lý sách hiện tại; các API mới mục 7–22 sẽ được Frontend thêm khi dựng UI tương ứng.)

```javascript
var config = {
  baseUrl: "http://localhost:8000",
  endpoints: {
    login: "/api/auth/login",
    books: "/api/books",
    createBook: "/api/books",
    updateBook: "/api/books/{id}",
    deleteBook: "/api/books/{id}"
  },
  fieldMap: {
    login: {
      username: "username",
      password: "password"
    },
    loginResponse: {
      token: "token",
      role: "role",
      name: "name"
    },
    book: {
      ma: "ma",
      ten: "ten",
      tacGia: "tacGia",
      theLoai: "theLoai",
      nxb: "nxb",
      namXb: "namXb",
      soLuong: "soLuong"
    }
  },
  roleMap: {
    admin: "admin",
    librarian: "librarian",
    reader: "reader"
  }
};
```
