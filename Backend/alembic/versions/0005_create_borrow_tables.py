"""create borrow, borrow details and fine history tables

Revision ID: 0005
Revises: 0004
Create Date: 2026-08-09

"""
import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "BorrowSlips",
        sa.Column("ma_phieu", sa.Unicode(length=20), nullable=False),
        sa.Column("ma_doc_gia", sa.Unicode(length=20), nullable=False),
        sa.Column("ngay_muon", sa.DateTime(), nullable=False),
        sa.Column("han_tra", sa.DateTime(), nullable=False),
        sa.Column("ngay_tra", sa.DateTime(), nullable=True),
        sa.Column("trang_thai", sa.Unicode(length=20), nullable=False),
        sa.Column("so_lan_gia_han", sa.Integer(), nullable=False),
        sa.CheckConstraint("trang_thai IN ('dang_muon', 'da_tra')", name="ck_borrow_slips_status"),
        sa.CheckConstraint("so_lan_gia_han >= 0", name="ck_borrow_slips_renew_count"),
        sa.PrimaryKeyConstraint("ma_phieu", name="pk_borrow_slips"),
    )
    op.create_index("ix_borrow_slips_ma_doc_gia", "BorrowSlips", ["ma_doc_gia"])

    op.create_table(
        "BorrowDetails",
        sa.Column("ma_phieu", sa.Unicode(length=20), nullable=False),
        sa.Column("ma_sach", sa.Unicode(length=20), nullable=False),
        sa.Column("so_luong", sa.Integer(), nullable=False),
        sa.Column("ngay_tra_chi_tiet", sa.DateTime(), nullable=True),
        sa.CheckConstraint("so_luong > 0", name="ck_borrow_details_so_luong"),
        sa.PrimaryKeyConstraint("ma_phieu", "ma_sach", name="pk_borrow_details"),
    )
    op.create_index("ix_borrow_details_ma_sach", "BorrowDetails", ["ma_sach"])

    op.create_table(
        "FineHistory",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ma_phieu", sa.Unicode(length=20), nullable=False),
        sa.Column("ma_doc_gia", sa.Unicode(length=20), nullable=False),
        sa.Column("so_ngay_qua_han", sa.Integer(), nullable=False),
        sa.Column("so_tien", sa.Numeric(12, 2), nullable=False),
        sa.Column("ngay_tinh", sa.DateTime(), nullable=False),
        sa.CheckConstraint("so_ngay_qua_han >= 0", name="ck_fine_history_days"),
        sa.CheckConstraint("so_tien >= 0", name="ck_fine_history_amount"),
        sa.PrimaryKeyConstraint("id", name="pk_fine_history"),
    )
    op.create_index("ix_fine_history_ma_phieu", "FineHistory", ["ma_phieu"])


def downgrade() -> None:
    op.drop_index("ix_fine_history_ma_phieu", table_name="FineHistory")
    op.drop_table("FineHistory")
    op.drop_index("ix_borrow_details_ma_sach", table_name="BorrowDetails")
    op.drop_table("BorrowDetails")
    op.drop_index("ix_borrow_slips_ma_doc_gia", table_name="BorrowSlips")
    op.drop_table("BorrowSlips")
