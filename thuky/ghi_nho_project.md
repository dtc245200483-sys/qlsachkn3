# Ghi nhớ project — cập nhật 2026-08-09

## Project
- Tên: Hệ thống quản lý thư viện có tích hợp AI
- Đường dẫn gốc: D:\ung dung tri tue nhan ao\app
- Vai trò hiện tại: Thư Ký Agent — chỉ ghi/đọc trong thư mục thuky,
  không code nghiệp vụ, không sửa file của Backend/Frontend/AI_Engine.
- Chế độ hoạt động: QUÉT CHỦ ĐỘNG — mỗi lần được gọi phải tự quét
  Backend/Frontend/AI_Engine (không chờ log gửi tới).

## Cấu trúc hiện tại
- AI_Engine/ — có AI.txt (prompt AI Engine Agent, chưa có code)
- Backend/ — FastAPI + SQLAlchemy + Alembic: đã có API chức năng 1, 2
  (auth.py, books.py, models Users/Books, migration 0001) + api_docs.md
- Frontend/ — có 6 file UI (index.html, books.html, css/style.css,
  js/api.js, js/auth.js, js/books.js) — api.js CHƯA dán config API từ api_docs.md
- thuky/ — chứa prompt Thư Ký, ghi nhớ project, changelog, trạng thái quét

## Trạng thái
- Lần quét đầu tiên: 2026-08-09 06:28:24 — không có git, so sánh bằng timestamp.
- Đã ghi 2 log "phát hiện từ quét" vào changelog_tong.md (Backend/AGENTS.md,
  AI_Engine/AI.txt — đều là prompt, chưa phải code).
- Lần quét 2026-08-09 06:47:38: phát hiện 6 file mới ở Frontend, khớp với
  log [FRONTEND] 06:46:46 → đã ghi log agent tự báo cáo vào changelog_tong.md.
- Lần quét 2026-08-09 07:05:39: Backend có toàn bộ code API chức năng 1, 2 +
  LOG_THU_KY.md → đã ghi log [BACKEND] 07:02:48 vào changelog_tong.md.
- canh_bao_dong_bo.md: cảnh báo 1 đã cập nhật — Backend đã giải quyết phần
  thiếu API/tài liệu; còn theo dõi: Frontend chưa dán config api.js.
- Yêu cầu đồng bộ YC-2026-08-09-001 đang CHỜ Frontend xử lý: dán config API
  từ Backend/api_docs.md vào Frontend/js/api.js (xem yeu_cau_dong_bo.md).
- Cập nhật 07:33:23: Frontend đã sửa api.js (07:12:12) — config API đã điền
  đúng tài liệu; NHƯNG Frontend chưa gửi log hoàn thành, chưa có bằng chứng
  test end-to-end; phát hiện tiến trình python PID 38928 treo từ 07:17:21.
- Cập nhật 07:43:24 (yêu cầu người dùng): đã tạo 3 tài khoản đăng nhập trong
  LibraryDB.dbo.Users — admin/admin1 (admin), librarian/librarian1 (librarian),
  reader/reader1 (reader). Đã xác minh login qua API thành công cho cả 3.
- Cập nhật 07:45:14: Frontend sửa books.js (07:41:01) nhưng chưa gửi log.
  Hiện admin và librarian có cùng quyền (thêm/sửa/xoá sách) — chưa có tính
  năng nào tách biệt admin; đang chờ người dùng quyết định có cần phân biệt.
- Cập nhật 07:49:46: Nhận log [FRONTEND] 07:41:41 — nối API xong, test
  12/12 PASS → YC-001 HOÀN THÀNH. Người dùng đã chốt ranh giới quyền admin:
  quản lý tài khoản thủ thư, cấu hình tham số thư viện, cấu hình AI Engine,
  audit log + backup → đã tạo YC-2026-08-09-002 chờ Backend/Frontend/AI Engine.
- Cập nhật 08:09:34: Backend HOÀN THÀNH YC-002 (log 08:06:16, api_docs 0.2.0,
  migration 0002/0003). Thư mục hỗ trợ xuất hiện chứa đề bài gốc + kế hoạch
  + quy trình vòng lặp. Frontend/AI_Engine mới có prompt, chưa có code theo
  YC-002 → đã ghi cảnh báo 2 (lệch pha Backend xong trước).
- Cập nhật 09:50:40: Backend HOÀN THÀNH chức năng 3 (log 09:49:03, /api/readers,
  api_docs 0.3.0, test 9/9 PASS). Frontend cập nhật giao diện + khung admin.js
  nhưng CHƯA nối API admin/readers, chưa gửi log → đã tạo YC-003 và cảnh báo 3.
