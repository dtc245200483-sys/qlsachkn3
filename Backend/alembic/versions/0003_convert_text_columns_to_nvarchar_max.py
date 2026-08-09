"""convert text columns to nvarchar(max)

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-09

"""
import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "AIConfig",
        "prompt_template",
        existing_type=sa.Text(),
        type_=sa.UnicodeText(),
        existing_nullable=False,
    )
    op.alter_column(
        "AuditLog",
        "details",
        existing_type=sa.Text(),
        type_=sa.UnicodeText(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "AuditLog",
        "details",
        existing_type=sa.UnicodeText(),
        type_=sa.Text(),
        existing_nullable=True,
    )
    op.alter_column(
        "AIConfig",
        "prompt_template",
        existing_type=sa.UnicodeText(),
        type_=sa.Text(),
        existing_nullable=False,
    )
