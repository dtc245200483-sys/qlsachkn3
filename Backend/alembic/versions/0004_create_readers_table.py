"""create readers table

Revision ID: 0004
Revises: 0003
Create Date: 2026-08-09

"""
import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "Readers",
        sa.Column("ma", sa.Unicode(length=20), nullable=False),
        sa.Column("hoTen", sa.Unicode(length=255), nullable=False),
        sa.Column("email", sa.Unicode(length=255), nullable=False),
        sa.Column("soDienThoai", sa.Unicode(length=20), nullable=False),
        sa.Column("loaiDocGia", sa.Unicode(length=50), nullable=False),
        sa.Column("trangThaiThe", sa.Unicode(length=20), nullable=False),
        sa.Column("ngayTao", sa.DateTime(), nullable=False),
        sa.CheckConstraint("LEN(LTRIM(ma)) > 0", name="ck_readers_ma_not_empty"),
        sa.CheckConstraint("LEN(LTRIM(hoTen)) > 0", name="ck_readers_ho_ten_not_empty"),
        sa.CheckConstraint("LEN(LTRIM(email)) > 0", name="ck_readers_email_not_empty"),
        sa.CheckConstraint("LEN(LTRIM(soDienThoai)) > 0", name="ck_readers_phone_not_empty"),
        sa.CheckConstraint(
            "loaiDocGia IN ('sinh_vien', 'giang_vien', 'khac')",
            name="ck_readers_loai",
        ),
        sa.CheckConstraint(
            "trangThaiThe IN ('hoat_dong', 'khoa')",
            name="ck_readers_trang_thai",
        ),
        sa.PrimaryKeyConstraint("ma", name="pk_readers"),
    )


def downgrade() -> None:
    op.drop_table("Readers")
