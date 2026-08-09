# Backend — Hệ thống quản lý thư viện có tích hợp AI

Công nghệ: Python FastAPI + SQLAlchemy + Microsoft SQL Server (ODBC Driver 17, Windows Authentication), Alembic cho migration.

## Cài đặt

```powershell
cd "D:\ung dung tri tue nhan ao\app\Backend"
pip install -r requirements.txt
```

## Tạo database và bảng

Đảm bảo SQL Server instance `localhost\QUANGHUNG` đang chạy, rồi chạy:

```powershell
sqlcmd -S "localhost\QUANGHUNG" -E -C -Q "IF DB_ID('LibraryDB') IS NULL CREATE DATABASE LibraryDB;"
python -m alembic upgrade head
```

Kết nối mặc định lấy từ file `.env` (`DATABASE_URL`), tài khoản dùng Windows Authentication.

## Chạy server

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

API docs: [api_docs.md](api_docs.md)

## API Admin (YC-2026-08-09-002 — ranh giới quyền Admin vs Librarian)

- Cấu hình thư viện: `GET/PUT /api/admin/config/library` — đọc: `admin`/`librarian`; ghi: chỉ `admin`.
- Cấu hình AI: `GET/PUT /api/admin/config/ai` — chỉ `admin` (API key trả về đã che).
- Audit log: `GET /api/admin/audit-logs` — chỉ `admin`.
- Backup CSDL: `POST /api/admin/backup` — chỉ `admin` (mặc định vào thư mục backup của SQL Server; đổi qua biến `BACKUP_DIR`).

Bảng `Users` có thêm cột `is_active` để khoá/mở khoá tài khoản. Các bảng `LibraryConfig`, `AIConfig`, `AuditLog` được tạo ở migration `0002`, và migration `0003` chuyển cột văn bản sang NVARCHAR(MAX).

## Quản lý độc giả (chức năng 3)

- Bảng `Readers` tạo ở migration `0004`: mã độc giả, họ tên, email, số điện thoại, loại độc giả (`sinh_vien`/`giang_vien`/`khac`), trạng thái thẻ (`hoat_dong`/`khoa`), ngày tạo.
- API: `GET/POST /api/readers`, `PUT /api/readers/{ma}`, `DELETE /api/readers/{ma}` — chi tiết trong [api_docs.md](api_docs.md) mục 11.
- `Readers` (dữ liệu độc giả) tách biệt với `Users` (tài khoản đăng nhập).

## Mượn/trả/gia hạn/phạt (chức năng 4)

- Migration `0005` tạo 3 bảng: `BorrowSlips`, `BorrowDetails`, `FineHistory`.
- API: `POST /api/borrows` (lập phiếu, giảm số lượng sách, tự tính `han_tra`), `PUT /api/borrows/{ma}/return` (trả, tăng số lượng, tự tính phạt nếu quá hạn), `PUT /api/borrows/{ma}/renew` (gia hạn tối đa 1 lần), `GET /api/borrows` (lọc theo độc giả/trạng thái) — chi tiết trong [api_docs.md](api_docs.md) mục 12.
- Phạt: `so_tien = so_ngay_qua_han * overdue_fine_per_day` (tham số trong `LibraryConfig`).

## Đợt A — Tương thích Use Case

- Migration `0006`: bảng `TheLoai`, `Nxb` (kèm dữ liệu mẫu), bảng `YeuCau`; `Books` thêm `theLoaiId`/`nxbId` (giữ text cũ); `Users` thêm `reader_id` liên kết `Readers`.
- API mới: đăng ký độc giả (`/api/auth/register`), lịch sử của độc giả (`/api/borrows/me`), yêu cầu mượn/trả/gia hạn (`/api/requests` + approve/reject), quản lý tài khoản (`/api/admin/accounts`), danh mục thể loại/NXB (`/api/admin/categories`, `/api/admin/publishers`), restore (`/api/admin/restore`).
- Reader có thể xoá lịch sử mượn đã trả của mình: `DELETE /api/borrows/me/{ma_phieu}` (1 phiếu) và `DELETE /api/borrows/me` (toàn bộ phiếu `da_tra`).

## Đặt trước sách (chức năng 6)

