"""
search_engine.py — Module tìm kiếm sơ bộ (fuzzy search) trên danh sách sách.

Dùng thư viện rapidfuzz để khớp từ khóa mờ (partial_ratio) trên 3 trường:
  - ten_sach
  - tac_gia
  - tom_tat_noi_dung

Kết quả được sắp xếp giảm dần theo điểm khớp và giới hạn tối đa 20 sách.
"""

import sys
from typing import Optional

# Đảm bảo hiển thị đúng tiếng Việt trên Windows console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from rapidfuzz import fuzz
except ImportError as e:
    raise ImportError(
        "Thư viện 'rapidfuzz' chưa được cài đặt. "
        "Hãy chạy: pip install rapidfuzz"
    ) from e

# Ngưỡng điểm khớp tối thiểu (0–100)
NGUONG_DIEM_KHOP: int = 60
# Số kết quả tối đa trả về
SO_KET_QUA_TOI_DA: int = 20


def _chuan_hoa(van_ban: Optional[str]) -> str:
    """
    Chuẩn hóa chuỗi văn bản để so sánh: viết thường, loại khoảng trắng thừa.
    Trả về chuỗi rỗng nếu đầu vào là None hoặc không phải chuỗi.
    """
    if not isinstance(van_ban, str):
        return ""
    return van_ban.strip().lower()


def tim_kiem_so_bo(tu_khoa: str, danh_sach_sach: list[dict]) -> list[dict]:
    """
    Tìm kiếm sơ bộ theo từ khóa trên danh sách sách bằng thuật toán fuzzy match.

    Tham số:
        tu_khoa (str):             Từ khóa tìm kiếm của độc giả.
        danh_sach_sach (list[dict]): Danh sách các dict thông tin sách từ cơ sở dữ liệu.
                                    Mỗi dict có thể gồm các trường:
                                    ten_sach, tac_gia, tom_tat_noi_dung,
                                    so_luong_con, ma_sach, ...

    Trả về:
        list[dict]: Danh sách sách khớp, đã sắp xếp giảm dần theo điểm khớp,
                    tối đa SO_KET_QUA_TOI_DA (20) kết quả.
                    Mỗi phần tử được bổ sung thêm 2 trường:
                    - "diem_khop" (float): Điểm khớp cao nhất trong các trường đã kiểm tra.
                    - "ly_do_khop_so_bo" (str): Danh sách các trường có điểm khớp >= ngưỡng,
                      ví dụ: "tên sách, nội dung tóm tắt"
    """
    if not tu_khoa or not isinstance(tu_khoa, str):
        return []
    if not danh_sach_sach or not isinstance(danh_sach_sach, list):
        return []

    tu_khoa_chuan = _chuan_hoa(tu_khoa)
    if not tu_khoa_chuan:
        return []

    ket_qua_co_diem: list[dict] = []

    for sach in danh_sach_sach:
        if not isinstance(sach, dict):
            continue

        # Lấy giá trị từng trường, chuẩn hóa trước khi so sánh
        ten_sach_val = _chuan_hoa(sach.get("ten_sach"))
        tac_gia_val = _chuan_hoa(sach.get("tac_gia"))
        tom_tat_val = _chuan_hoa(sach.get("tom_tat_noi_dung"))

        # Tính điểm partial_ratio cho từng trường
        diem_ten = fuzz.partial_ratio(tu_khoa_chuan, ten_sach_val) if ten_sach_val else 0
        diem_tac_gia = fuzz.partial_ratio(tu_khoa_chuan, tac_gia_val) if tac_gia_val else 0
        diem_tom_tat = fuzz.partial_ratio(tu_khoa_chuan, tom_tat_val) if tom_tat_val else 0

        # Ghi nhận các trường vượt ngưỡng
        truong_khop: list[str] = []
        if diem_ten >= NGUONG_DIEM_KHOP:
            truong_khop.append("tên sách")
        if diem_tac_gia >= NGUONG_DIEM_KHOP:
            truong_khop.append("tác giả")
        if diem_tom_tat >= NGUONG_DIEM_KHOP:
            truong_khop.append("nội dung tóm tắt")

        # Bỏ qua sách không khớp ở bất kỳ trường nào
        if not truong_khop:
            continue

        diem_cao_nhat = max(diem_ten, diem_tac_gia, diem_tom_tat)

        # Tạo bản sao để không làm thay đổi dict gốc
        sach_ket_qua = dict(sach)
        sach_ket_qua["diem_khop"] = diem_cao_nhat
        sach_ket_qua["ly_do_khop_so_bo"] = ", ".join(truong_khop)

        ket_qua_co_diem.append(sach_ket_qua)

    # Sắp xếp giảm dần theo điểm khớp
    ket_qua_co_diem.sort(key=lambda x: x["diem_khop"], reverse=True)

    # Giới hạn số kết quả tối đa
    return ket_qua_co_diem[:SO_KET_QUA_TOI_DA]


# ---------------------------------------------------------------------------
# Chạy thử khi gọi trực tiếp file này
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    du_lieu_mau = [
        {
            "ten_sach": "Trí tuệ nhân tạo: Tiếp cận hiện đại",
            "tac_gia": "Stuart Russell & Peter Norvig",
            "tom_tat_noi_dung": "Giáo trình kinh điển về AI, bao gồm tìm kiếm, học máy, logic và ứng dụng.",
            "so_luong_con": 3,
        },
        {
            "ten_sach": "Python cho khoa học dữ liệu",
            "tac_gia": "Wes McKinney",
            "tom_tat_noi_dung": "Hướng dẫn sử dụng Python và thư viện pandas, numpy để phân tích dữ liệu.",
            "so_luong_con": 0,
        },
        {
            "ten_sach": "Lập trình Python cơ bản",
            "tac_gia": "Nguyễn Thành Nam",
            "tom_tat_noi_dung": "Sách nhập môn lập trình Python từ cơ bản đến ứng dụng thực tiễn.",
            "so_luong_con": 5,
        },
    ]

    ket_qua = tim_kiem_so_bo("trí tuệ nhân tạo", du_lieu_mau)
    print(f"Tìm thấy {len(ket_qua)} kết quả:")
    for s in ket_qua:
        print(f"  - {s['ten_sach']} | Điểm: {s['diem_khop']} | Khớp: {s['ly_do_khop_so_bo']}")
