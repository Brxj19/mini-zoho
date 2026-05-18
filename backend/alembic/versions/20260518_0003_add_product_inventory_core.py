"""add product inventory core

Revision ID: 20260518_0003
Revises: 20260518_0002
Create Date: 2026-05-18 00:03:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260518_0003"
down_revision = "20260518_0002"
branch_labels = None
depends_on = None


inventory_transaction_type_enum = sa.Enum(
    "STOCK_IN",
    "STOCK_OUT",
    "ADJUSTMENT",
    "TRANSFER_IN",
    "TRANSFER_OUT",
    "SALES_ORDER_RESERVE",
    "SALES_ORDER_DEDUCT",
    "SALES_ORDER_CANCEL_RELEASE",
    "PURCHASE_RECEIVE",
    "RETURN_IN",
    "DAMAGE_OUT",
    name="inventory_transaction_type_enum",
)


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("sku", sa.String(length=100), nullable=False),
        sa.Column("barcode", sa.String(length=100), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("brand_id", sa.Integer(), nullable=True),
        sa.Column("vendor_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("unit", sa.String(length=64), nullable=False, server_default="unit"),
        sa.Column("cost_price", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("selling_price", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("reorder_level", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.Enum("ACTIVE", "ARCHIVED", name="record_status_enum"), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["brand_id"], ["brands.id"]),
        sa.ForeignKeyConstraint(["vendor_id"], ["vendors.id"]),
        sa.UniqueConstraint("tenant_id", "sku", name="uq_products_tenant_sku"),
        sa.UniqueConstraint("tenant_id", "barcode", name="uq_products_tenant_barcode"),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_products_id", "products", ["id"])
    op.create_index("ix_products_name", "products", ["name"])
    op.create_index("ix_products_sku", "products", ["sku"])
    op.create_index("ix_products_barcode", "products", ["barcode"])
    op.create_index("ix_products_category_id", "products", ["category_id"])
    op.create_index("ix_products_brand_id", "products", ["brand_id"])
    op.create_index("ix_products_vendor_id", "products", ["vendor_id"])
    op.create_index("ix_products_status", "products", ["status"])
    op.create_index("ix_products_tenant_id", "products", ["tenant_id"])
    op.create_index("ix_products_tenant_status", "products", ["tenant_id", "status"])
    op.create_index("ix_products_tenant_category", "products", ["tenant_id", "category_id"])
    op.create_index("ix_products_tenant_brand", "products", ["tenant_id", "brand_id"])
    op.create_index("ix_products_tenant_vendor", "products", ["tenant_id", "vendor_id"])

    op.create_table(
        "warehouse_stock",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("warehouse_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reserved_quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("available_quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reorder_level", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.UniqueConstraint("tenant_id", "warehouse_id", "product_id", name="uq_warehouse_stock_tenant_wh_product"),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_warehouse_stock_id", "warehouse_stock", ["id"])
    op.create_index("ix_warehouse_stock_tenant_id", "warehouse_stock", ["tenant_id"])
    op.create_index("ix_warehouse_stock_warehouse_id", "warehouse_stock", ["warehouse_id"])
    op.create_index("ix_warehouse_stock_product_id", "warehouse_stock", ["product_id"])
    op.create_index("ix_warehouse_stock_tenant_product", "warehouse_stock", ["tenant_id", "product_id"])
    op.create_index("ix_warehouse_stock_tenant_warehouse", "warehouse_stock", ["tenant_id", "warehouse_id"])

    op.create_table(
        "inventory_transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("warehouse_id", sa.Integer(), nullable=False),
        sa.Column("source_warehouse_id", sa.Integer(), nullable=True),
        sa.Column("destination_warehouse_id", sa.Integer(), nullable=True),
        sa.Column("transaction_type", inventory_transaction_type_enum, nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("reference_type", sa.String(length=100), nullable=True),
        sa.Column("reference_id", sa.Integer(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"]),
        sa.ForeignKeyConstraint(["source_warehouse_id"], ["warehouses.id"]),
        sa.ForeignKeyConstraint(["destination_warehouse_id"], ["warehouses.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_inventory_transactions_id", "inventory_transactions", ["id"])
    op.create_index("ix_inventory_transactions_product_id", "inventory_transactions", ["product_id"])
    op.create_index("ix_inventory_transactions_warehouse_id", "inventory_transactions", ["warehouse_id"])
    op.create_index("ix_inventory_transactions_transaction_type", "inventory_transactions", ["transaction_type"])
    op.create_index("ix_inventory_transactions_created_by", "inventory_transactions", ["created_by"])
    op.create_index("ix_inventory_tx_tenant_product", "inventory_transactions", ["tenant_id", "product_id"])
    op.create_index("ix_inventory_tx_tenant_warehouse", "inventory_transactions", ["tenant_id", "warehouse_id"])
    op.create_index("ix_inventory_tx_tenant_type", "inventory_transactions", ["tenant_id", "transaction_type"])
    op.create_index("ix_inventory_tx_tenant_created_by", "inventory_transactions", ["tenant_id", "created_by"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("old_value_json", sa.JSON(), nullable=True),
        sa.Column("new_value_json", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_audit_logs_id", "audit_logs", ["id"])
    op.create_index("ix_audit_logs_tenant_id", "audit_logs", ["tenant_id"])
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_entity_type", "audit_logs", ["entity_type"])
    op.create_index("ix_audit_logs_entity_id", "audit_logs", ["entity_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_logs_entity_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_entity_type", table_name="audit_logs")
    op.drop_index("ix_audit_logs_action", table_name="audit_logs")
    op.drop_index("ix_audit_logs_user_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_tenant_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_id", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index("ix_inventory_tx_tenant_created_by", table_name="inventory_transactions")
    op.drop_index("ix_inventory_tx_tenant_type", table_name="inventory_transactions")
    op.drop_index("ix_inventory_tx_tenant_warehouse", table_name="inventory_transactions")
    op.drop_index("ix_inventory_tx_tenant_product", table_name="inventory_transactions")
    op.drop_index("ix_inventory_transactions_created_by", table_name="inventory_transactions")
    op.drop_index("ix_inventory_transactions_transaction_type", table_name="inventory_transactions")
    op.drop_index("ix_inventory_transactions_warehouse_id", table_name="inventory_transactions")
    op.drop_index("ix_inventory_transactions_product_id", table_name="inventory_transactions")
    op.drop_index("ix_inventory_transactions_id", table_name="inventory_transactions")
    op.drop_table("inventory_transactions")

    op.drop_index("ix_warehouse_stock_tenant_warehouse", table_name="warehouse_stock")
    op.drop_index("ix_warehouse_stock_tenant_product", table_name="warehouse_stock")
    op.drop_index("ix_warehouse_stock_product_id", table_name="warehouse_stock")
    op.drop_index("ix_warehouse_stock_warehouse_id", table_name="warehouse_stock")
    op.drop_index("ix_warehouse_stock_tenant_id", table_name="warehouse_stock")
    op.drop_index("ix_warehouse_stock_id", table_name="warehouse_stock")
    op.drop_table("warehouse_stock")

    op.drop_index("ix_products_tenant_vendor", table_name="products")
    op.drop_index("ix_products_tenant_brand", table_name="products")
    op.drop_index("ix_products_tenant_category", table_name="products")
    op.drop_index("ix_products_tenant_status", table_name="products")
    op.drop_index("ix_products_tenant_id", table_name="products")
    op.drop_index("ix_products_status", table_name="products")
    op.drop_index("ix_products_vendor_id", table_name="products")
    op.drop_index("ix_products_brand_id", table_name="products")
    op.drop_index("ix_products_category_id", table_name="products")
    op.drop_index("ix_products_barcode", table_name="products")
    op.drop_index("ix_products_sku", table_name="products")
    op.drop_index("ix_products_name", table_name="products")
    op.drop_index("ix_products_id", table_name="products")
    op.drop_table("products")

    inventory_transaction_type_enum.drop(op.get_bind(), checkfirst=False)
