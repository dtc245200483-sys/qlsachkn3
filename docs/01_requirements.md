# 01 - BÁO CÁO YÊU CẦU PHẦN MỀM (SRS - LIBRARY MANAGEMENT)

## 1. Bằng chứng áp dụng skill

| Skill | Vai trò | Bằng chứng |
|---|---|---|
| `software-requirements` | PRIMARY | Cấu trúc SRS chuẩn IEEE 830, có Requirement ID, Priority, Acceptance Criteria, Source Trace. |
| `domain-modeling` | PRIMARY | Chuẩn hóa thuật ngữ nghiệp vụ thư viện: Độc giả, Phiếu mượn, Phạt quá hạn, Điểm SVNET, Đặt trước, Yêu cầu bổ sung. |
| `fastapi-expert` | SUPPORTING | Ràng buộc kiến trúc Backend FastAPI, JWT authentication, Pydantic validation. |
| `brainstorming` | SUPPORTING | Phân tích open questions về giới hạn mượn, chính sách phạt. |

## 2. Source Trace

| Source ID | Nguồn | Nội dung |
|---|---|---|
| SRC-001 | `00_project.md` | Nghiệp vụ quản lý thư viện: sách, độc giả, mượn/trả, phạt, đặt trước, gợi ý AI. |
| SRC-002 | `prompts/01_requirements.md` | Ràng buộc: FastAPI, SQL Server, Vanilla JS, JWT, RBAC 3 role. |
| SRC-003 | `backend/api_docs.md` | Chi tiết API contract đã triển khai. |

## 3. Mục tiêu & Phạm vi

### 3.1 Mục tiêu (Goals)
Hệ thống quản lý thư viện số hóa toàn bộ quy trình mượn trả sách vật lý, quản lý kho sách theo thời gian thực và tích hợp AI để tối ưu trải nghiệm đọc của độc giả thông qua hệ thống gợi ý thông minh.

### 3.2 Phạm vi (In Scope)
- Quản lý vòng đời sách (Nhập kho, Sửa, Xóa, Tìm kiếm, Sắp xếp).
- Quản lý hồ sơ độc giả và tài khoản nội bộ.
- Quản lý quy trình mượn/trả/gia hạn/thu phạt.
- Đặt trước sách (Reservations).
- Yêu cầu bổ sung sách mới (Requests).
- Hệ thống thông báo (Notifications).
- Thống kê tổng quan (Dashboard Stats).
- Xuất báo cáo (Export).
- Hệ thống AI gợi ý sách.
- Quản trị hệ thống (Admin: tài khoản, cấu hình, danh mục).

### 3.3 Ngoài phạm vi (Out of Scope)
- Thanh toán phạt trực tuyến (chỉ tính toán, trừ điểm SVNET nội bộ).
- Quản lý thẻ thư viện vật lý.
- Ứng dụng mobile native.

## 4. Thuật ngữ nghiệp vụ (Glossary)

| Thuật ngữ | Định nghĩa |
|---|---|
| Reader (Độc giả) | Người dùng có tài khoản, được phép mượn sách. Mỗi reader có `diem_svnet` (mặc định 100). |
| Librarian (Thủ thư) | Nhân viên thư viện xác nhận mượn/trả, thu phạt. |
| Admin | Quản trị viên toàn quyền. |
| Borrow Record (Phiếu mượn) | Dữ liệu ghi nhận giao dịch mượn sách, có `ngay_muon`, `han_tra`, `ngay_tra`, `da_tra`. |
| Fine (Phạt) | Khi trả sách quá hạn: `so_diem = so_ngay_qua_han × 2` (mặc định 2 điểm/ngày). |
| SVNET Points (Điểm uy tín) | Điểm uy tín của độc giả, mặc định 100, bị trừ khi thu phạt. |
| Reservation (Đặt trước) | Độc giả đặt trước sách đang hết, ưu tiên khi sách được trả. |
| Request (Yêu cầu) | Độc giả yêu cầu thư viện bổ sung sách mới. |
| soLuongKhaDung | Số lượng sách hiện có trên kệ (tổng - đang mượn). |

