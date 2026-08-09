# Quy trình chạy tuần tự 4 agent — Hệ thống quản lý thư viện tích hợp AI

## Nguyên tắc (theo yêu cầu người dùng 2026-08-09)

Mỗi vòng chạy theo đúng thứ tự:

1. **Frontend** — làm phần UI được giao trong lượt, tự kiểm tra, báo xong.
2. **Backend** — làm phần API/logic được giao trong lượt, tự kiểm tra, báo xong.
3. **AI Engine** — làm phần AI được giao trong lượt (AI-1/2/3), tự kiểm tra, báo xong.
4. **Thư Ký** — quét chủ động Backend/Frontend/AI_Engine, đối chiếu đề bài, ghi
   log vào `thuky/changelog_tong.md`, cảnh báo lệch pha vào `canh_bao_dong_bo.md`.
5. **Trợ Lý** — đọc log Thư Ký sau mỗi vòng, rà soát tiến độ, chốt lệnh cho vòng
   tiếp theo. Rồi quay lại bước 1.

> **QUY TẮC KHÔNG ĐƯỢC QUÊN:** người dùng báo xong bước nào → Trợ Lý tự gửi
> prompt bước kế tiếp ĐÚNG THỨ TỰ (Frontend → Backend → AI Engine → Thư Ký),
> không chờ nhắc, không đảo thứ tự. Đổi thứ tự phải xin xác nhận trước.

## Vai trò Trợ Lý trong vòng lặp

- Điều phối và chốt lệnh cho từng agent; KHÔNG viết code thay.
- KHÔNG ghi/sửa file trong Backend/Frontend/thuky/AI_Engine — chỉ đọc.
- Sau mỗi vòng, dựa trên log Thư Ký để báo cáo đã làm/chưa làm/đang dở.

## Trạng thái khởi điểm (2026-08-09)

- Backend: có `AGENTS.md` (prompt, chưa có code).
- AI Engine: có `AI.txt` (prompt, chưa có code).
- Frontend: thư mục trống — **chưa có prompt Frontend**.
- Thư Ký: có prompt + `changelog_tong.md` + `trang_thai_quet.md` (2 log quét
  đầu tiên, đều là prompt chưa phải code).
- ĐÃ BỔ SUNG vào `hỗ trợ`: `DE_BAI.md` (đề bài gốc mục 1–7), `KE_HOACH_9_TUAN.md`,
  `REQUIREMENTS_QA.md`, `TIEU_CHI_DANH_GIA.md` (10 tiêu chí + quy tắc + thông tin
  nhóm), `FRONTEND_AGENT_PROMPT.md` (bản nháp prompt Frontend — chờ duyệt).
- Công nghệ (framework Backend, CSDL, nhà cung cấp AI) chưa được chốt.

## Điều kiện bắt đầu vòng 1

1. Có prompt Frontend (người dùng cung cấp, hoặc duyệt bản nháp Trợ Lý soạn).
2. Có đề bài gốc để các agent đối chiếu đúng chức năng + ràng buộc.
3. Chốt công nghệ: Backend (FastAPI/Flask/Django), CSDL (SQLite/MySQL/
   PostgreSQL), AI (OpenAI/Gemini/Claude/Ollama...).
4. Chốt phạm vi vòng 1 (làm chức năng nào trong 8 quản lý + 3 AI).

## Rủi ro thứ tự Frontend → Backend → AI (cần ghi nhớ)

- Frontend cần biết API/field trước để gọi đúng; nếu chạy Frontend trước khi
  Backend chốt API, UI có thể phải làm lại (rework).
- Cách giảm rủi ro nếu giữ thứ tự này: vòng 1 giao Frontend dựng giao diện tĩnh
  theo prototype/đặc tả (chưa gọi API thật), Backend chốt API theo đúng màn
  hình đó, AI chạy sau khi Backend có API đã lọc dữ liệu.

## Cập nhật 2026-08-09 09:55
- Đã xoá "quản lý tài khoản thủ thư" (ngoài đề bài) — Frontend + Backend gỡ sạch, `/api/admin/librarians` → 404.
- Đã tạo 5 sách mẫu S001-S005 (qua API, tiếng Việt chuẩn).
- Backend vòng 2 (chức năng 3 Quản lý độc giả) ĐÃ XONG (09:49:03, test 9/9) — cần restart server để API live.
- Bước kế tiếp theo vòng: AI Engine (AI-1 chatbot tra cứu) → rồi Thư Ký quét → vòng sau Frontend làm UI độc giả/admin.
- Chứng minh chức năng 1 khi báo cáo: admin đăng nhập + librarian đăng nhập (quyền khác nhau), reader chỉ xem sách.