- Cập nhật 10:12:52: Frontend HOÀN THÀNH UI chức năng 3 (log 10:03:12,
  readers.html/readers.js, test 16/16) → cảnh báo 3 đã hết. UI admin
  (YC-002 phần Frontend) VẪN CHỜ.
- Cập nhật 10:30:00: Backend HOÀN THÀNH chức năng 4 (log 10:27:48,
  /api/borrows, migration 0005, api_docs 0.4.0, test 19/19). Frontend CHƯA
  nối /api/borrows → cảnh báo 4 + YC-004. UI admin vẫn chưa làm.
- Cập nhật 17:04:10: Backend HOÀN THÀNH chức năng 5 (log 10:43:48, /api/books
  q/theLoai/trangThai, test 28/28). Frontend đã thêm borrow.html/borrow.js và
  search.html/search.js, api.js nối /api/borrows + query books — nhưng CHƯA
  gửi log (cảnh báo 4, 5 đã hết theo quét; cần log chính thức).
- Cập nhật 18:08:31: Backend Đợt A (log 17:35:06, 0.6.0, 38/38): register,
  borrows/me, requests approve/reject, admin accounts/categories/publishers/
  restore. Frontend thêm register/my-borrows/requests/admin-accounts/admin-catalog
  + api.js nối đầy đủ; nhận log 18:01:49 (so_ngay_muon) + 18:07:45 (sinh mã yêu
  cầu). Lệch pha: Backend CHƯA có so_ngay_muon → YC-005. Mâu thuẫn cần xác nhận:
  09:55 xoá quản lý tài khoản thủ thư nhưng 17:35 Đợt A thêm lại /api/admin/accounts.
- Cập nhật 18:19:07: Frontend thêm nút xoá lịch sử mượn (log 18:17:43,
  deleteMyBorrow + deleteMyBorrows trong api.js) — Backend CHƯA có 2 endpoint
  DELETE → YC-006.
- Cập nhật 19:03:51: Backend xong YC-006 (log 18:21:59, 43/43) + chức năng 6
  Đặt trước (log 19:02:38, migration 0007, api_docs 0.7.0, 50/50; admin 403
  mượn/trả/đặt trước — Frontend menu đã đồng bộ). Frontend UI reservations
  còn mock fallback → YC-007. YC-005 (so_ngay_muon) VẪN CHỜ Backend.
- Cập nhật 19:13:58: Frontend UC11 Thông báo (log 19:11:17, test 15/15) —
  notifications.html + core/badge; api.js khai báo /api/notifications; Backend
  chưa có → YC-008 (không khẩn cấp, UI dùng localStorage tạm).
- Cập nhật 19:17:29: Backend HOÀN THÀNH UC11 (log 19:16:09, GET /api/notifications,
  api_docs 0.8.0, test 54/54) → YC-008 phần GET xong; phần đánh dấu đã đọc
  (PUT + bảng ThongBao) để sau khi cần.
