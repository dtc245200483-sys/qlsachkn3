"""add user email and phone columns

Revision ID: 0010
Revises: 0009
Create Date: 2026-08-10

"""
import sqlalchemy as sa
from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("Users", sa.Column("email", sa.Unicode(length=255), nullable=True))
    op.add_column("Users", sa.Column("so_dien_thoai", sa.Unicode(length=20), nullable=True))
    op.create_index(
        "uq_users_email",
        "Users",
        ["email"],
        unique=True,
        mssql_where=sa.text("email IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_users_email", table_name="Users")
    op.drop_column("Users", "so_dien_thoai")
    op.drop_column("Users", "email")
