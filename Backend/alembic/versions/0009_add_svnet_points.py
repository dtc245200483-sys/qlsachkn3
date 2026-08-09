"""add svnet points to readers

Revision ID: 0009
Revises: 0008
Create Date: 2026-08-09

"""
import sqlalchemy as sa
from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "Readers",
        sa.Column(
            "diem_svnet",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("100"),
        ),
    )


def downgrade() -> None:
    op.execute(
        """
        DECLARE @constraint_name sysname = (
            SELECT dc.name
            FROM sys.default_constraints dc
            JOIN sys.columns c
              ON dc.parent_object_id = c.object_id
             AND dc.parent_column_id = c.column_id
            WHERE dc.parent_object_id = OBJECT_ID('Readers')
              AND c.name = 'diem_svnet'
        );
        IF @constraint_name IS NOT NULL
            EXEC('ALTER TABLE [Readers] DROP CONSTRAINT [' + @constraint_name + ']');
        """
    )
    op.drop_column("Readers", "diem_svnet")
