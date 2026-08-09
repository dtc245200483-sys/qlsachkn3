"""add admin support tables and user lock flag

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-09

"""
import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "Users",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
    )

    op.create_table(
        "LibraryConfig",
        sa.Column("id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("max_borrow_days", sa.Integer(), nullable=False),
        sa.Column("overdue_fine_per_day", sa.Numeric(10, 2), nullable=False),
        sa.Column("max_books_at_once", sa.Integer(), nullable=False),
        sa.CheckConstraint("id = 1", name="ck_library_config_singleton"),
        sa.CheckConstraint("max_borrow_days > 0", name="ck_library_config_max_borrow_days"),
        sa.CheckConstraint("overdue_fine_per_day >= 0", name="ck_library_config_fine"),
        sa.CheckConstraint("max_books_at_once > 0", name="ck_library_config_max_books"),
        sa.PrimaryKeyConstraint("id", name="pk_library_config"),
    )
    op.create_table(
        "AIConfig",
        sa.Column("id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("provider", sa.Unicode(length=50), nullable=False),
        sa.Column("model", sa.Unicode(length=100), nullable=False),
        sa.Column("api_key", sa.Unicode(length=500), nullable=False),
        sa.Column("prompt_template", sa.Text(), nullable=False),
        sa.CheckConstraint("id = 1", name="ck_ai_config_singleton"),
        sa.PrimaryKeyConstraint("id", name="pk_ai_config"),
    )
    op.create_table(
        "AuditLog",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.Unicode(length=50), nullable=True),
        sa.Column("role", sa.Unicode(length=20), nullable=True),
        sa.Column("action", sa.Unicode(length=50), nullable=False),
        sa.Column("entity", sa.Unicode(length=50), nullable=False),
        sa.Column("entity_id", sa.Unicode(length=50), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_audit_log"),
    )
    op.create_index("ix_audit_log_created_at", "AuditLog", ["created_at"])

    library_config = sa.table(
        "LibraryConfig",
        sa.column("id", sa.Integer()),
        sa.column("max_borrow_days", sa.Integer()),
        sa.column("overdue_fine_per_day", sa.Numeric(10, 2)),
        sa.column("max_books_at_once", sa.Integer()),
    )
    op.bulk_insert(
        library_config,
        [
            {
                "id": 1,
                "max_borrow_days": 14,
                "overdue_fine_per_day": 5000.00,
                "max_books_at_once": 3,
            }
        ],
    )

    ai_config = sa.table(
        "AIConfig",
        sa.column("id", sa.Integer()),
        sa.column("provider", sa.Unicode(length=50)),
        sa.column("model", sa.Unicode(length=100)),
        sa.column("api_key", sa.Unicode(length=500)),
        sa.column("prompt_template", sa.Text()),
    )
    op.bulk_insert(
        ai_config,
        [
            {
                "id": 1,
                "provider": "openai",
                "model": "",
                "api_key": "",
                "prompt_template": "",
            }
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_audit_log_created_at", table_name="AuditLog")
    op.drop_table("AuditLog")
    op.drop_table("AIConfig")
    op.drop_table("LibraryConfig")
    op.execute(
        """
        DECLARE @constraint_name sysname = (
            SELECT dc.name
            FROM sys.default_constraints dc
            JOIN sys.columns c
              ON dc.parent_object_id = c.object_id
             AND dc.parent_column_id = c.column_id
            WHERE dc.parent_object_id = OBJECT_ID('Users')
              AND c.name = 'is_active'
        );
        IF @constraint_name IS NOT NULL
            EXEC('ALTER TABLE [Users] DROP CONSTRAINT [' + @constraint_name + ']');
        """
    )
    op.drop_column("Users", "is_active")