- Migration `0007` tạo bảng `DatTruoc` (ma_dat, ma_sach, ma_doc_gia, ngay_dat, trang_thai, ngay_xu_ly; filtered unique index chống đặt trùng active; FK tới Books/Readers).
- API: `GET/POST /api/reservations`, `PUT /api/reservations/{ma_dat}/cancel`, `PUT /api/reservations/{ma_dat}/fulfill` — chi tiết trong [api_docs.md](api_docs.md) mục 18.
- Khi trả sách có đặt trước chờ → tự chuyển `SAN_SANG`; gia hạn bị từ chối nếu có đặt trước cho sách trong phiếu.
- Admin không xử lý mượn/trả/gia hạn và đặt trước (403); thủ thư xử lý borrow + đặt trước.

## Thông báo cho độc giả (UC11)

- `GET /api/notifications` (chỉ reader): tổng hợp động nhắc hạn trả (≤ 3 ngày / quá hạn) và đặt trước `SAN_SANG`; trả `{ id, loai, noi_dung, ngay, da_doc }` với `da_doc=false` (chưa lưu trạng thái đọc — Frontend đang dùng localStorage).

## Thống kê (chức năng 7)

- `GET /api/stats/top-books?limit=` — sách mượn nhiều nhất (đếm `BorrowDetails`).
- `GET /api/stats/top-readers` — độc giả hoạt động nhất (đếm `BorrowSlips`).
- `GET /api/stats/overdue-books` — sách quá hạn của phiếu `dang_muon` có `han_tra` trước hôm nay.
- Chỉ `librarian`/`admin` xem được; `reader` → 403.

## Xuất dữ liệu (chức năng 8)

- `GET /api/export/books.csv`, `GET /api/export/borrows.csv`, `GET /api/export/report.csv` — trả CSV UTF-8 có BOM, `Content-Disposition: attachment` filename kèm ngày giờ; chỉ `librarian`/`admin`.

## Thu phạt (UC19)

- Migration `0008`: `FineHistory` thêm `da_thu` + `ngay_thu`; `0009`: `Readers.diem_svnet`; `0011`: đổi toàn bộ phạt sang **điểm** — `LibraryConfig.overdue_fine_points_per_day` (mặc định 2), `FineHistory.so_diem`.
- Phạt = `so_ngay_qua_han × overdue_fine_points_per_day` (điểm). `POST /api/borrows/{ma}/collect-fine` (chỉ librarian) trả `{ message, so_diem_da_thu, diem_con_lai, ngay_thu }` và trừ `diem_svnet`.
- `GET /api/borrows` trả `fines` với `{ so_ngay_qua_han, so_diem, da_thu, ngay_thu }`; CSV `borrows.csv` cột `Điểm phạt`.

## Nhãn role tiếng Việt

Giá trị role gốc vẫn là `admin`/`librarian`/`reader` (không đổi để không vỡ logic). API login/register/accounts trả thêm `role_display`: `Quản trị viên`, `Thủ thư`, `Độc giả` — Frontend dùng field này để hiển thị tiếng Việt.

## Sắp xếp sách (KT2 tiêu chí 4)

`GET /api/books` hỗ trợ `sort` (`ten`/`tacGia`/`namXb`/`soLuong`, mặc định `ten`) và `order` (`asc`/`desc`, mặc định `asc`); kết hợp được với `q`, `theLoai`, `trangThai` (lọc trước, sắp xếp sau, tie-break `ma`).

## Hồ sơ cá nhân (mở rộng)

- `GET/PUT /api/profile/me` — xem/cập nhật hồ sơ của chính mình (`ho_ten`, `email`, `so_dien_thoai`, `loai_doc_gia` cho reader).
- `PUT /api/profile/me/password` — đổi mật khẩu (body `mat_khau_cu`, `mat_khau_moi`, `xac_nhan` tùy chọn).
- `POST /api/profile/me/avatar` — upload PNG/JPG ≤ 2MB, lưu `static/avatars/{username}.{ext}`, xem qua `/static/...`.
- Audit: `UPDATE_PROFILE`, `CHANGE_PASSWORD`, `UPDATE_AVATAR`.

## Hoàn thiện tài khoản & validation

- Migration `0010`: `Users` thêm `email` (unique, nullable — chỉ unique khi khác NULL) + `so_dien_thoai` (nullable).
- Validation dùng chung (register, profile, admin accounts): họ tên ≥ 2 từ (mỗi từ ≥ 2 ký tự, không số/ký tự đặc biệt); email bắt buộc định dạng ICTU `@ictu.edu.vn` (trùng → 409); SĐT Việt Nam `^(0|\+84)(3|5|7|8|9)\d{8}$`; sai → 422.
- GET/PUT `/api/profile/me` và `/api/admin/accounts` trả/lưu `email` + `so_dien_thoai` cho mọi role (reader đồng bộ sang `Readers`).

