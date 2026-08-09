"""
Dọn dữ liệu cũ hơn N ngày (mặc định 30) — chống phình dữ liệu và trùng mã.

CHỈ XOÁ:
  - Yêu cầu đã xử lý (DA_DUYET / TU_CHOI) có ngay_tao < cutoff.
  - Phiếu mượn ĐÃ TRẢ (da_tra, có ngay_tra < cutoff) kèm chi tiết + phạt.

KHÔNG BAO GIỜ XOÁ:
  - Phiếu đang mượn (dang_muon).
  - Yêu cầu đang chờ xử lý (CHO_XU_LY).
  - Sách, tài khoản, độc giả, cấu hình.

Cách chạy:
  python cleanup_old_data.py --dry-run            # xem trước, không xoá
  python cleanup_old_data.py --days 30            # xoá dữ liệu cũ hơn 30 ngày

Để tự chạy mỗi 30 ngày: đăng ký Windows Task Scheduler hoặc lên lịch
trong Backend (khuyến nghị Backend tích hợp job này).
"""

import argparse
import datetime
import os
import sys

import pyodbc

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CONNECTION_STRING = os.getenv(
    "LIBRARY_DB_CS",
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost\\QUANGHUNG;DATABASE=LibraryDB;"
    "Trusted_Connection=Yes;TrustServerCertificate=yes",
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Dọn dữ liệu cũ của thư viện")
    parser.add_argument("--days", type=int, default=30, help="Số ngày giữ lại (mặc định 30)")
    parser.add_argument("--dry-run", action="store_true", help="Chỉ báo cáo, không xoá")
    args = parser.parse_args()

    cutoff = datetime.datetime.now() - datetime.timedelta(days=args.days)
    cn = pyodbc.connect(CONNECTION_STRING, timeout=10)
    cur = cn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM YeuCau "
        "WHERE trang_thai IN ('DA_DUYET','TU_CHOI') AND ngay_tao < ?",
        cutoff,
    )
    old_requests = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM BorrowSlips "
        "WHERE trang_thai='da_tra' AND ngay_tra < ?",
        cutoff,
    )
    old_slips = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM BorrowSlips WHERE trang_thai='dang_muon'")
    active_slips = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM YeuCau WHERE trang_thai='CHO_XU_LY'")
    pending_requests = cur.fetchone()[0]

    print("Cutoff:", cutoff)
    print("Yêu cầu đã xử lý cũ:", old_requests)
    print("Phiếu đã trả cũ:", old_slips)
    print("Giữ nguyên (không xoá): phiếu đang mượn =", active_slips,
          "| yêu cầu chờ =", pending_requests)

    if args.dry_run:
        print("DRY-RUN: chưa xoá gì.")
        cn.close()
        return 0

    cur.execute(
        "DELETE FROM FineHistory WHERE ma_phieu IN ("
        "SELECT ma_phieu FROM BorrowSlips WHERE trang_thai='da_tra' AND ngay_tra < ?)",
        cutoff,
    )
    cur.execute(
        "DELETE FROM BorrowDetails WHERE ma_phieu IN ("
        "SELECT ma_phieu FROM BorrowSlips WHERE trang_thai='da_tra' AND ngay_tra < ?)",
        cutoff,
    )
    cur.execute(
        "DELETE FROM BorrowSlips WHERE trang_thai='da_tra' AND ngay_tra < ?",
        cutoff,
    )
    cur.execute(
        "DELETE FROM YeuCau WHERE trang_thai IN ('DA_DUYET','TU_CHOI') AND ngay_tao < ?",
        cutoff,
    )
    cn.commit()
    print("Đã xoá dữ liệu cũ hơn", args.days, "ngày.")
    cn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