## 5. Phân tích Actor

| Actor | Vai trò | Quyền hạn |
|---|---|---|
| Admin | Quản trị hệ thống | Toàn quyền: quản lý tài khoản, cấu hình, sách, độc giả, mượn/trả. |
| Librarian | Thủ thư | Quản lý sách, độc giả, mượn/trả, thu phạt. Không quản lý tài khoản. |
| Reader | Độc giả | Tìm kiếm sách, mượn sách, xem lịch sử, đặt trước, yêu cầu bổ sung, xem hồ sơ. |

## 6. Yêu cầu Chức năng (Functional Requirements)

### Phân hệ Đăng nhập và Phân quyền (Auth)

| ID | Yêu cầu | Tiêu chí chấp nhận | Priority |
|---|---|---|---|
| FR-AUTH-01 | Đăng nhập hệ thống | `POST /api/auth/login` trả JWT token. Sai password → 401. | MUST |
| FR-AUTH-02 | Điều hướng theo Role | Token chứa role. Frontend `js/layout.js` ẩn/hiện sidebar menu theo role. | MUST |
| FR-AUTH-03 | Đăng ký tài khoản | `POST /api/auth/register` tạo tài khoản reader mới. | SHOULD |

### Phân hệ Quản lý Sách (Books)

| ID | Yêu cầu | Tiêu chí chấp nhận | Priority |
|---|---|---|---|
| FR-BOOK-01 | Thêm sách mới | `POST /api/books` tạo sách. `soLuongKhaDung = soLuong`. | MUST |
| FR-BOOK-02 | Tra cứu sách | `GET /api/books?search=&the_loai=&sort=` trả kết quả khớp. | MUST |
| FR-BOOK-03 | Sửa thông tin sách | `PUT /api/books/{id}` cập nhật. | MUST |
| FR-BOOK-04 | Xóa sách | `DELETE /api/books/{id}`. Nếu đang có phiếu mượn chưa trả → 400. | MUST |

### Phân hệ Quản lý Độc giả (Readers)

| ID | Yêu cầu | Tiêu chí chấp nhận | Priority |
|---|---|---|---|
| FR-RDR-01 | Thêm độc giả | `POST /api/readers` tạo hồ sơ. `diem_svnet = 100`. | MUST |
| FR-RDR-02 | Danh sách độc giả | `GET /api/readers?search=` trả danh sách, hỗ trợ tìm kiếm. | MUST |
| FR-RDR-03 | Sửa/Xóa độc giả | `PUT/DELETE /api/readers/{id}`. | MUST |

### Phân hệ Mượn Trả (Borrows)

| ID | Yêu cầu | Tiêu chí chấp nhận | Priority |
|---|---|---|---|
| FR-BRW-01 | Tạo phiếu mượn | `POST /api/borrows` trừ 1 `soLuongKhaDung`. 400 nếu hết sách. | MUST |
| FR-BRW-02 | Trả sách | `PUT /api/borrows/{ma}/return` cộng 1 `soLuongKhaDung`. Nếu quá hạn → tạo FineHistory. | MUST |
| FR-BRW-03 | Gia hạn | `PUT /api/borrows/{ma}/renew` tối đa 1 lần. | MUST |
| FR-BRW-04 | Thu phạt | `POST /api/borrows/{ma}/collect-fine` trừ `diem_svnet`. Chỉ librarian. | MUST |
| FR-BRW-05 | Giới hạn mượn | Một reader không quá 5 phiếu đang mượn. | MUST |
| FR-BRW-06 | Lịch sử mượn | `GET /api/borrows/me` trả phiếu của reader đang đăng nhập. | MUST |

### Phân hệ Đặt trước (Reservations)

| ID | Yêu cầu | Tiêu chí chấp nhận | Priority |
|---|---|---|---|
| FR-RSV-01 | Đặt trước sách | `POST /api/reservations` khi sách hết. | SHOULD |
| FR-RSV-02 | Xác nhận đặt trước | Khi sách được trả, ưu tiên reader đặt trước. | SHOULD |

