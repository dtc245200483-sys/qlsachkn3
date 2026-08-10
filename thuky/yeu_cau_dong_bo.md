# Yêu cầu đồng bộ giữa các agent — do Thư Ký quản lý
File này là kênh trao đổi khi một agent cần agent khác thay đổi (theo quy tắc:
không tự sửa thư mục của agent khác).

---

## YC-2026-08-09-001 — Kết nối API Frontend ↔ Backend (chức năng 1, 2)

- Ngày tạo: 2026-08-09
- Người yêu cầu: Người dùng ("bạn kết nối api này giúp tôi")
- Gửi cho: **Frontend Agent**
- Trạng thái: HOÀN THÀNH (log [FRONTEND] 2026-08-09 07:41:41: đã nối api.js, test API + UI Chrome headless 12/12 PASS)

### Lý do
- Backend đã hoàn thiện API chức năng 1, 2 và cấp tài liệu (log [BACKEND]
  2026-08-09 07:02:48; file Backend/api_docs.md).
- Frontend/js/api.js hiện vẫn để config TRỐNG (baseUrl: "", endpoints rỗng,
  fieldMap rỗng) → UI chưa gọi được API thật.

### Việc cần làm (Frontend Agent)
1. Mở Backend/api_docs.md, phần "Cấu hình sẵn để dán vào Frontend/js/api.js".
2. Thay khối `config` hiện tại trong `window.API` ở Frontend/js/api.js bằng
   khối config từ tài liệu (gồm baseUrl, endpoints, fieldMap, roleMap).
3. Kiểm tra Backend đang chạy (uvicorn app.main:app --port 8000) và DB đã
   migration; thử đăng nhập + CRUD sách trên 2 màn hình index.html/books.html.
4. Gửi log cho Thư Ký theo định dạng:
   [FRONTEND] <thời gian> - Thay đổi: <mô tả> - Chức năng đề bài liên quan: 1, 2
   - API đang gọi: <endpoint đã nối> - Cần Backend bổ sung: <có/không>

### Khối config gốc (sao chép nguyên văn từ Backend/api_docs.md, có thể dùng luôn)

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

---

## YC-2026-08-09-002 — Ranh giới quyền Quản trị viên (Admin) vs Thủ thư (Librarian)

- Ngày tạo: 2026-08-09 07:49:46
- Người yêu cầu: Người dùng (xác nhận rõ ranh giới quyền; cảnh báo rủi ro
  Backend gộp admin + librarian thành 1 role)
- Gửi cho: **Backend Agent** (chính), **Frontend Agent**, **AI Engine Agent**
  (đọc để biết cấu hình AI thuộc quyền admin)
- Trạng thái: CHỜ CÁC AGENT TRIỂN KHAI

### Nguyên tắc
- Giữ đúng 3 vai trò đề bài: `admin`, `librarian`, `reader` — KHÔNG gộp
  admin + librarian thành role chung.
- Admin có các quyền dưới đây mà Librarian KHÔNG có.

### Quyền Admin-only (người dùng chốt)
1. Quản lý nhân sự/tài khoản hệ thống: tạo, sửa, xoá, khoá tài khoản
   THỦ THƯ. (Thủ thư chỉ thao tác tài khoản/thẻ ĐỘC GIẢ — chức năng 3.)
2. Cấu hình tham số lõi thư viện: số ngày mượn tối đa mặc định, mức phạt
   quá hạn/ngày, giới hạn số sách mượn cùng lúc. (Thủ thư chỉ áp dụng các
   quy định này — chức năng 4.)
3. Cấu hình AI Engine: cập nhật API Key (OpenAI/Gemini/Hugging Face...),
   thay đổi model AI, tinh chỉnh prompt template gốc. (Thủ thư chỉ dùng AI
   đã được setup sẵn.)
4. Xem nhật ký hoạt động (Audit Logs) toàn hệ thống (VD: biết thủ thư nào
   vừa xoá/thêm sách) và sao lưu CSDL (Backup).

