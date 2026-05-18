"""add sales orders

Revision ID: 20260518_0006
Revises: 20260518_0005
Create Date: 2026-05-18 00:06:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260518_0006"
down_revision = "20260518_0005"
branch_labels = None
depends_on = None


sales_order_status_enum = sa.Enum(
    "DRAFT",
    "CONFIRMED",
    "PACKED",
    "SHIPPED",
    "DELIVERED",
    "CANCELLED",
    name="sales_order_status_enum",
)


def upgrade() -> None:
    op.create_table(
        "sales_orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("so_number", sa.String(length=100), nullable=False),
        sa.Column("order_date", sa.Date(), nullable=False),
        sa.Column("status", sales_order_status_enum, nullable=False, server_default="DRAFT"),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("tax_amount", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("discount_amount", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.UniqueConstraint("tenant_id", "so_number", name="uq_sales_orders_tenant_number"),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_sales_orders_id", "sales_orders", ["id"])
    op.create_index("ix_sales_orders_tenant_id", "sales_orders", ["tenant_id"])
    op.create_index("ix_sales_orders_customer_id", "sales_orders", ["customer_id"])
    op.create_index("ix_sales_orders_so_number", "sales_orders", ["so_number"])
    op.create_index("ix_sales_orders_order_date", "sales_orders", ["order_date"])
    op.create_index("ix_sales_orders_status", "sales_orders", ["status"])
    op.create_index("ix_sales_orders_created_by", "sales_orders", ["created_by"])
    op.create_index("ix_sales_orders_tenant_status", "sales_orders", ["tenant_id", "status"])
    op.create_index("ix_sales_orders_tenant_customer", "sales_orders", ["tenant_id", "customer_id"])
    op.create_index("ix_sales_orders_tenant_order_date", "sales_orders", ["tenant_id", "order_date"])

    op.create_table(
        "sales_order_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sales_order_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("warehouse_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("tax_rate", sa.Numeric(5, 2), nullable=False, server_default="0.00"),
        sa.Column("discount", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("total_price", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.ForeignKeyConstraint(["sales_order_id"], ["sales_orders.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"]),
        sa.UniqueConstraint("sales_order_id", "product_id", "warehouse_id", name="uq_sales_order_items_so_product_wh"),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_sales_order_items_id", "sales_order_items", ["id"])
    op.create_index("ix_sales_order_items_sales_order_id", "sales_order_items", ["sales_order_id"])
    op.create_index("ix_sales_order_items_product_id", "sales_order_items", ["product_id"])
    op.create_index("ix_sales_order_items_warehouse_id", "sales_order_items", ["warehouse_id"])


def downgrade() -> None:
    op.drop_index("ix_sales_order_items_warehouse_id", table_name="sales_order_items")
    op.drop_index("ix_sales_order_items_product_id", table_name="sales_order_items")
    op.drop_index("ix_sales_order_items_sales_order_id", table_name="sales_order_items")
    op.drop_index("ix_sales_order_items_id", table_name="sales_order_items")
    op.drop_table("sales_order_items")

    op.drop_index("ix_sales_orders_tenant_order_date", table_name="sales_orders")
    op.drop_index("ix_sales_orders_tenant_customer", table_name="sales_orders")
    op.drop_index("ix_sales_orders_tenant_status", table_name="sales_orders")
    op.drop_index("ix_sales_orders_created_by", table_name="sales_orders")
    op.drop_index("ix_sales_orders_status", table_name="sales_orders")
    op.drop_index("ix_sales_orders_order_date", table_name="sales_orders")
    op.drop_index("ix_sales_orders_so_number", table_name="sales_orders")
    op.drop_index("ix_sales_orders_customer_id", table_name="sales_orders")
    op.drop_index("ix_sales_orders_tenant_id", table_name="sales_orders")
    op.drop_index("ix_sales_orders_id", table_name="sales_orders")
    op.drop_table("sales_orders")

    sales_order_status_enum.drop(op.get_bind(), checkfirst=False)
