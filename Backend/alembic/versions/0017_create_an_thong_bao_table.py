"""create an thong bao table

Revision ID: 0017
Revises: 0016
Create Date: 2026-08-10

"""
import sqlalchemy as sa
from alembic import op

revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "AnThongBao",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ma_doc_gia", sa.Unicode(length=20), nullable=False),
        sa.Column("nguon_id", sa.Unicode(length=100), nullable=False),
        sa.Column("ngay_an", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_an_thong_bao"),
        sa.UniqueConstraint("ma_doc_gia", "nguon_id", name="uq_an_thong_bao_nguon"),
    )


def downgrade() -> None:
    op.drop_table("AnThongBao")
