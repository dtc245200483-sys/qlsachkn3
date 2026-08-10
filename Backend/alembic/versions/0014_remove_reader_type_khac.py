"""remove reader type khac

Revision ID: 0014
Revises: 0013
Create Date: 2026-08-10

"""
from alembic import op

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE [Readers] DROP CONSTRAINT [ck_readers_loai]")
    op.execute("UPDATE Readers SET loaiDocGia = 'sinh_vien' WHERE loaiDocGia = 'khac'")
    op.execute(
        "ALTER TABLE [Readers] ADD CONSTRAINT [ck_readers_loai] "
        "CHECK (loaiDocGia IN ('sinh_vien', 'giang_vien'))"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE [Readers] DROP CONSTRAINT [ck_readers_loai]")
    op.execute(
        "ALTER TABLE [Readers] ADD CONSTRAINT [ck_readers_loai] "
        "CHECK (loaiDocGia IN ('sinh_vien', 'giang_vien', 'khac'))"
    )
