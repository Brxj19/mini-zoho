"""add purchase orders

Revision ID: 20260518_0005
Revises: 20260518_0004
Create Date: 2026-05-18 00:05:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260518_0005"
down_revision = "20260518_0004"
branch_labels = None
depends_on = None


purchase_order_status_enum = sa.Enum(
    "DRAFT",
    "ISSUED",
    "PARTIALLY_RECEIVED",
    "RECEIVED",
    "CANCELLED",
    name="purchase_order_status_enum",
)


def upgrade() -> None:
    op.create_table(
        "purchase_orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("vendor_id", sa.Integer(), nullable=False),
        sa.Column("po_number", sa.String(length=100), nullable=False),
        sa.Column("order_date", sa.Date(), nullable=False),
        sa.Column("expected_delivery_date", sa.Date(), nullable=True),
        sa.Column("status", purchase_order_status_enum, nullable=False, server_default="DRAFT"),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("tax_amount", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["vendor_id"], ["vendors.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.UniqueConstraint("tenant_id", "po_number", name="uq_purchase_orders_tenant_number"),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_purchase_orders_id", "purchase_orders", ["id"])
    op.create_index("ix_purchase_orders_tenant_id", "purchase_orders", ["tenant_id"])
    op.create_index("ix_purchase_orders_vendor_id", "purchase_orders", ["vendor_id"])
    op.create_index("ix_purchase_orders_po_number", "purchase_orders", ["po_number"])
    op.create_index("ix_purchase_orders_order_date", "purchase_orders", ["order_date"])
    op.create_index("ix_purchase_orders_status", "purchase_orders", ["status"])
    op.create_index("ix_purchase_orders_created_by", "purchase_orders", ["created_by"])
    op.create_index("ix_purchase_orders_tenant_status", "purchase_orders", ["tenant_id", "status"])
    op.create_index("ix_purchase_orders_tenant_vendor", "purchase_orders", ["tenant_id", "vendor_id"])
    op.create_index("ix_purchase_orders_tenant_order_date", "purchase_orders", ["tenant_id", "order_date"])

    op.create_table(
        "purchase_order_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("purchase_order_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("warehouse_id", sa.Integer(), nullable=False),
        sa.Column("quantity_ordered", sa.Integer(), nullable=False),
        sa.Column("quantity_received", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("tax_rate", sa.Numeric(5, 2), nullable=False, server_default="0.00"),
        sa.Column("total_price", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.ForeignKeyConstraint(["purchase_order_id"], ["purchase_orders.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"]),
        sa.UniqueConstraint("purchase_order_id", "product_id", "warehouse_id", name="uq_purchase_order_items_po_product_wh"),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_purchase_order_items_id", "purchase_order_items", ["id"])
    op.create_index("ix_purchase_order_items_purchase_order_id", "purchase_order_items", ["purchase_order_id"])
    op.create_index("ix_purchase_order_items_product_id", "purchase_order_items", ["product_id"])
    op.create_index("ix_purchase_order_items_warehouse_id", "purchase_order_items", ["warehouse_id"])


def downgrade() -> None:
    op.drop_index("ix_purchase_order_items_warehouse_id", table_name="purchase_order_items")
    op.drop_index("ix_purchase_order_items_product_id", table_name="purchase_order_items")
    op.drop_index("ix_purchase_order_items_purchase_order_id", table_name="purchase_order_items")
    op.drop_index("ix_purchase_order_items_id", table_name="purchase_order_items")
    op.drop_table("purchase_order_items")

    op.drop_index("ix_purchase_orders_tenant_order_date", table_name="purchase_orders")
    op.drop_index("ix_purchase_orders_tenant_vendor", table_name="purchase_orders")
    op.drop_index("ix_purchase_orders_tenant_status", table_name="purchase_orders")
    op.drop_index("ix_purchase_orders_created_by", table_name="purchase_orders")
    op.drop_index("ix_purchase_orders_status", table_name="purchase_orders")
    op.drop_index("ix_purchase_orders_order_date", table_name="purchase_orders")
    op.drop_index("ix_purchase_orders_po_number", table_name="purchase_orders")
    op.drop_index("ix_purchase_orders_vendor_id", table_name="purchase_orders")
    op.drop_index("ix_purchase_orders_tenant_id", table_name="purchase_orders")
    op.drop_index("ix_purchase_orders_id", table_name="purchase_orders")
    op.drop_table("purchase_orders")

    purchase_order_status_enum.drop(op.get_bind(), checkfirst=False)
