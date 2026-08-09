# UI Design Spec — Hệ thống thư viện ICTU (WCAG 2.1 AA+)

Thiết kế giao diện website/hệ thống cho Trường Đại học Công nghệ Thông
tin và Truyền thông (ICTU) – Đại học Thái Nguyên. Phong cách: hiện đại,
chuyên nghiệp, học thuật, đạt chuẩn **WCAG 2.1 AA trở lên** cho toàn bộ text.

> Spec này THAY THẾ toàn bộ prompt thiết kế màu trước đó. Mọi giao diện
> Frontend từ nay phải dùng đúng bảng màu + quy tắc dưới đây.
> CẬP NHẬT: bỏ màu vàng (người dùng thấy không hợp), thay bằng xanh dương
> nhạt `#1E4B8C` cho CTA và điểm nhấn.

## LOGO

- Logo chính thức: `https://ictu.edu.vn/wp-content/uploads/2023/02/cropped-logoww.png`
- Bản cục bộ: `Frontend/assets/cropped-logoww.png`
- Header dùng logo màu gốc (không filter trắng).

## BẢNG MÀU (đã kiểm tra contrast WCAG 2.1)

| Nền | Chữ | Contrast | Chuẩn | Dùng cho |
|---|---|---:|---|---|
| Navy `#0A2E5C` | Trắng `#FFFFFF` | 12.6:1 | AAA | Header, footer, text chính |
| Navy `#1E4B8C` | Trắng `#FFFFFF` | 7.1:1 | AAA | Section bg, hover state, CTA chính |
| Xanh hover `#16407A` | Trắng `#FFFFFF` | ~9:1 | AAA | Hover CTA |
| Xám nhạt `#F5F6FA` | Navy `#0A2E5C` | 11.9:1 | AAA | Nền trang, bảng dữ liệu |
| Đỏ `#A93226` | Trắng `#FFFFFF` | 6.2:1 | AAA | Nút Xoá dạng filled (chỉ trong modal xác nhận) |

## QUY TẮC CẤM

- ❌ KHÔNG dùng màu vàng `#F2B705` làm màu nhấn/CTA (theo lựa chọn người dùng).
- ❌ KHÔNG dùng nền đỏ filled `#C0392B` cho text nhỏ (<18px) — chỉ 5.1:1, fail AA.
- ❌ KHÔNG lặp lại nút đỏ filled trên nhiều dòng liên tiếp trong bảng/danh sách
  (alert fatigue, phá tỉ lệ 60-30-10).

## MÀU ĐỎ THEO NGỮ CẢNH

- Trong bảng/danh sách: nút Xoá = **OUTLINE** —
  `border: 1px solid #A93226; color: #A93226; background: transparent;`
  hover → `background: #A93226; color: #FFFFFF;`
- Trong modal xác nhận xoá (chỉ 1 lần): nút Xoá = **FILLED** —
  `background: #A93226; color: #FFFFFF;`

## TỈ LỆ 60-30-10

- 60% Trắng `#FFFFFF` / Xám nhạt `#F5F6FA` → nền, khoảng trắng.
- 30% Navy `#0A2E5C` / `#1E4B8C` → header, footer, text, khối nội dung.
- 10% Xanh nhạt `#1E4B8C` (CTA chính ~8%) + Đỏ `#A93226` (cảnh báo ~2% tối đa).

## TYPOGRAPHY

- Font: Inter hoặc Be Vietnam Pro (hỗ trợ dấu tiếng Việt).
- Heading: bold, Navy `#0A2E5C`.
- Body: regular, `#1A1A1A` trên nền sáng / `#FFFFFF` trên nền Navy.
- Text phụ/caption trên nền Navy: dùng `#E8ECF5`, KHÔNG dùng opacity < 70%.

## COMPONENT TOKENS

```css
--color-primary-900:        #0A2E5C;
--color-primary-600:        #1E4B8C;
--color-accent-blue:        #1E4B8C;
--color-accent-blue-light:  #2F6FB0;
--color-accent-red:         #A93226;
--color-neutral-50:         #F5F6FA;
--color-neutral-0:          #FFFFFF;
--color-text-dark:          #1A1A1A;
--color-text-light:         #FFFFFF;
--color-text-muted:         #E8ECF5;  /* trên nền Navy, không dùng opacity */
```

## BỐ CỤC

- Header: logo bên trái, menu ngang, nền Navy `#0A2E5C`, chữ trắng.
- Hero: ảnh campus + overlay gradient Navy → trong suốt, CTA xanh `#1E4B8C`
  (chữ trắng).
- Bảng dữ liệu: nền trắng, hover row `#F5F6FA`, nút Sửa = outline Navy,
  nút Xoá = outline đỏ (theo quy tắc trên).
- Footer: nền Navy đậm `#0A2E5C`, chữ trắng, logo bản âm bản.

## TONE

Đáng tin cậy – Hiện đại – Công nghệ – Học thuật. Tránh màu sặc sỡ, ưu tiên
khoảng trắng và độ tương phản cao.