### Việc cần làm (theo từng agent)
- **Backend**: thêm API + phân quyền `admin` cho 4 nhóm quyền trên; schema/
  migration mới nếu cần (bảng cấu hình hệ thống, cấu hình AI, audit log);
  KHÔNG gộp role.
- **Frontend**: UI quản trị cho admin (quản lý tài khoản thủ thư, cấu hình
  hệ thống, cấu hình AI, xem audit log/backup), ẩn theo role admin-only.
- **AI Engine**: đọc cấu hình model/API key/prompt do admin cài đặt (qua API
  Backend), không tự đọc file cấu hình nhạy cảm của admin.

### Lưu ý
- Mọi thay đổi phải gửi log cho Thư Ký theo định dạng chuẩn của từng agent.
- Khi triển khai xong, Backend cập nhật api_docs.md; Frontend cập nhật theo
  và gửi log; AI Engine gửi log nếu có thay đổi.

### Trạng thái cập nhật 2026-08-09 08:09:34
- **Backend: HOÀN THÀNH** — log [BACKEND] 2026-08-09 08:06:16; api_docs.md
  đã lên bản 0.2.0 (mục 6-10), migration 0002 + 0003.
- **Frontend: CHỜ xử lý** — chưa có code/UI admin.
- **AI Engine: CHỜ xử lý** — chưa có code dùng cấu hình AI.

