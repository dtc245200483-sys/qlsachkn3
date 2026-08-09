# Prompt Ý 3 — Hồ sơ nộp bài (dán vào Codex hoặc giao cho Thư Ký)

```text
Agent Hồ Sơ — Ý 3 (Chuẩn bị hồ sơ nộp bài, sau khi xong UI admin + dữ liệu mẫu):
1. Tạo thư mục docs/ trong D:\ung dung tri tue nhan ao\app với các tài liệu:
   - SRS.md — đặc tả yêu cầu: phạm vi, 3 actor, 8 chức năng quản lý + 3 chức năng AI, mỗi chức năng có đầu vào → xử lý → đầu ra; yêu cầu phi chức năng (bảo mật, phân quyền, hiệu năng, sao lưu, UX) — dựa trên hỗ trợ/DE_BAI.md + REQUIREMENTS_QA.md.
   - USE_CASE.md — lấy tài liệu Actor & Use Case (28 UC) + sơ đồ Mermaid đã có; ghi chú phần "(Mở rộng)".
   - ERD.md — vẽ ERD từ migrations 0001-0008: Users, Books, Readers, BorrowSlips, BorrowDetails, FineHistory, DatTruoc, YeuCau, TheLoai, Nxb, LibraryConfig, AIConfig, AuditLog; nêu khóa chính/khóa ngoại + ràng buộc (số lượng ≥ 0, trạng thái thẻ, giới hạn gia hạn, phạt...).
   - KIEN_TRUC.md — kiến trúc: Frontend HTML/JS ↔ FastAPI ↔ SQL Server ↔ AI Engine; luồng dữ liệu chính (tra cứu, mượn/trả, đặt trước, AI).
   - AI_DESIGN.md — vị trí AI-1/2/3, prompt template gốc + ràng buộc (không bịa sách, ẩn dữ liệu nhạy cảm), luồng gọi AI qua Backend.
2. Bổ sung minh chứng AI: promtAI/MINH_CHUNG_AI_FRONTEND_BACKEND.md — đảm bảo có prompt → phản hồi → phần dùng nguyên → phần đã chỉnh sửa → nhận xét kiểm chứng (tối thiểu 5 mục, đủ tiêu chí 9 KT1/KT2).
3. Tạo Backend/.env.example — copy cấu trúc .env nhưng thay JWT_SECRET, DATABASE_URL... bằng placeholder (KHÔNG chứa giá trị thật).
4. Git: git init tại D:\ung dung tri tue nhan ao\app; tạo .gitignore (bỏ .env, __pycache__, *.pyc, *.bak, thư mục backup); commit phân đoạn rõ ràng (VD: "feat: auth+books", "feat: readers/borrows/reservations", "docs: SRS/ERD").
5. Cập nhật README.md: hướng dẫn cài đặt (pip install, alembic upgrade head, uvicorn), tài khoản demo (admin/admin1, librarian/librarian1, reader/reader1, docgia1/docgia1...), cách chạy seed_demo.py.
6. Gửi log cho Thư Ký:
   [HOSO] <thời gian> - Thay đổi: <mô tả> - Chức năng đề bài: toàn bộ - Ảnh hưởng: tài liệu
```

## Cách dùng

- Cách 1: dán nguyên khối vào cửa sổ Codex (chat/task mới) để chạy.
- Cách 2: giao cho Thư Ký Agent (vì hệ thống không có agent Hồ Sơ riêng — Thư Ký đang quản lý promtAI + minh chứng).