## Phân quyền quản lý độc giả

`POST`/`PUT`/`DELETE /api/readers...` chỉ `admin`; `GET /api/readers` cho `admin` + `librarian`; `PUT /api/readers/{ma}/lock` (khoá/mở khoá thẻ) cho `admin` + `librarian` — thủ thư không sửa được thông tin độc giả.

## Yêu cầu DAT_TRUOC

Yêu cầu (request) hỗ trợ loai `DAT_TRUOC`: reader gửi `ma_sach` (hoặc `items` 1 sách); khi thủ thư duyệt, Backend tạo đặt trước thật (`DatTruoc` mã `RV...`, trạng thái `CHO_XU_LY`) — chỉ khi sách hết, đặt trùng → 409.

## Xoá lịch sử đặt trước của reader

`DELETE /api/reservations/me` (xoá toàn bộ `HUY`/`DA_MUON`) và `DELETE /api/reservations/me/{ma_dat}` (xoá 1 phiếu) — chỉ reader, giữ nguyên `CHO_XU_LY`/`SAN_SANG`; audit `DELETE_RESERVATION_HISTORY[_ALL]`.

## Export CSV đặt trước + Admin accounts

- `GET /api/export/reservations.csv` — xuất đặt trước (Mã đặt, Mã sách, Tên sách, Độc giả, Ngày đặt, Trạng thái), UTF-8 BOM; librarian/admin.
- `POST /api/admin/accounts` chỉ nhận role `librarian`; gửi `reader` → `400 "Độc giả tự đăng ký qua /api/auth/register"`.

## Dữ liệu demo (seed)

Chạy 1 lần, idempotent (chạy lại không đè/không trùng). Backend phải đang chạy để tạo tài khoản qua API register:

```powershell
cd "D:\ung dung tri tue nhan ao\app\Backend"
python scripts/seed_demo.py            # seed dữ liệu
python scripts/seed_demo.py --verify   # seed + gọi API kiểm tra số liệu
```

Dữ liệu demo tạo ra (đánh dấu DEMO trong README/log, không đụng dữ liệu thật):

- Sách: dùng S001–S005 (tạo mới nếu chưa có).
- Độc giả: DG001 Nguyễn Văn An, DG002 Trần Thị Bích, DG003 Lê Minh Cường — email định dạng ICTU (`DTC2452004xx@ictu.edu.vn`).
- Tài khoản đăng nhập demo: `docgia1/docgia1` (liên kết DG001), `docgia2/docgia2` (liên kết DG002) — tạo qua `POST /api/auth/register`.
- Phiếu mượn: PM001 (đang mượn), PM002 (đã trả đúng hạn), PM003 (đã trả trễ 2 ngày → FineHistory), PM004 (đang mượn, hạn còn ≤ 3 ngày → thông báo `SAP_HET_HAN`).
- Đặt trước: RV001 `SAN_SANG` (S002), RV002 `CHO_XU_LY` (S005 đang hết).

Script còn **backfill email + SĐT cho tài khoản cũ** — email tự sinh theo tên người (bỏ dấu, nối liền, đuôi `@ictu.edu.vn`): Nguyễn Văn Huy → `nguyenvanhuy@ictu.edu.vn`, Trần Thị Thu Hà → `tranthithuha@ictu.edu.vn`, Lê Văn Nam → `levannam@ictu.edu.vn`, Nguyễn Văn An → `nguyenvanan@ictu.edu.vn`, Trần Thị Bích → `tranthibich@ictu.edu.vn`. Chạy lại không ghi đè SĐT đã có.
- Chi tiết trong [api_docs.md](api_docs.md) mục 1–17.

## Tạo tài khoản đăng nhập

Ở phạm vi hiện tại chỉ có API đăng nhập, chưa có API đăng ký tài khoản. Tài khoản `admin`, `librarian`, `reader` ban đầu tạo trực tiếp trong bảng `Users` qua SSMS/sqlcmd: chạy Python để sinh mật khẩu hash rồi thêm dòng vào bảng `Users`:

```powershell
python -c "from app.security import hash_password; print(hash_password('MatKhauCuaBan'))"
```

Sau đó dùng kết quả hash chèn vào `Users (username, password_hash, ho_ten, role)` với role là `admin`, `librarian` hoặc `reader`.