### Trạng thái cập nhật 2026-08-09 09:50:40
- **Backend: HOÀN THÀNH** (đã thêm chức năng 3: /api/readers, api_docs 0.3.0).
- **Frontend: CHỜ xử lý** — mới có khung admin.js/requireAdmin, CHƯA nối API
  /api/admin/* và /api/readers, chưa có màn hình admin/độc giả.
- **AI Engine: CHỜ xử lý** — chưa có code.

---

## YC-2026-08-09-003 — Frontend: UI quản lý độc giả (chức năng 3) + hoàn tất UI admin (YC-002)

- Ngày tạo: 2026-08-09 09:50:40
- Người yêu cầu: Thư Ký (theo log Backend 09:49:03 + đối chiếu đề bài)
- Gửi cho: **Frontend Agent**
- Trạng thái: CHỜ FRONTEND XỬ LÝ

### Việc cần làm
1. UI quản lý độc giả theo api_docs.md bản 0.3.0 (mục 11): danh sách + tìm
   theo mã/tên, thêm, sửa, khoá/mở khoá thẻ, xoá (chỉ admin) — endpoint
   /api/readers; field: ma, hoTen, email, soDienThoai, loaiDocGia, trangThaiThe.
2. Hoàn tất UI admin theo YC-2026-08-09-002 (quản lý tài khoản thủ thư,
   cấu hình thư viện, cấu hình AI, audit log, backup) — nối /api/admin/*.
3. Cập nhật api.js (endpoints + fieldMap), gửi log [FRONTEND] cho Thư Ký.

### Trạng thái cập nhật 2026-08-09 10:12:52
- Phần 1 (UI Quản lý độc giả): HOÀN THÀNH — log [FRONTEND] 10:03:12, test 16/16.
- Phần 2 (UI admin theo YC-002): VẪN CHỜ — chưa có màn hình admin, api.js
  chưa nối /api/admin/*.

---

## YC-2026-08-09-004 — Frontend: UI Mượn/trả/gia hạn/phạt (chức năng 4)

- Ngày tạo: 2026-08-09 10:30:00
- Người yêu cầu: Thư Ký (theo log Backend 10:27:48 + đối chiếu đề bài)
- Gửi cho: **Frontend Agent**
- Trạng thái: CHỜ FRONTEND XỬ LÝ

### Việc cần làm
1. Làm UI mượn sách, trả sách, gia hạn, hiển thị phạt theo api_docs.md 0.4.0
   (mục /api/borrows): POST tạo phiếu mượn, PUT return, PUT renew, GET danh sách
   (lọc docGia/trangThai) — field theo tài liệu (BorrowSlips, BorrowDetails,
   FineHistory).
2. Phân quyền: thủ thư/admin dùng được; độc giả chưa xem phiếu riêng (Backend
   chưa liên kết Users-Readers — đừng tự đoán endpoint cho reader).
3. Cập nhật api.js (endpoints + fieldMap), gửi log [FRONTEND] cho Thư Ký.

### Trạng thái cập nhật 2026-08-09 17:04:10
- HOÀN THÀNH theo quét (borrow.html/borrow.js + api.js đã nối /api/borrows);
  CHƯA nhận log chính thức từ Frontend — cần Frontend gửi log xác nhận.

---

## YC-2026-08-09-005 — Backend: bổ sung so_ngay_muon cho luồng yêu cầu mượn

- Ngày tạo: 2026-08-09 18:08:31
- Người yêu cầu: Thư Ký (theo log [FRONTEND] 18:01:49 + kiểm tra code Backend)
- Gửi cho: **Backend Agent**
- Trạng thái: CHỜ BACKEND XỬ LÝ

### Việc cần làm
1. Thêm trường so_ngay_muon vào RequestCreate (reader gửi số ngày đề xuất).
2. Thêm so_ngay_muon vào RequestOut (trả về cho Frontend hiển thị ở bảng duyệt).
3. Khi approve yêu cầu MUON: dùng so_ngay_muon (có kiểm tra giới hạn
   max_borrow_days / 1 tối thiểu nếu cần) thay vì mặc định max_borrow_days.
4. Cập nhật api_docs.md + migration nếu cần; gửi log [BACKEND] cho Thư Ký.

---

## YC-2026-08-09-006 — Backend: 2 endpoint DELETE lịch sử mượn của độc giả

- Ngày tạo: 2026-08-09 18:19:07
- Người yêu cầu: Thư Ký (theo log [FRONTEND] 18:17:43 + kiểm tra code Backend)
- Gửi cho: **Backend Agent**
- Trạng thái: CHỜ BACKEND XỬ LÝ

### Việc cần làm
1. DELETE /api/borrows/me/{ma} — reader xoá 1 phiếu ĐÃ TRẢ (chỉ da_tra);
   phiếu đang mượn (chưa trả) phải trả lỗi.
2. DELETE /api/borrows/me — reader xoá toàn bộ lịch sử mượn của chính mình
   (chỉ các phiếu đã trả).
3. Phân quyền: chỉ reader truy cập được lịch sử của chính mình (theo liên kết
   Users.reader_id — Đợt A đã có).
4. Cập nhật api_docs.md; gửi log [BACKEND] cho Thư Ký.

### Trạng thái cập nhật 2026-08-09 19:03:51
- **HOÀN THÀNH** — log [BACKEND] 18:21:59 (2 endpoint DELETE, test 43/43 PASS).

---

## YC-2026-08-09-007 — Frontend: xác nhận/chuyển hẳn UI Đặt trước sang API thật

- Ngày tạo: 2026-08-09 19:03:51
- Người yêu cầu: Thư Ký (quét thấy reservation-mock.js + banner mock; Backend 0.7.0 đã có /api/reservations)
- Gửi cho: **Frontend Agent**
- Trạng thái: CHỜ FRONTEND XÁC NHẬN

### Việc cần làm
1. Xác nhận reservations.html/reservations.js đã gọi API thật /api/reservations
   (GET/POST, PUT cancel/fulfill) theo api_docs 0.7.0 — nếu còn mock fallback
   thì bỏ/bật tuỳ chọn rõ ràng.
2. Gửi log [FRONTEND] cho Thư Ký (chức năng 6) sau khi xong.

---

## YC-2026-08-09-008 — Backend: bổ sung /api/notifications (UC11)

- Ngày tạo: 2026-08-09 19:13:58
- Người yêu cầu: Thư Ký (theo log [FRONTEND] 19:11:17 — Frontend đang dùng localStorage tạm)
- Gửi cho: **Backend Agent**
- Trạng thái: CHỜ BACKEND (không khẩn cấp — UI đang chạy được bằng localStorage)

### Việc cần làm
1. API /api/notifications cho reader: tổng hợp nhắc hạn trả (phiếu trả hạn <=3
   ngày hoặc quá hạn, từ /api/borrows/me) + sách đặt trước SAN_SANG (reservations).
2. Trạng thái đã đọc (từng mục / tất cả) để thay thế localStorage.
3. Cập nhật api_docs.md; gửi log [BACKEND] cho Thư Ký.

### Trạng thái cập nhật 2026-08-09 19:17:29
- Phần 1 (GET /api/notifications): HOÀN THÀNH — log [BACKEND] 19:16:09,
  test 54/54 PASS, api_docs 0.8.0.
- Phần 2 (đánh dấu đã đọc PUT + bảng ThongBao): CHƯA LÀM — Backend để sau
  khi Frontend cần; hiện Frontend dùng localStorage (không chặn).

---

## YC-2026-08-09-009 — Backend: API thống kê chức năng 7

- Ngày tạo: 2026-08-09 19:22:31
- Người yêu cầu: Thư Ký (theo log [FRONTEND] 19:21:47 — Frontend đang mock)
- Gửi cho: **Backend Agent**
- Trạng thái: CHỜ BACKEND XỬ LÝ

### Việc cần làm (khớp contract Frontend)
1. GET /api/stats/top-books — sách mượn nhiều nhất.
2. GET /api/stats/top-readers — độc giả hoạt động nhất.
3. GET /api/stats/overdue-books — sách quá hạn.
4. Phân quyền: admin + librarian; reader 403. Cập nhật api_docs.md;
   gửi log [BACKEND] cho Thư Ký.

### Trạng thái cập nhật 2026-08-09 19:27:44
- **HOÀN THÀNH** — log [BACKEND] 19:25:14 (api_docs 0.9.0, test 58/58 PASS).

---

## YC-2026-08-09-010 — Backend: 3 endpoint xuất CSV (chức năng 8)

- Ngày tạo: 2026-08-09 19:32:55
- Người yêu cầu: Thư Ký (theo log [FRONTEND] 19:31:59 — UI đang báo "chưa sẵn sàng")
- Gửi cho: **Backend Agent**
- Trạng thái: CHỜ BACKEND XỬ LÝ

### Việc cần làm (khớp contract Frontend)
1. GET /api/export/books.csv — xuất danh sách sách.
2. GET /api/export/borrows.csv — xuất danh sách phiếu mượn.
3. GET /api/export/report.csv — xuất báo cáo thư viện.
4. Phân quyền: librarian + admin; reader 403. Cập nhật api_docs.md;
   gửi log [BACKEND] cho Thư Ký.

### Trạng thái cập nhật 2026-08-09 19:37:21
- **HOÀN THÀNH** — log [BACKEND] 19:34:48 (api_docs 0.10.0, test 62/62 PASS).

---

## YC-2026-08-09-011 — Backend: Thu phạt UC19 + loại yêu cầu DAT_TRUOC

- Ngày tạo: 2026-08-09 20:00:48
- Người yêu cầu: Thư Ký (theo log [FRONTEND] 20:00:07 — UI đang mock/chờ)
- Gửi cho: **Backend Agent**
- Trạng thái: CHỜ BACKEND XỬ LÝ

### Việc cần làm
1. API liệt kê phạt chưa thu (độc giả/phiếu quá hạn chưa thu tiền) cho màn
   hình Thu phạt UC19.
2. POST /api/borrows/{ma}/collect-fine — thủ thư thu phạt, đánh dấu đã thu
   (FineHistory), ghi audit log.
3. Bổ sung loai DAT_TRUOC vào RequestCreate + luồng tạo/duyệt yêu cầu
   "Đặt trước sách" (khi approve → tạo reservation theo luồng /api/reservations).
4. Cập nhật api_docs.md; gửi log [BACKEND] cho Thư Ký.

### Trạng thái cập nhật 2026-08-09 20:28:18
- Phần 2 (collect-fine + fines trong GET /api/borrows): HOÀN THÀNH — log
  [BACKEND] 20:05:33, migration 0008, api_docs 0.11.0, test 67/67.
- Phần 1 (Frontend nối danh sách phạt thật): CHƯA — borrow.js vẫn mock
  (cần Frontend cập nhật).
- Phần 3 (DAT_TRUOC): CHƯA — Backend chưa hỗ trợ loai này.

---

## YC-2026-08-09-012 — Frontend: bật sort Backend + nối danh sách phạt thật + đóng mock

- Ngày tạo: 2026-08-09 23:19:29
- Người yêu cầu: Thư Ký (quét thấy sortBooksBackend=false, MOCK_FINES, reservation-mock.js)
- Gửi cho: **Frontend Agent**
- Trạng thái: CHỜ FRONTEND XỬ LÝ

### Việc cần làm
1. Đổi sortBooksBackend = true trong api.js (Backend 23:16:54 đã hỗ trợ
   sort/order; bỏ sắp xếp client trùng).
2. Nối danh sách phạt chưa thu từ GET /api/borrows (bỏ MOCK_FINES) — UC19.
3. Xác nhận reservations dùng API thật (đóng YC-007) và gửi log [FRONTEND].

### Trạng thái cập nhật 2026-08-10 02:17:44
- Phần 1 (sortBooksBackend=true): HOÀN THÀNH — api.js 02:08:52.
- Phần 2 (danh sách phạt thật): HOÀN THÀNH — borrow.js 01:52:48 bỏ MOCK_FINES.
- Phần 3 (reservations bỏ mock): VẪN CHỜ — reservation-mock.js còn trong trang.

---

## YC-2026-08-10-013 — Frontend: cập nhật phạt ĐIỂM theo Backend 0.16.0

- Ngày tạo: 2026-08-10 03:01:24
- Người yêu cầu: Thư Ký (Backend 0.16.0 đổi so_tien → so_diem; Frontend chưa theo)
- Gửi cho: **Frontend Agent**
- Trạng thái: CHỜ FRONTEND XỬ LÝ

### Việc cần làm
1. api.js: fieldMap fineOut đổi soTien:"so_tien" → soDiem:"so_diem".
2. borrow.js + my-borrows.js: hiển thị fine.soDiem (điểm) thay vì fine.soTien;
   collect-fine dùng so_diem_da_thu + diem_con_lai.
3. Gửi log [FRONTEND] xác nhận.

### Trạng thái cập nhật 2026-08-10 03:07:46
- **HOÀN THÀNH** — log [FRONTEND] 03:07:07 (fineOut/collectFineOut + hiển thị điểm).

---

## YC-2026-08-10-014 — Frontend: xác nhận menu Quản lý độc giả cho admin

- Ngày tạo: 2026-08-10 04:01:20
- Người yêu cầu: Thư Ký (Backend 0.17.0 admin có đủ quyền độc giả; menu chỉ librarian)
- Gửi cho: **Frontend Agent**
- Trạng thái: CHỜ FRONTEND XÁC NHẬN

### Việc cần làm
1. Xác nhận menu "Quản lý độc giả" có nên hiển thị cho admin không (đề xuất:
   data-roles="admin,librarian" vì admin có quyền thêm/sửa/xoá/lock).
2. Hoặc giữ thiết kế hiện tại và xác nhận bằng log [FRONTEND].

### Trạng thái cập nhật 2026-08-10 04:53:07
- **HOÀN THÀNH** — readers.html 04:31:48 đã đổi data-roles="admin,librarian"
  (theo quét; chưa có log chính thức).

---

## YC-2026-08-10-015 — Backend: bổ sung so_ngay_muon (đóng YC-005 còn treo)

- Ngày tạo: 2026-08-10 04:53:07
- Người yêu cầu: Thư Ký (YC-005 từ 18:08/08 — Frontend vẫn gửi soNgayMuon)
- Gửi cho: **Backend Agent**
- Trạng thái: CHỜ BACKEND XỬ LÝ

### Việc cần làm
1. Thêm so_ngay_muon vào RequestCreate (reader đề xuất số ngày mượn).
2. Trả về trong RequestOut + dùng khi approve MUON (giới hạn max_borrow_days).
3. Cập nhật api_docs.md; gửi log [BACKEND].

---

## YC-2026-08-10-016 — UI: bỏ Xuất CSV + thêm Xoá lịch sử đặt trước

- Ngày tạo: 2026-08-10 05:05:08
- Người yêu cầu: Người dùng (trực tiếp)
- Gửi cho: **Frontend Agent** (chính) + **Backend Agent** (nếu cần DELETE lịch sử)
- Trạng thái: CHỜ XÁC NHẬN PHẠM VI XOÁ LỊCH SỬ → mới gửi agent

### Yêu cầu đã rõ
1. Bỏ nút "Xuất CSV" ở **books.html (Quản lý sách)**.
2. Bỏ nút "Xuất CSV" ở **stats.html (Thống kê)**.
   (Nút Xuất CSV ở borrow.html — Mượn/Trả — GIỮ NGUYÊN vì người dùng không yêu cầu bỏ.)
3. Thêm nút **"Xoá lịch sử"** trong Danh sách đặt trước (xử lý) — PHẠM VI CẦN
   XÁC NHẬN (xem dưới).

### Cần người dùng xác nhận 1 câu
- "Xoá lịch sử" áp dụng cho ai và xoá những đặt trước nào?
  - Phương án A (đề xuất): reader xoá lịch sử đặt trước CỦA MÌNH (các đặt trước
    đã kết thúc: HUY / DA_MUON); librarian xoá lịch sử đã xử lý trong danh sách.
  - Phương án B: chỉ thêm nút xoá từng dòng cho librarian/admin trong màn hình xử lý.

### Nếu theo phương án A (cần Backend)
- Thêm DELETE /api/reservations/me/{ma_dat} + DELETE /api/reservations/me
  (chỉ xoá đặt trước đã kết thúc, giữ đặt trước active CHO_XU_LY/SAN_SANG).
- Cập nhật api_docs.md + gửi log [BACKEND].

### Frontend sau khi rõ phạm vi
- Bỏ 2 nút Xuất CSV (books, stats).
- Thêm nút/UI Xoá lịch sử đặt trước theo phạm vi đã chốt.
- Gửi log [FRONTEND] cho Thư Ký.

### Trạng thái cập nhật 2026-08-10 05:48:15
- Xoá lịch sử đặt trước: Backend HOÀN THÀNH (log 05:13:10, 0.20.0, 94/94);
  Frontend đã nối 2 nút xoá theo quét (05:14-05:15) — chờ log chính thức.
- Bỏ Xuất CSV books/stats: CHƯA LÀM — vẫn còn nút (05:15:27).

### Trạng thái cập nhật 2026-08-10 06:45:01
- stats: ĐÃ BỎ (06:42, có log Frontend 06:45:01).
- books: VẪN CÒN nút Xuất CSV (06:10:05) — CHƯA XONG.

### Trạng thái cập nhật 2026-08-10 06:54:40
- **HOÀN THÀNH** — Frontend bỏ toàn bộ nút/hàm Xuất CSV (books, stats, borrow,
  reservations; log 06:54:40); Backend /api/export/* giữ nguyên.

---

## YC-2026-08-10-017 — Frontend: chặn gửi yêu cầu khi chưa chọn sách

- Ngày tạo: 2026-08-10 05:06:54
- Người yêu cầu: Người dùng (báo: không chọn sách vẫn bấm "Gửi yêu cầu" được)
- Gửi cho: **Frontend Agent**
- Trạng thái: CHỜ FRONTEND XỬ LÝ

### Hiện trạng (Thư Ký kiểm tra code requests.js 20:14)
- createRequest() ĐÃ kiểm tra items.length === 0 → hiện "Vui lòng chọn ít nhất
  1 sách." và return (không gửi API).
- NHƯNG nút "Gửi yêu cầu" vẫn ENABLE khi chưa chọn sách → UX cho phép bấm
  (chỉ báo lỗi sau khi bấm). Có thể người dùng đang chạy bản JS cũ do cache.

### Việc cần làm
1. Vô hiệu hoá (disabled) nút "Gửi yêu cầu" khi chưa có ≥1 sách hợp lệ cho
   MUON/DAT_TRUOC (theo dõi change trên .req-item-book + số lượng), enable
   khi hợp lệ.
2. Kiểm tra lại validation cho cả 2 luồng MUON và DAT_TRUOC (đảm bảo không
   gửi payload items rỗng).
3. Bump version query `?v=` của requests.js trong requests.html để tránh cache
   cũ.
4. Gửi log [FRONTEND] cho Thư Ký.

### Trạng thái cập nhật 2026-08-10 05:48:15
- CHƯA THỰC HIỆN — requests.js không đổi (20:14), nút vẫn enable.

### Trạng thái cập nhật 2026-08-10 06:45:01
- HOÀN THÀNH theo code — requests.js 06:04:31 có updateSubmitState (disable +
  enable theo chọn sách); chờ log chính thức.

### Trạng thái cập nhật 2026-08-10 06:54:40
- HOÀN THÀNH (đã có log Frontend 06:54:40 xác nhận phần UI; requests.js đã disable).

---

## YC-2026-08-10-018 — Log bổ sung Backend 0.25.0 + bỏ Xuất CSV books + xác nhận export reservations

- Ngày tạo: 2026-08-10 06:45:01
- Người yêu cầu: Thư Ký (quét: Backend đổi nhiều nhưng không có log; books.html còn nút CSV)
- Gửi cho: **Backend Agent** + **Frontend Agent**
- Trạng thái: CHỜ XỬ LÝ

### Backend
1. Gửi log [BACKEND] tổng hợp cho các thay đổi 05:29-06:31: so_ngay_muon
   (migration 0013), bỏ loại "khac" (0014), validation tài khoản, export đặt
   trước chỉ thủ thư, Email DTC, thông báo lỗi đăng nhập tiếng Việt,
   api_docs 0.25.0 + số test PASS.

### Frontend
2. Bỏ nút "Xuất CSV" ở books.html (theo yêu cầu người dùng — chỉ giữ
   borrow.html).
3. Xác nhận nút "Xuất CSV" ở reservations.html (librarian) có giữ không
   (Backend đã có /api/export/reservations.csv; giữ hay bỏ tuỳ yêu cầu).
4. Gửi log [FRONTEND] xác nhận YC-017 (disable nút gửi) + bỏ UC trên UI admin.

### Trạng thái cập nhật 2026-08-10 06:54:40
- Phần Backend (gửi log): HOÀN THÀNH — đã nhận 4 log 05:59→06:32.
- Phần Frontend: HOÀN THÀNH — đã bỏ toàn bộ nút Xuất CSV (gồm books + reservations).

### Cập nhật 2026-08-09 09:55 (Trợ Lý đính chính theo quyết định người dùng)
- Mục 2 của YC-003: BỎ phần "quản lý tài khoản thủ thư" — tính năng này đã bị xoá toàn bộ (Frontend + Backend), KHÔNG làm lại vì không có trong đề bài.
- UI admin còn lại (nếu làm): cấu hình thư viện, cấu hình AI, audit log + backup.
- Thứ tự vòng lặp: sau Backend vòng 2 (chức năng 3 xong) → AI Engine (AI-1) trước; UI độc giả/admin của YC-003 sẽ xử lý ở lượt Frontend vòng sau.
