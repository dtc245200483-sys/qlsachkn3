"""extend yeu cau loai with dat truoc

Revision ID: 0012
Revises: 0011
Create Date: 2026-08-10

"""
from alembic import op

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE [YeuCau] DROP CONSTRAINT [ck_yeu_cau_loai]")
    op.execute(
        "ALTER TABLE [YeuCau] ADD CONSTRAINT [ck_yeu_cau_loai] "
        "CHECK (loai IN ('MUON', 'TRA', 'GIA_HAN', 'DAT_TRUOC'))"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE [YeuCau] DROP CONSTRAINT [ck_yeu_cau_loai]")
    op.execute(
        "ALTER TABLE [YeuCau] ADD CONSTRAINT [ck_yeu_cau_loai] "
        "CHECK (loai IN ('MUON', 'TRA', 'GIA_HAN'))"
    )
