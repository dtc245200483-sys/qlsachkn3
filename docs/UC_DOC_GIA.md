# Sơ đồ Use Case — Độc giả (KT2, chưa tích hợp AI)

> Bám sát đề tài (mục 3.1, 3.2) + ứng dụng đã triển khai. AI-1/2/3 (UC03/04/05) sẽ thêm vào sơ đồ sau khi làm KT3.

```mermaid
flowchart LR
  DocGia((Độc giả))

  subgraph HT["Hệ thống quản lý thư viện"]
    UC01a["UC01 — Đăng ký"]
    UC01b["UC01 — Đăng nhập"]
    UC02["UC02 — Tra cứu sách<br/>(tên, tác giả, thể loại, trạng thái)"]
    UC06["UC06 — Đặt trước sách<br/>(chỉ khi sách hết)"]
    UC07["UC07 — Yêu cầu mượn sách"]
    UC08["UC08 — Yêu cầu trả sách"]
    UC09["UC09 — Yêu cầu gia hạn"]
    UC10["UC10 — Xem lịch sử mượn/trả & phạt"]
    UC11["UC11 — Nhận thông báo<br/>(nhắc hạn trả, sách đặt trước sẵn sàng)"]
    P1["Hồ sơ — Xem/cập nhật thông tin cá nhân"]
    P2["Hồ sơ — Đổi mật khẩu"]
    P3["Hồ sơ — Đổi ảnh đại diện"]
  end

  DocGia --> UC01a
  DocGia --> UC01b
  DocGia --> UC02
  DocGia --> UC06
  DocGia --> UC07
  DocGia --> UC08
  DocGia --> UC09
  DocGia --> UC10
  DocGia --> UC11
  DocGia --> P1
  DocGia --> P2
  DocGia --> P3

  UC06 -.->|extend: sách về → báo| UC11
  UC07 -.->|extend: gửi Thủ thư xử lý| UC15
  UC08 -.->|extend: gửi Thủ thư xử lý| UC16
  UC09 -.->|extend: gửi Thủ thư xử lý| UC17

  subgraph TT["Thủ thư (xử lý yêu cầu của độc giả)"]
    UC15["UC15 — Xử lý phiếu mượn"]
    UC16["UC16 — Xử lý phiếu trả"]
    UC17["UC17 — Xử lý gia hạn"]
  end
```

## Ghi chú

- **Độc giả không tự mượn/trả/gia hạn trực tiếp** — chỉ gửi **Yêu cầu** (UC07/08/09); Thủ thư xử lý (UC15/16/17). Đúng phân vai đề tài.
- **Đặt trước** chỉ được tạo khi sách hết/đang mượn hết; khi sách trả về hệ thống chuyển thành "Sẵn sàng" và thông báo (UC11).
- **Hồ sơ cá nhân** (P1/P2/P3) là phần mở rộng đã triển khai (Profile).
- **AI-1/2/3 (UC03/04/05)** chưa vẽ — sẽ bổ sung ở giai đoạn KT3.
