"""rename monetary fines to points

Revision ID: 0011
Revises: 0010
Create Date: 2026-08-10

"""
import sqlalchemy as sa
from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE [LibraryConfig] DROP CONSTRAINT [ck_library_config_fine]")
    op.execute(
        "EXEC sp_rename 'LibraryConfig.overdue_fine_per_day', "
        "'overdue_fine_points_per_day', 'COLUMN'"
    )
    op.alter_column(
        "LibraryConfig",
        "overdue_fine_points_per_day",
        existing_type=sa.Numeric(10, 2),
        type_=sa.Integer(),
        existing_nullable=False,
    )
    op.execute("UPDATE LibraryConfig SET overdue_fine_points_per_day = 2")
    op.execute(
        "ALTER TABLE [LibraryConfig] ADD CONSTRAINT [ck_library_config_points] "
        "CHECK (overdue_fine_points_per_day >= 0)"
    )

    op.execute("ALTER TABLE [FineHistory] DROP CONSTRAINT [ck_fine_history_amount]")
    op.execute("EXEC sp_rename 'FineHistory.so_tien', 'so_diem', 'COLUMN'")
    op.alter_column(
        "FineHistory",
        "so_diem",
        existing_type=sa.Numeric(12, 2),
        type_=sa.Integer(),
        existing_nullable=False,
    )
    op.execute("UPDATE FineHistory SET so_diem = so_ngay_qua_han * 2")
    op.execute(
        "ALTER TABLE [FineHistory] ADD CONSTRAINT [ck_fine_history_points] "
        "CHECK (so_diem >= 0)"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE [FineHistory] DROP CONSTRAINT [ck_fine_history_points]"
    )
    op.alter_column(
        "FineHistory",
        "so_diem",
        existing_type=sa.Integer(),
        type_=sa.Numeric(12, 2),
        existing_nullable=False,
    )
    op.execute("UPDATE FineHistory SET so_diem = so_ngay_qua_han * 5000")
    op.execute("EXEC sp_rename 'FineHistory.so_diem', 'so_tien', 'COLUMN'")
    op.execute(
        "ALTER TABLE [FineHistory] ADD CONSTRAINT [ck_fine_history_amount] "
        "CHECK (so_tien >= 0)"
    )

    op.execute(
        "ALTER TABLE [LibraryConfig] DROP CONSTRAINT [ck_library_config_points]"
    )
    op.execute("UPDATE LibraryConfig SET overdue_fine_points_per_day = 5000")
    op.alter_column(
        "LibraryConfig",
        "overdue_fine_points_per_day",
        existing_type=sa.Integer(),
        type_=sa.Numeric(10, 2),
        existing_nullable=False,
    )
    op.execute(
        "EXEC sp_rename 'LibraryConfig.overdue_fine_points_per_day', "
        "'overdue_fine_per_day', 'COLUMN'"
    )
    op.execute(
        "ALTER TABLE [LibraryConfig] ADD CONSTRAINT [ck_library_config_fine] "
        "CHECK (overdue_fine_per_day >= 0)"
    )
