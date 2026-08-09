"""add so ngay muon to yeu cau

Revision ID: 0013
Revises: 0012
Create Date: 2026-08-10

"""
import sqlalchemy as sa
from alembic import op

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("YeuCau", sa.Column("so_ngay_muon", sa.Integer(), nullable=True))
    op.execute(
        "ALTER TABLE [YeuCau] ADD CONSTRAINT [ck_yeu_cau_so_ngay_muon] "
        "CHECK (so_ngay_muon IS NULL OR so_ngay_muon >= 1)"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE [YeuCau] DROP CONSTRAINT [ck_yeu_cau_so_ngay_muon]")
    op.drop_column("YeuCau", "so_ngay_muon")
