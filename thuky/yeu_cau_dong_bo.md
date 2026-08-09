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

### Cập nhật 2026-08-09 09:55 (Trợ Lý đính chính theo quyết định người dùng)
- Mục 2 của YC-003: BỎ phần "quản lý tài khoản thủ thư" — tính năng này đã bị xoá toàn bộ (Frontend + Backend), KHÔNG làm lại vì không có trong đề bài.
- UI admin còn lại (nếu làm): cấu hình thư viện, cấu hình AI, audit log + backup.
- Thứ tự vòng lặp: sau Backend vòng 2 (chức năng 3 xong) → AI Engine (AI-1) trước; UI độc giả/admin của YC-003 sẽ xử lý ở lượt Frontend vòng sau.
