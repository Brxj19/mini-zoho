"""add stock transfers

Revision ID: 20260518_0004
Revises: 20260518_0003
Create Date: 2026-05-18 00:04:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260518_0004"
down_revision = "20260518_0003"
branch_labels = None
depends_on = None


stock_transfer_status_enum = sa.Enum(
    "DRAFT",
    "IN_TRANSIT",
    "COMPLETED",
    "CANCELLED",
    name="stock_transfer_status_enum",
)


def upgrade() -> None:
    op.create_table(
        "stock_transfers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("source_warehouse_id", sa.Integer(), nullable=False),
        sa.Column("destination_warehouse_id", sa.Integer(), nullable=False),
        sa.Column("status", stock_transfer_status_enum, nullable=False, server_default="DRAFT"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["source_warehouse_id"], ["warehouses.id"]),
        sa.ForeignKeyConstraint(["destination_warehouse_id"], ["warehouses.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_stock_transfers_id", "stock_transfers", ["id"])
    op.create_index("ix_stock_transfers_status", "stock_transfers", ["status"])
    op.create_index("ix_stock_transfers_created_by", "stock_transfers", ["created_by"])
    op.create_index("ix_stock_transfers_source_warehouse_id", "stock_transfers", ["source_warehouse_id"])
    op.create_index("ix_stock_transfers_destination_warehouse_id", "stock_transfers", ["destination_warehouse_id"])
    op.create_index("ix_stock_transfers_tenant_id", "stock_transfers", ["tenant_id"])
    op.create_index("ix_stock_transfers_tenant_status", "stock_transfers", ["tenant_id", "status"])
    op.create_index("ix_stock_transfers_tenant_source", "stock_transfers", ["tenant_id", "source_warehouse_id"])
    op.create_index("ix_stock_transfers_tenant_destination", "stock_transfers", ["tenant_id", "destination_warehouse_id"])

    op.create_table(
        "stock_transfer_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("stock_transfer_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["stock_transfer_id"], ["stock_transfers.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.UniqueConstraint("stock_transfer_id", "product_id", name="uq_stock_transfer_items_transfer_product"),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_stock_transfer_items_id", "stock_transfer_items", ["id"])
    op.create_index("ix_stock_transfer_items_stock_transfer_id", "stock_transfer_items", ["stock_transfer_id"])
    op.create_index("ix_stock_transfer_items_product_id", "stock_transfer_items", ["product_id"])
    op.create_index("ix_stock_transfer_items_transfer_product", "stock_transfer_items", ["stock_transfer_id", "product_id"])


def downgrade() -> None:
    op.drop_index("ix_stock_transfer_items_transfer_product", table_name="stock_transfer_items")
    op.drop_index("ix_stock_transfer_items_product_id", table_name="stock_transfer_items")
    op.drop_index("ix_stock_transfer_items_stock_transfer_id", table_name="stock_transfer_items")
    op.drop_index("ix_stock_transfer_items_id", table_name="stock_transfer_items")
    op.drop_table("stock_transfer_items")

    op.drop_index("ix_stock_transfers_tenant_destination", table_name="stock_transfers")
    op.drop_index("ix_stock_transfers_tenant_source", table_name="stock_transfers")
    op.drop_index("ix_stock_transfers_tenant_status", table_name="stock_transfers")
    op.drop_index("ix_stock_transfers_tenant_id", table_name="stock_transfers")
    op.drop_index("ix_stock_transfers_destination_warehouse_id", table_name="stock_transfers")
    op.drop_index("ix_stock_transfers_source_warehouse_id", table_name="stock_transfers")
    op.drop_index("ix_stock_transfers_created_by", table_name="stock_transfers")
    op.drop_index("ix_stock_transfers_status", table_name="stock_transfers")
    op.drop_index("ix_stock_transfers_id", table_name="stock_transfers")
    op.drop_table("stock_transfers")

    stock_transfer_status_enum.drop(op.get_bind(), checkfirst=False)
