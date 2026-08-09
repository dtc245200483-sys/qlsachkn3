"""create users and books tables

Revision ID: 0001
Revises:
Create Date: 2026-08-09

"""
import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "Users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.Unicode(length=50), nullable=False),
        sa.Column("password_hash", sa.Unicode(length=255), nullable=False),
        sa.Column("ho_ten", sa.Unicode(length=255), nullable=False),
        sa.Column("role", sa.Unicode(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("role IN ('admin', 'librarian', 'reader')", name="ck_users_role"),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("username", name="uq_users_username"),
    )
    op.create_table(
        "Books",
        sa.Column("ma", sa.Unicode(length=20), nullable=False),
        sa.Column("ten", sa.Unicode(length=255), nullable=False),
        sa.Column("tacGia", sa.Unicode(length=255), nullable=False),
        sa.Column("theLoai", sa.Unicode(length=100), nullable=False),
        sa.Column("nxb", sa.Unicode(length=255), nullable=False),
        sa.Column("namXb", sa.Integer(), nullable=False),
        sa.Column("soLuong", sa.Integer(), nullable=False),
        sa.CheckConstraint("soLuong >= 0", name="ck_books_soluong"),
        sa.PrimaryKeyConstraint("ma", name="pk_books"),
    )


def downgrade() -> None:
    op.drop_table("Books")
    op.drop_table("Users")
