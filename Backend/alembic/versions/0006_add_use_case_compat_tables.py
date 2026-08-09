"""add use case compat tables and link columns

Revision ID: 0006
Revises: 0005
Create Date: 2026-08-09

"""
import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "TheLoai",
        sa.Column("ma", sa.Unicode(length=20), nullable=False),
        sa.Column("ten", sa.Unicode(length=100), nullable=False),
        sa.CheckConstraint("LEN(LTRIM(ma)) > 0", name="ck_the_loai_ma_not_empty"),
        sa.CheckConstraint("LEN(LTRIM(ten)) > 0", name="ck_the_loai_ten_not_empty"),
        sa.PrimaryKeyConstraint("ma", name="pk_the_loai"),
    )
    op.create_table(
        "Nxb",
        sa.Column("ma", sa.Unicode(length=20), nullable=False),
        sa.Column("ten", sa.Unicode(length=255), nullable=False),
        sa.CheckConstraint("LEN(LTRIM(ma)) > 0", name="ck_nxb_ma_not_empty"),
        sa.CheckConstraint("LEN(LTRIM(ten)) > 0", name="ck_nxb_ten_not_empty"),
        sa.PrimaryKeyConstraint("ma", name="pk_nxb"),
    )

    the_loai = sa.table(
        "TheLoai",
        sa.column("ma", sa.Unicode(length=20)),
        sa.column("ten", sa.Unicode(length=100)),
    )
    op.bulk_insert(
        the_loai,
        [
            {"ma": "TL_CN", "ten": "Công nghệ"},
            {"ma": "TL_VH", "ten": "Văn học"},
            {"ma": "TL_LS", "ten": "Lịch sử"},
            {"ma": "TL_GD", "ten": "Giáo dục"},
            {"ma": "TL_KH", "ten": "Khoa học"},
        ],
    )
    nxb = sa.table(
        "Nxb",
        sa.column("ma", sa.Unicode(length=20)),
        sa.column("ten", sa.Unicode(length=255)),
    )
    op.bulk_insert(
        nxb,
        [
            {"ma": "NXB_GD", "ten": "NXB Giáo dục"},
            {"ma": "NXB_VH", "ten": "NXB Văn học"},
            {"ma": "NXB_KHKT", "ten": "NXB Khoa học và Kỹ thuật"},
            {"ma": "NXB_TRE", "ten": "NXB Trẻ"},
        ],
    )

    op.add_column("Books", sa.Column("theLoaiId", sa.Unicode(length=20), nullable=True))
    op.add_column("Books", sa.Column("nxbId", sa.Unicode(length=20), nullable=True))
    op.create_foreign_key("fk_books_the_loai", "Books", "TheLoai", ["theLoaiId"], ["ma"])
    op.create_foreign_key("fk_books_nxb", "Books", "Nxb", ["nxbId"], ["ma"])
    op.execute(
        "UPDATE Books SET theLoaiId = (SELECT ma FROM TheLoai WHERE ten = Books.theLoai) WHERE theLoaiId IS NULL"
    )
    op.execute(
        "UPDATE Books SET nxbId = (SELECT ma FROM Nxb WHERE ten = Books.nxb) WHERE nxbId IS NULL"
    )

    op.add_column("Users", sa.Column("reader_id", sa.Unicode(length=20), nullable=True))
    op.create_foreign_key("fk_users_reader", "Users", "Readers", ["reader_id"], ["ma"])
    op.create_unique_constraint("uq_readers_email", "Readers", ["email"])

    op.create_table(
        "YeuCau",
        sa.Column("ma_yeu_cau", sa.Unicode(length=20), nullable=False),
        sa.Column("loai", sa.Unicode(length=20), nullable=False),
        sa.Column("ma_doc_gia", sa.Unicode(length=20), nullable=False),
        sa.Column("ma_phieu", sa.Unicode(length=20), nullable=True),
        sa.Column("items", sa.UnicodeText(), nullable=False),
        sa.Column("trang_thai", sa.Unicode(length=20), nullable=False),
        sa.Column("ngay_tao", sa.DateTime(), nullable=False),
        sa.CheckConstraint("loai IN ('MUON', 'TRA', 'GIA_HAN')", name="ck_yeu_cau_loai"),
        sa.CheckConstraint(
            "trang_thai IN ('CHO_XU_LY', 'DA_DUYET', 'TU_CHOI')",
            name="ck_yeu_cau_trang_thai",
        ),
        sa.PrimaryKeyConstraint("ma_yeu_cau", name="pk_yeu_cau"),
    )
    op.create_index("ix_yeu_cau_ma_doc_gia", "YeuCau", ["ma_doc_gia"])


def downgrade() -> None:
    op.drop_index("ix_yeu_cau_ma_doc_gia", table_name="YeuCau")
    op.drop_table("YeuCau")
    op.drop_constraint("uq_readers_email", "Readers", type_="unique")
    op.drop_constraint("fk_users_reader", "Users", type_="foreignkey")
    op.drop_column("Users", "reader_id")
    op.drop_constraint("fk_books_the_loai", "Books", type_="foreignkey")
    op.drop_constraint("fk_books_nxb", "Books", type_="foreignkey")
    op.drop_column("Books", "nxbId")
    op.drop_column("Books", "theLoaiId")
    op.drop_table("Nxb")
    op.drop_table("TheLoai")
