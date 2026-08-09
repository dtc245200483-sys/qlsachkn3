# So sánh: Đề bài ↔ Use Case ↔ Hiện trạng ↔ KT1/KT2/KT3 (2026-08-10)

## A. Đề bài (8 quản lý + 3 AI) ↔ Use Case ↔ Hiện trạng

| Đề bài | Use Case | Hiện trạng |
|---|---|---|
| 1. Đăng nhập, phân quyền 3 vai trò | UC01/12/22 + UC23 (mở rộng) | ✅ login + JWT + phân quyền; admin quản lý tài khoản |
| 2. Quản lý sách | UC13 | ✅ books CRUD + search + sort |
| 3. Quản lý độc giả | UC14 | ✅ admin thêm/sửa/xoá; thủ thư khoá thẻ |
| 4. Mượn/trả/gia hạn/phạt | UC15/16/17/19 | ✅ borrows + thu phạt bằng ĐIỂM |
| 5. Tra cứu sách | UC02 | ✅ search (q/theLoai/trangThai/sort) |
| 6. Đặt trước sách | UC06/18 | ✅ reservations |
| 7. Thống kê | UC20 (+UC28) | ✅ stats top-books/top-readers/overdue |
| 8. Xuất danh sách/báo cáo | UC20/28 | ✅ export CSV |
| AI-1 Chatbot tra cứu | UC03 | ❌ chưa (KT3) |
| AI-2 Tóm tắt sách | UC04 | ❌ chưa (KT3) |
| AI-3 Gợi ý sách liên quan | UC05 | ❌ chưa (KT3) |

### Mở rộng đã làm (ngoài đề bài, không hại)

| Mở rộng | UC | Trạng thái |
|---|---|---|
| Đăng ký độc giả | UC01 | ✅ |
| Yêu cầu mượn/trả/gia hạn online | UC07/08/09 | ✅ |
| Lịch sử mượn/phạt + xoá | UC10 | ✅ |
| Thông báo | UC11 | ✅ |
| Hồ sơ cá nhân (ảnh, mật khẩu, thông tin) | (Profile) | ✅ |
| Admin quản lý tài khoản | UC23 | ✅ |
| Danh mục thể loại/NXB | UC25 | ✅ |
| Cấu hình quy định mượn/trả | UC24 | ✅ |
| Cấu hình AI | UC26 | ✅ Backend (UI ẩn) |
| Sao lưu/phục hồi + audit log | UC27 | ✅ Backend (UI ẩn) |

## B. KT1 — Phân tích & thiết kế (tài liệu)

| # | Tiêu chí | Tài liệu | Trạng thái |
|---|---|---|---|
| 1 | Phân tích bài toán | DE_BAI + SRS + REQUIREMENTS_QA | ✅ |
| 2 | Yêu cầu chức năng | SRS (bảng input/xử lý/output) | ✅ |
| 3 | Yêu cầu phi chức năng | SRS mục 4 | ✅ |
| 4 | Actor & use case | docs/USE_CASE.md (28 UC + Mermaid) | ✅ (nhớ cập nhật UC14 phân vai mới) |
| 5 | ERD | docs/ERD.md (13 bảng) | ✅ |
| 6 | Kiến trúc hệ thống | docs/KIEN_TRUC.md | ✅ |
| 7 | Vị trí ứng dụng AI | docs/AI_DESIGN.md | ✅ (tài liệu) |
| 8 | Prompt + luồng AI sơ bộ | docs/AI_DESIGN.md + prompt mẫu đề bài | ✅ |
| 9 | Minh chứng dùng AI | promtAI/MINH_CHUNG (5 mục) | ✅ (bổ sung khi làm KT3) |
| 10 | Tài liệu + kế hoạch | docs/ + KE_HOACH_9_TUAN | ✅ |

**KT1: ~10/10 — chỉ cần rà soát + đồng bộ UC14.**

## C. KT2 — Xây dựng chức năng quản lý (code)

| # | Tiêu chí | Trạng thái |
|---|---|---|
| 1 | Cấu trúc dự án hợp lý | ✅ |
| 2 | Đăng nhập + phân quyền | ✅ |
| 3 | CRUD nghiệp vụ chính | ✅ |
| 4 | Tìm kiếm + lọc + sắp xếp | ✅ |
| 5 | Thống kê/báo cáo | ✅ |
| 6 | Giao diện rõ ràng | ✅ |
| 7 | CSDL ổn định + dữ liệu mẫu | ✅ |
| 8 | Xử lý lỗi cơ bản | ✅ |
| 9 | Minh chứng AI khi lập trình | ✅ (5 minh chứng) |
| 10 | README + .env.example + git commit | ✅ |

**KT2: 10/10 ✅**

## D. KT3 — Tích hợp AI (chưa làm)

| # | Tiêu chí | Trạng thái |
|---|---|---|
| 1 | Tích hợp AI vào hệ thống | ❌ chưa |
| 2 | Kết nối API/model AI, bảo vệ key | ❌ (AIConfig có, code chưa) |
| 3 | Prompt tách khỏi code (system/user, ràng buộc) | ❌ (chỉ tài liệu) |
| 4 | Tối ưu ≥ 3 vòng prompt | ❌ |
| 5 | Dùng dữ liệu hệ thống + kiểm soát quyền | ❌ (thiết kế có) |
| 6 | Hiển thị kết quả AI rõ ràng | ❌ |
| 7 | Xử lý lỗi AI (timeout, rate limit, rỗng) | ❌ |
| 8 | Kiểm thử chức năng + AI | ❌ (test quản lý có, AI chưa) |
| 9 | Review code bằng AI + minh chứng | ❌ |
| 10 | UX AI tự nhiên | ❌ |

**KT3: 0/10 — cần làm AI-1/2/3 + test + minh chứng + review (Ý 4).**

## Kết luận

- **KT1 ≈ xong** (rà soát tài liệu), **KT2 xong 10/10**, **KT3 chưa làm**.
- Thi cuối: sau KT3 + báo cáo/demo.
