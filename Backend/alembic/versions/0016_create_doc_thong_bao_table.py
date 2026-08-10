"""create doc thong bao table

Revision ID: 0016
Revises: 0015
Create Date: 2026-08-10

"""
import sqlalchemy as sa
from alembic import op

revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "DocThongBao",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ma_doc_gia", sa.Unicode(length=20), nullable=False),
        sa.Column("nguon_id", sa.Unicode(length=100), nullable=False),
        sa.Column("da_doc", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("ngay_doc", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_doc_thong_bao"),
        sa.UniqueConstraint("ma_doc_gia", "nguon_id", name="uq_doc_thong_bao_nguon"),
    )


def downgrade() -> None:
    op.drop_table("DocThongBao")
