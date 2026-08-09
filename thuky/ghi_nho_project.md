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
- Cập nhật 23:19:29: Backend SVNET (21:52:51, 0009), role_display (21:56:59,
  68/68), sort/order (23:16:54, 0.13.0, 75/75). Git + .env.example + README +
  docs + QA đã có → KT2 đủ 10/10. Frontend sortBooksBackend còn FALSE → YC-012.
- Cập nhật 02:17:44 (10/08): Backend Hồ sơ cá nhân (02:15:52, /api/profile/me
  + password + avatar, static avatars, api_docs 0.14.0, test 82/82). Frontend
  profile.html/profile.js nối API thật; sortBooksBackend=true; borrow.js nối
  phạt thật → YC-012 còn phần reservations mock; YC-011 chỉ còn DAT_TRUOC.
- Cập nhật 03:01:24 (10/08): Backend 0.16.0 — validation email ICTU/SĐT (0010),
  phạt = ĐIỂM (0011), email theo tên, backfill + restart (86/86). Frontend
  profile/admin-config theo kịp; NHƯNG fineOut còn map so_tien → YC-013.
- Cập nhật 03:07:46 (10/08): Frontend log 03:07:07 — fineOut soDiem,
  collectFineOut so_diem_da_thu/diem_con_lai, hiển thị điểm → YC-013 xong,
  cảnh báo 14 đóng.
- Cập nhật 04:01:20 (10/08): Backend 0.17.0 (03:59:25) — thêm/sửa/xoá độc giả
  chỉ admin, PUT /api/readers/{ma}/lock (admin+librarian); test 86/86; restart.
  Frontend nối lockReader; menu độc giả chỉ librarian → YC-014.
- Cập nhật 04:53:07 (10/08): Backend DAT_TRUOC xong (04:52:00, migration 0012,
  api_docs 0.19.0, test 90/90) → YC-011 đóng. Menu độc giả admin+librarian
  (04:31:48) → YC-014 đóng. Còn: so_ngay_muon (YC-005/YC-015), reservations mock.
- Cập nhật 05:01:03 (10/08): Khôi phục dữ liệu demo theo yêu cầu người dùng —
  xoá + seed lại PM001–PM004 (PM001/PM004 dang_muon, PM002/PM003 da_tra,
  PM003 phạt 4 điểm); xác minh API dang_muon = 2 phiếu.
- Cập nhật 05:02:44 (10/08): S005 "Lịch sử Việt Nam hiện đại" soLuong 0 → 2
  theo yêu cầu người dùng; đã xác minh API; RV002 (CHO_XU_LY) vẫn còn, chưa
  tự ý huỷ/duyệt.
- YC-2026-08-10-016 (05:05:08): bỏ Xuất CSV ở books/stats; thêm Xoá lịch sử
  đặt trước — chờ người dùng xác nhận phạm vi xoá trước khi gửi agent.
- YC-2026-08-10-017 (05:06:54): chặn Gửi yêu cầu khi chưa chọn sách — code đã
  có validate items rỗng, cần disable nút + bump version JS (nghi cache cũ).
- Cập nhật 05:48:15 (10/08): Backend xong Xoá lịch sử đặt trước (05:13:10,
  0.20.0, 94/94) + Export reservations.csv + accounts chỉ thủ thư (05:22:45,
  0.21.0, 95/95). Frontend nối xoá lịch sử + accounts thủ thư (theo quét).
  CHƯA LÀM: bỏ Xuất CSV books/stats (YC-016), disable nút gửi (YC-017),
  so_ngay_muon (YC-015), reservations mock (YC-007).

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
- UC02/KT2: tìm/lọc/sắp xếp xong (10:43:48 + 23:16:54); Frontend dropdown có,
  chờ bật sortBooksBackend.
- Mở rộng Profile (10/08): Backend xong (02:15:52, 82/82); Frontend xong
  (02:09) — profile.html + avatar + đổi mật khẩu.
- Phạt ĐIỂM (0.16.0): Backend xong (02:56:16); Frontend chưa cập nhật fineOut
  (so_tien → so_diem) → YC-013.
- Phạt ĐIỂM (cập nhật): Frontend đã theo (log 03:07:07) → UC19 khép kín.
- UC14 (0.17.0): thêm/sửa/xoá chỉ admin; lock librarian+admin — Frontend nối
  lockReader; menu cần xác nhận (YC-014).
- UC06/07 (DAT_TRUOC): Backend xong (04:52:00) — approve tạo reservation thật.

## KT2 — Xác nhận 10/10 (2026-08-09 23:19)
1. Cấu trúc ✅ 2. Đăng nhập/phân quyền ✅ 3. CRUD ✅ 4. Tìm/lọc/sắp xếp ✅
5. Thống kê/báo cáo ✅ 6. UI ✅ 7. CSDL + dữ liệu mẫu ✅ 8. Xử lý lỗi ✅
9. Minh chứng AI ✅ 10. README/.env.example/git ✅
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
