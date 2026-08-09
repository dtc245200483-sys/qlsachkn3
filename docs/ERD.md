# ERD — Thiết kế cơ sở dữ liệu
## Hệ thống quản lý thư viện có tích hợp AI

> Vẽ từ migrations 0001-0008 (SQL Server, bảng `LibraryDB`).

```mermaid
erDiagram
    Users ||--o| Readers : "reader_id"
    Books }o--o| TheLoai : "theLoaiId"
    Books }o--o| Nxb : "nxbId"
    BorrowSlips ||--|{ BorrowDetails : "ma_phieu"
    BorrowSlips ||--o{ FineHistory : "ma_phieu"
    BorrowSlips }o--|| Readers : "ma_doc_gia"
    BorrowDetails }o--|| Books : "ma_sach"
    DatTruoc }o--|| Books : "ma_sach"
    DatTruoc }o--|| Readers : "ma_doc_gia"
    YeuCau }o--|| Readers : "ma_doc_gia"
    YeuCau o|--o| BorrowSlips : "ma_phieu"

    Users { int id PK
      string username UK
      string password_hash
      string ho_ten
      string role
      string reader_id FK
      bit is_active
      datetime created_at }
    Readers { string ma PK
      string hoTen
      string email UK
      string soDienThoai
      string loaiDocGia
      string trangThaiThe
      datetime ngayTao }
    Books { string ma PK
      string ten
      string tacGia
      string theLoai
      string nxb
      int namXb
      int soLuong
      string theLoaiId FK
      string nxbId FK }
    TheLoai { string ma PK
      string ten }
    Nxb { string ma PK
      string ten }
    BorrowSlips { string ma_phieu PK
      string ma_doc_gia
      datetime ngay_muon
      datetime han_tra
      datetime ngay_tra
      string trang_thai
      int so_lan_gia_han }
    BorrowDetails { string ma_phieu PK,FK
      string ma_sach PK,FK
      int so_luong
      datetime ngay_tra_chi_tiet }
    FineHistory { int id PK
      string ma_phieu
      string ma_doc_gia
      int so_ngay_qua_han
      decimal so_tien
      bit da_thu
      datetime ngay_thu
      datetime ngay_tinh }
    DatTruoc { string ma_dat PK
      string ma_sach FK
      string ma_doc_gia FK
      datetime ngay_dat
      string trang_thai
      datetime ngay_xu_ly }
    YeuCau { string ma_yeu_cau PK
      string loai
      string ma_doc_gia
      string ma_phieu FK
      string items
      string trang_thai
      datetime ngay_tao }
    LibraryConfig { int id PK
      int max_borrow_days
      decimal overdue_fine_per_day
      int max_books_at_once }
    AIConfig { int id PK
      string provider
      string model
      string api_key
      string prompt_template }
    AuditLog { int id PK
      string username
      string role
      string action
      string entity
      string entity_id
      string details
      datetime created_at }
```

## Bảng + khóa chính/ngoại + ràng buộc chính

| Bảng | PK | FK | Ràng buộc |
|---|---|---|---|
| Users | id | reader_id → Readers.ma | role IN (admin/librarian/reader); username unique; is_active |
| Readers | ma | — | email unique; loai IN (sinh_vien/giang_vien/khac); trangThaiThe IN (hoat_dong/khoa) |
| Books | ma | theLoaiId → TheLoai.ma; nxbId → Nxb.ma | soLuong ≥ 0 |
| TheLoai / Nxb | ma | — | không rỗng |
| BorrowSlips | ma_phieu | ma_doc_gia (logical → Readers) | trang_thai IN (dang_muon/da_tra); so_lan_gia_han ≥ 0 |
| BorrowDetails | (ma_phieu, ma_sach) | ma_sach → Books.ma | so_luong > 0 |
| FineHistory | id | ma_phieu (logical → BorrowSlips) | so_ngay_qua_han ≥ 0; so_tien ≥ 0; da_thu |
| DatTruoc | ma_dat | ma_sach → Books.ma; ma_doc_gia → Readers.ma | trang_thai IN (CHO_XU_LY/SAN_SANG/DA_MUON/HUY); unique active (sách+độc giả) |
| YeuCau | ma_yeu_cau | ma_doc_gia (logical) | loai IN (MUON/TRA/GIA_HAN); trang_thai IN (CHO_XU_LY/DA_DUYET/TU_CHOI) |
| LibraryConfig | id (=1) | — | max_borrow_days > 0; overdue_fine_per_day ≥ 0; max_books_at_once > 0 |
| AIConfig | id (=1) | — | singleton |
| AuditLog | id | — | tự ghi mọi thao tác quan trọng |
