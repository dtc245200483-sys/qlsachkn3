"""add fine collection columns

Revision ID: 0008
Revises: 0007
Create Date: 2026-08-09

"""
import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "FineHistory",
        sa.Column("da_thu", sa.Boolean(), nullable=False, server_default=sa.text("0")),
    )
    op.add_column("FineHistory", sa.Column("ngay_thu", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.execute(
        """
        DECLARE @constraint_name sysname = (
            SELECT dc.name
            FROM sys.default_constraints dc
            JOIN sys.columns c
              ON dc.parent_object_id = c.object_id
             AND dc.parent_column_id = c.column_id
            WHERE dc.parent_object_id = OBJECT_ID('FineHistory')
              AND c.name = 'da_thu'
        );
        IF @constraint_name IS NOT NULL
            EXEC('ALTER TABLE [FineHistory] DROP CONSTRAINT [' + @constraint_name + ']');
        """
    )
    op.drop_column("FineHistory", "ngay_thu")
    op.drop_column("FineHistory", "da_thu")
