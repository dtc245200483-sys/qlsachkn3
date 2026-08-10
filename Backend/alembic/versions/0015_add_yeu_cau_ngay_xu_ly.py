"""add yeu cau ngay xu ly

Revision ID: 0015
Revises: 0014
Create Date: 2026-08-10

"""
import sqlalchemy as sa
from alembic import op

revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("YeuCau", sa.Column("ngay_xu_ly", sa.DateTime(), nullable=True))
    op.execute(
        "UPDATE YeuCau SET ngay_xu_ly = ngay_tao "
        "WHERE trang_thai IN ('DA_DUYET', 'TU_CHOI') AND ngay_xu_ly IS NULL"
    )


def downgrade() -> None:
    op.drop_column("YeuCau", "ngay_xu_ly")
