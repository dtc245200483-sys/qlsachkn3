"""create dat truoc table

Revision ID: 0007
Revises: 0006
Create Date: 2026-08-09

"""
import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "DatTruoc",
        sa.Column("ma_dat", sa.Unicode(length=20), nullable=False),
        sa.Column("ma_sach", sa.Unicode(length=20), nullable=False),
        sa.Column("ma_doc_gia", sa.Unicode(length=20), nullable=False),
        sa.Column("ngay_dat", sa.DateTime(), nullable=False),
        sa.Column("trang_thai", sa.Unicode(length=20), nullable=False),
        sa.Column("ngay_xu_ly", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "trang_thai IN ('CHO_XU_LY', 'SAN_SANG', 'DA_MUON', 'HUY')",
            name="ck_dat_truoc_trang_thai",
        ),
        sa.PrimaryKeyConstraint("ma_dat", name="pk_dat_truoc"),
    )
    op.create_index("ix_dat_truoc_ma_sach", "DatTruoc", ["ma_sach"])
    op.create_index("ix_dat_truoc_ma_doc_gia", "DatTruoc", ["ma_doc_gia"])
    op.create_index(
        "uq_dat_truoc_active",
        "DatTruoc",
        ["ma_sach", "ma_doc_gia"],
        unique=True,
        mssql_where=sa.text("trang_thai IN ('CHO_XU_LY', 'SAN_SANG')"),
    )
    op.create_foreign_key("fk_dat_truoc_sach", "DatTruoc", "Books", ["ma_sach"], ["ma"])
    op.create_foreign_key("fk_dat_truoc_reader", "DatTruoc", "Readers", ["ma_doc_gia"], ["ma"])


def downgrade() -> None:
    op.drop_constraint("fk_dat_truoc_reader", "DatTruoc", type_="foreignkey")
    op.drop_constraint("fk_dat_truoc_sach", "DatTruoc", type_="foreignkey")
    op.drop_index("uq_dat_truoc_active", table_name="DatTruoc")
    op.drop_index("ix_dat_truoc_ma_doc_gia", table_name="DatTruoc")
    op.drop_index("ix_dat_truoc_ma_sach", table_name="DatTruoc")
    op.drop_table("DatTruoc")
