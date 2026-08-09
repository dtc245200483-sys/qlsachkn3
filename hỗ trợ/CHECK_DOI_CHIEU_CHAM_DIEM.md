# Đối chiếu Frontend/Backend với tiêu chí chấm điểm (cập nhật 2026-08-09)

## KT2 — Xây dựng chức năng quản lý (đang là trọng tâm Frontend/Backend)

| # | Tiêu chí KT2 | Trạng thái | Bằng chứng | Cần làm |
|---|---|---|---|---|
| 1 | Cấu trúc dự án hợp lý | ✅ | Backend/ (app, routers, tests, alembic), Frontend/, AI_Engine/, thuky/, hỗ trợ/ | — |
| 2 | Đăng nhập + phân quyền | ✅ | JWT, 3 role, API bảo vệ theo role, test 401/403 | — |
| 3 | CRUD nghiệp vụ chính | ⚠️ | Sách ✅, độc giả ✅, phiếu mượn: Backend ✅, UI ❌ | Làm UI mượn/trả; chưa có đặt trước |
| 4 | Tìm kiếm + lọc + sắp xếp | ⚠️ | books: q/theLoai/trangThai ✅; readers: q ✅ | Chưa có sắp xếp (sort) |
| 5 | Thống kê/báo cáo cơ bản | ❌ | Chưa có dashboard/stats | Làm chức năng 7 (thống kê) + xuất báo cáo (chức năng 8) |
| 6 | Giao diện rõ ràng, dễ dùng | ✅ | UI_DESIGN.md, thông báo lỗi, ẩn/hiện theo role | Rà soát responsive lần cuối |
| 7 | CSDL ổn định + dữ liệu mẫu | ⚠️ | 5 sách + 3 tài khoản; migrations 0001-0005 | Thêm dữ liệu mẫu độc giả + phiếu mượn |
| 8 | Xử lý lỗi cơ bản | ✅ | API trả detail rõ, Frontend hiện thông báo, 28/28 test | Bổ sung test biên nếu cần |
| 9 | Minh chứng AI khi lập trình | ❌ | Chưa có nhật ký prompt/phản hồi AI | Tạo file minh chứng (prompt → kết quả → chỉnh sửa) |
| 10 | README + .env.example + commit | ⚠️ | README ✅ | Thêm .env.example; tạo git repo + commit rõ ràng |

## KT1 — Phân tích và thiết kế (tài liệu, nộp tuần 3)

| # | Tiêu chí KT1 | Trạng thái | Cần làm |
|---|---|---|---|
| 1 | Phân tích bài toán | ⚠️ | Có DE_BAI, REQUIREMENTS_QA — cần tài liệu phân tích hoàn chỉnh |
| 2 | Yêu cầu chức năng | ⚠️ | Cần SRS/đặc tả có đầu vào-xử lý-đầu ra |
| 3 | Yêu cầu phi chức năng | ❌ | Cần mục bảo mật, hiệu năng, sao lưu, UX |
| 4 | Actor + use case | ❌ | Cần sơ đồ/mô tả use case cho 3 vai trò |
| 5 | ERD + bảng + ràng buộc | ❌ | Có migration nhưng chưa có tài liệu ERD |
| 6 | Kiến trúc hệ thống | ⚠️ | Có README/api_docs — cần tài liệu kiến trúc + luồng dữ liệu |
| 7 | Vị trí ứng dụng AI | ⚠️ | Có prompt mẫu đề bài — cần tài liệu chọn AI-1/2/3 |
| 8 | Prompt + luồng gọi AI sơ bộ | ⚠️ | Có AI.txt — cần tài liệu system/user prompt + giới hạn |
| 9 | Minh chứng dùng AI khi phân tích | ❌ | Chưa có nhật ký prompt/phản hồi AI |
| 10 | Tài liệu + kế hoạch | ⚠️ | Có KE_HOACH_9_TUAN — cần gộp thành tài liệu hoàn chỉnh |

## KT3 + Thi cuối — phụ thuộc phần AI (chưa làm)

- KT3: toàn bộ 10 tiêu chí chưa đạt (AI chưa có code).
- Thi cuối: cần hoàn thiện 8+3 chức năng + tài liệu + demo.