- Cập nhật 19:22:31: Frontend chức năng 7 Thống kê (log 19:21:47, stats.html +
  stats.js, api.js /api/stats/*, mock, test 12/12) — Backend chưa có → YC-009.
  Frontend/AGENTS.md đổi 19:21:05 (thêm LƯU PROMPT) nhưng agent không lưu
  promtAI → Thư Ký đã thêm PHIÊN BẢN 3 (19:21:05) vào FRONTEND_AGENT_PROMPT.md.
- Cập nhật 19:27:44: Backend HOÀN THÀNH chức năng 7 (log 19:25:14, /api/stats/*,
  api_docs 0.9.0, test 58/58) → YC-009 xong. Frontend đã nối (stats.js gọi API
  thật; mock chỉ khi API 404). CHECKLIST_UC_THUC_HIEN.md cập nhật UC20/UC28
  phần thống kê đã xong (xuất báo cáo chức năng 8 vẫn chưa).
- Cập nhật 19:32:55: Frontend chức năng 8 Xuất CSV (log 19:31:59, 3 nút +
  api.js /api/export/* + downloadFile, test 9/9) — Backend chưa có → YC-010.
  Prompt Frontend không đổi (P.3 khớp).
- Cập nhật 19:37:21: Backend HOÀN THÀNH chức năng 8 (log 19:34:48,
  /api/export/*.csv, BOM UTF-8, api_docs 0.10.0, test 62/62) → YC-010 xong;
  Frontend đã nối (books/borrow/stats.js). **8/8 chức năng quản lý: Backend +
  Frontend đều đã có code** (còn chờ log chính thức cho vài phần Frontend).
- Cập nhật 20:00:48: Frontend admin-config.html/js (UC24/26/27) + Thu phạt UC19
  (mock) + DAT_TRUOC (log 20:00:07, 19/19) — Backend thiếu collect-fine +
  DAT_TRUOC → YC-011. UI admin cấu hình/backup/restore đã có; audit log UI chưa rõ.
- Cập nhật 20:28:18: Backend xong Demo (19:50:00), Thu phạt (20:05:33, 67/67),
  Xoá lịch sử yêu cầu (20:15, 0.12.0). Server đã restart. Frontend nối delete
  requests; còn mock: danh sách phạt (borrow.js), reservations (YC-007);
  DAT_TRUOC Backend chưa có.

## Đối chiếu chức năng (cập nhật 09:50:40)
- 1 (đăng nhập/phân quyền): Backend + Frontend có code; phần admin-only Backend
  xong, Frontend mới có khung.
- 2 (quản lý sách): Backend + Frontend có code, đã nối API.
- 3 (quản lý độc giả): Backend xong (/api/readers + test); Frontend CHƯA.
- 3 (cập nhật): Backend + Frontend đều xong (log Backend 09:49:03 + Frontend 10:03:12).
- 4 (mượn/trả/gia hạn/phạt): Backend xong (log 10:27:48); Frontend CHƯA.
- 4 (cập nhật): Backend xong; Frontend đã nối /api/borrows theo quét (chưa log).
- 5 (tra cứu sách): Backend xong (log 10:43:48); Frontend đã có search.html/
  search.js nối query (chưa log).
- 6-8: chưa thấy code. AI-1/2/3: chưa thấy code (Backend đã sẵn dữ liệu cho
  AI-1 qua /api/books và AI-3 qua BorrowDetails/FineHistory).
- 6 (đặt trước): Backend xong (log 19:02:38); Frontend có UI nhưng còn mock
  fallback, chờ xác nhận API thật (YC-007).
- 4/6 mở rộng (UC11 thông báo): Frontend xong phần UI (log 19:11:17); Backend
  đã có GET /api/notifications (log 19:16:09); đánh dấu đã đọc chờ sau.
- 7 (thống kê): Frontend có UI (log 19:21:47, mock); Backend chưa có → YC-009.
- 7 (cập nhật): Backend xong (log 19:25:14, 58/58); Frontend đã nối API thật.
- 8 (xuất CSV): Frontend có UI + config (log 19:31:59); Backend chưa có → YC-010.
- 8 (cập nhật): Backend xong (log 19:34:48, 62/62); Frontend đã nối downloadFile.
- TỔNG KẾT 8 CHỨC NĂNG QUẢN LÝ: 1-8 đều có Backend + Frontend (hoàn thành 19:34:48).
- UC19/24/26/27: Frontend có UI (20:00:07); Backend cần collect-fine + DAT_TRUOC (YC-011).
- UC19 cập nhật: collect-fine xong (20:05:33); Frontend nối danh sách phạt chưa.
- UC07/08/09: xoá lịch sử yêu cầu xong (20:15) — Frontend đã nối (20:12-20:14).
- 4 (mở rộng): có luồng yêu cầu reader → duyệt thủ thư (requests, 0.6.0);
  chờ Backend bổ sung so_ngay_muon (YC-005). Đăng ký độc giả + lịch sử mượn
  cá nhân đã có (register, my-borrows); xoá lịch sử chờ YC-006.
- Admin: đã có accounts + categories/publishers UI/API (cần xác nhận giữ hay bỏ
  theo mâu thuẫn 09:55 vs 17:35).
- 4-8: chưa thấy code.
- AI-1/2/3: chưa thấy code (chỉ prompt).

## Đề bài gốc (đã đọc DE_BAI.md 2026-08-09)
- 8 chức năng quản lý (3.1): 1 đăng nhập/phân quyền 3 vai trò; 2 quản lý sách;
  3 quản lý độc giả; 4 mượn/trả/gia hạn/phạt; 5 tra cứu sách; 6 đặt trước;
  7 thống kê; 8 xuất danh sách/báo cáo.
- 3 chức năng AI (3.2): AI-1 chatbot tra cứu sách; AI-2 tóm tắt sách;
  AI-3 gợi ý sách liên quan (thể loại, tác giả, lịch sử mượn đã ẩn nhạy cảm).
- Ràng buộc: không bịa mã sách/trạng thái sách; không gửi dữ liệu cá nhân độc
  giả cho AI nếu chỉ cần dữ liệu sách; prompt template riêng cho từng chức năng.

## Quy trình vòng lặp (đã đọc QUY_TRINH_CHAY_TUAN_TU.md)
- Thứ tự: 1 Frontend → 2 Backend → 3 AI Engine → 4 Thư Ký quét + đối chiếu →
  5 Trợ Lý rà soát và chốt lệnh vòng tiếp theo.
- Trợ Lý không viết code, chỉ điều phối; Thư Ký không sửa file agent khác.

## Minh chứng AI
- File tổng hợp: thuky/MINH_CHUNG_AI_FRONTEND_BACKEND.md (tạo 2026-08-09 17:08:34)
- Chứa timeline, log chính thức nguyên văn, danh sách file, kết quả test và
  các phát hiện từ quét của Backend + Frontend từ đầu tới nay.
- QUY TẮC (17:13:53): mỗi lần người dùng gọi "cập nhật thư ký" / quét lại,
  PHẢI cập nhật luôn file minh chứng này (người dùng cần nộp).
- Bản sao nộp: promtAI/MINH_CHUNG_AI_FRONTEND_BACKEND.md — đồng bộ mỗi lần cập nhật.
- QUY TẮC LUÔN LƯU PROMPT (18:23:55): mỗi lần quét/cập nhật, kiểm tra
  Backend/AGENTS.md + Frontend/AGENTS.md + AI_Engine/AI.txt; nếu đổi thì cập
  nhật ngay bản sao trong promtAI dạng lịch sử (thêm phiên bản, giữ bản cũ).

## Prompt riêng của từng agent (thư mục promtAI)
- promtAI/BACKEND_AGENT_PROMPT.md — lịch sử đầy đủ: P.1 (06:11:05) + P.2 (09:54:52 — bản hiện tại, gộp bổ sung 07:54 + 09:54)
- promtAI/FRONTEND_AGENT_PROMPT.md — lịch sử đầy đủ: P.1 (07:54:08) + P.2 (09:54:52)
- promtAI/AI_ENGINE_AGENT_PROMPT.md — lịch sử đầy đủ: P.1 (06:12:29) + P.2 (07:54:08)
- Lưu riêng 3 file để tránh lẫn prompt giữa các agent.
- Mỗi file ghi nguyên văn từ phiên bản đầu đến phiên bản hiện tại.

## Đối chiếu chức năng đề bài (kết quả quét 2026-08-09 07:05:39)
- Chức năng 1 (đăng nhập, phân quyền) và 2 (quản lý sách): có code Backend
  (API login + CRUD sách) + có UI Frontend, NHƯNG Frontend chưa nối API
  (api.js config trống).
- Chức năng 3-8: chưa thấy code nào — chỉ có prompt liệt kê.
- AI-1, AI-2, AI-3: chưa thấy code nào — chỉ có prompt liệt kê.
- Đây là kết quả quét tự động, có thể sai; cần người dùng xác nhận nếu quan trọng.

## Định dạng log nhận vào
[BACKEND]/[FRONTEND]/[AI_ENGINE] <thời gian> - Thay đổi - Chức năng đề bài
liên quan - Ảnh hưởng agent khác.

## Cập nhật 2026-08-09 09:55 (Trợ Lý đồng bộ theo yêu cầu người dùng)

> Các mô tả cũ bên trên đã lỗi thời một phần — lấy phần này làm trạng thái mới nhất.

- Nguồn chuẩn: `hỗ trợ/DE_BAI.md`.
- Backend: login/phân quyền 3 role, CRUD sách, admin config library/AI, audit log, backup; ĐÃ XONG chức năng 3 — `/api/readers` (api_docs 0.3.0, test 9/9, migration 0004); ĐÃ XOÁ `/api/admin/librarians*` (quản lý thủ thư — ngoài đề bài).
- Frontend: login + books UI + UI_DESIGN.md; đã xoá admin-librarians.html/js; api.js chỉ còn login + books; CHƯA có UI độc giả (làm ở vòng sau).
- AI Engine: chỉ có AI.txt — chưa có code (là bước kế tiếp theo vòng).
- Dữ liệu demo: 5 sách S001-S005 (tiếng Việt chuẩn); 3 tài khoản admin/admin1, librarian/librarian1, reader/reader1.
- Server: đang chạy cổng 8000 — CẦN restart để `/api/readers` hoạt động.

## Bổ sung 2026-08-09 11:10 — Minh chứng sử dụng AI
- Thư Ký đã có nhiệm vụ + định dạng lưu minh chứng AI (`[MINH CHUNG AI]`) trong THU_KY_AGENT.md.
- File lưu trữ: `thuky/minh_chung_ai.md` (chỉ append) — hiện trống, chờ ghi chép từ người dùng/agent.
- Các lượt tới, khi người dùng/agent dùng AI (phân tích/viết code/review), nên gửi kèm prompt + phản hồi để Thư Ký ghi vào file này.

## Bổ sung 2026-08-09 18:40 — THỨ TỰ VÒNG LẶP (quy tắc cứng)
- Thứ tự bắt buộc: Frontend → Backend → AI Engine → Thư Ký. AI làm sau cùng.
- Người dùng báo "xong" → Trợ Lý tự gửi prompt bước kế tiếp, không cần nhắc.
- Trợ Lý/Thư Ký khi báo cáo phải nêu rõ bước hiện tại đang ở đâu trong thứ tự này.