### Phân hệ Yêu cầu bổ sung (Requests)

| ID | Yêu cầu | Tiêu chí chấp nhận | Priority |
|---|---|---|---|
| FR-REQ-01 | Gửi yêu cầu | `POST /api/requests` tạo yêu cầu bổ sung sách. | SHOULD |
| FR-REQ-02 | Duyệt yêu cầu | Librarian duyệt/từ chối yêu cầu. | SHOULD |

### Phân hệ Thông báo (Notifications)

| ID | Yêu cầu | Tiêu chí chấp nhận | Priority |
|---|---|---|---|
| FR-NOTIF-01 | Nhận thông báo | `GET /api/notifications` trả danh sách thông báo. | SHOULD |

### Phân hệ Thống kê (Stats)

| ID | Yêu cầu | Tiêu chí chấp nhận | Priority |
|---|---|---|---|
| FR-STAT-01 | Thống kê tổng quan | `GET /api/stats` trả tổng sách, tổng độc giả, phiếu đang mượn, sách được mượn nhiều nhất. | SHOULD |

### Phân hệ AI Engine

| ID | Yêu cầu | Tiêu chí chấp nhận | Priority |
|---|---|---|---|
| FR-AI-01 | Gợi ý sách | Dựa trên lịch sử mượn, AI trả về danh sách sách liên quan. | SHOULD |

### Phân hệ Admin

| ID | Yêu cầu | Tiêu chí chấp nhận | Priority |
|---|---|---|---|
| FR-ADM-01 | Quản lý tài khoản | `GET /api/admin/accounts` liệt kê tất cả tài khoản. | MUST |
| FR-ADM-02 | Cấu hình hệ thống | `GET|PUT /api/admin/config` cấu hình (max borrow, fine points/day). | MUST |
| FR-ADM-03 | Quản lý danh mục | `GET /api/catalog/categories` liệt kê danh mục sách. | MUST |
| FR-ADM-04 | Xuất báo cáo | `GET /api/export/*` xuất dữ liệu. | SHOULD |

## 7. Yêu cầu Phi Chức năng (NFR)
- **NFR-PERF-01:** API trả kết quả < 200ms với 10,000 bản ghi.
- **NFR-SEC-01:** Mật khẩu lưu băm Bcrypt. Không plaintext.
- **NFR-SEC-02:** JWT token hết hạn sau thời gian cấu hình (mặc định 60 phút).
- **NFR-UI-01:** Giao diện responsive (tương thích 360px trở lên).

## 8. Ràng buộc Kỹ thuật (Constraints)

| ID | Ràng buộc |
|---|---|
| CONSTRAINT-ARCH-01 | Backend: Python/FastAPI. |
| CONSTRAINT-DB-01 | Database: SQL Server. Migrations: Alembic. |
| CONSTRAINT-FE-01 | Frontend: HTML tĩnh + CSS custom + Vanilla JS Fetch API. Không dùng Bootstrap/React/Vue. |
| CONSTRAINT-AUTH-01 | Xác thực: JWT. Phân quyền: RBAC (admin, librarian, reader). |
| CONSTRAINT-FONT-01 | Typography: Google Fonts Be Vietnam Pro (wght 400–800). |

## 9. Business Rules
- BR-01: Mỗi reader tối đa 5 phiếu mượn đang hoạt động.
- BR-02: Phạt quá hạn: `so_diem = so_ngay × overdue_fine_points_per_day` (mặc định 2).
- BR-03: Thu phạt trừ `diem_svnet` (không âm). Chỉ `librarian` được thu.
- BR-04: Gia hạn tối đa 1 lần.
- BR-05: Xóa sách đang có phiếu mượn chưa trả → từ chối.

STATUS: PASS
NEXT_INPUT: docs/01_requirements.md
NEXT_PROMPT: prompts/02_design.md
TRACEABILITY_MATRIX_UPDATED: YES
