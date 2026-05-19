"""add extended business workflows

Revision ID: 20260519_0010
Revises: 20260519_0009
Create Date: 2026-05-19 01:10:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260519_0010"
down_revision = "20260519_0009"
branch_labels = None
depends_on = None


package_status_enum = sa.Enum("DRAFT", "PACKED", "SHIPPED", "DELIVERED", "CANCELLED", name="package_status_enum")
invoice_status_enum = sa.Enum("DRAFT", "SENT", "PAID", "VOID", name="invoice_status_enum")
sales_return_status_enum = sa.Enum("DRAFT", "RECEIVED", "REFUNDED", "CANCELLED", name="sales_return_status_enum")
purchase_receive_status_enum = sa.Enum("POSTED", "CANCELLED", name="purchase_receive_status_enum")
bill_status_enum = sa.Enum("DRAFT", "POSTED", "PAID", "VOID", name="bill_status_enum")


def upgrade() -> None:
    op.create_table(
        "packages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("sales_order_id", sa.Integer(), nullable=False),
        sa.Column("package_number", sa.String(length=100), nullable=False),
        sa.Column("status", package_status_enum, nullable=False, server_default="DRAFT"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["sales_order_id"], ["sales_orders.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.UniqueConstraint("tenant_id", "package_number", name="uq_packages_tenant_number"),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_packages_id", "packages", ["id"])
    op.create_index("ix_packages_package_number", "packages", ["package_number"])
    op.create_index("ix_packages_status", "packages", ["status"])
    op.create_index("ix_packages_sales_order_id", "packages", ["sales_order_id"])
    op.create_index("ix_packages_created_by", "packages", ["created_by"])
    op.create_index("ix_packages_tenant_status", "packages", ["tenant_id", "status"])
    op.create_index("ix_packages_tenant_sales_order", "packages", ["tenant_id", "sales_order_id"])

    op.create_table(
        "package_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("package_id", sa.Integer(), nullable=False),
        sa.Column("sales_order_item_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("warehouse_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["package_id"], ["packages.id"]),
        sa.ForeignKeyConstraint(["sales_order_item_id"], ["sales_order_items.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"]),
        sa.UniqueConstraint("package_id", "sales_order_item_id", name="uq_package_items_line"),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_package_items_id", "package_items", ["id"])
    op.create_index("ix_package_items_package_id", "package_items", ["package_id"])
    op.create_index("ix_package_items_sales_order_item_id", "package_items", ["sales_order_item_id"])
    op.create_index("ix_package_items_product_id", "package_items", ["product_id"])
    op.create_index("ix_package_items_warehouse_id", "package_items", ["warehouse_id"])

    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("sales_order_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("invoice_number", sa.String(length=100), nullable=False),
        sa.Column("invoice_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("status", invoice_status_enum, nullable=False, server_default="DRAFT"),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("tax_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("discount_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["sales_order_id"], ["sales_orders.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.UniqueConstraint("tenant_id", "invoice_number", name="uq_invoices_tenant_number"),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_invoices_id", "invoices", ["id"])
    op.create_index("ix_invoices_invoice_number", "invoices", ["invoice_number"])
    op.create_index("ix_invoices_invoice_date", "invoices", ["invoice_date"])
    op.create_index("ix_invoices_status", "invoices", ["status"])
    op.create_index("ix_invoices_sales_order_id", "invoices", ["sales_order_id"])
    op.create_index("ix_invoices_customer_id", "invoices", ["customer_id"])
    op.create_index("ix_invoices_created_by", "invoices", ["created_by"])
    op.create_index("ix_invoices_tenant_status", "invoices", ["tenant_id", "status"])
    op.create_index("ix_invoices_tenant_sales_order", "invoices", ["tenant_id", "sales_order_id"])

    op.create_table(
        "sales_returns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("sales_order_id", sa.Integer(), nullable=False),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("return_number", sa.String(length=100), nullable=False),
        sa.Column("return_date", sa.Date(), nullable=False),
        sa.Column("status", sales_return_status_enum, nullable=False, server_default="DRAFT"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["sales_order_id"], ["sales_orders.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.UniqueConstraint("tenant_id", "return_number", name="uq_sales_returns_tenant_number"),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_sales_returns_id", "sales_returns", ["id"])
    op.create_index("ix_sales_returns_return_number", "sales_returns", ["return_number"])
    op.create_index("ix_sales_returns_return_date", "sales_returns", ["return_date"])
    op.create_index("ix_sales_returns_status", "sales_returns", ["status"])
    op.create_index("ix_sales_returns_sales_order_id", "sales_returns", ["sales_order_id"])
    op.create_index("ix_sales_returns_customer_id", "sales_returns", ["customer_id"])
    op.create_index("ix_sales_returns_created_by", "sales_returns", ["created_by"])
    op.create_index("ix_sales_returns_tenant_status", "sales_returns", ["tenant_id", "status"])
    op.create_index("ix_sales_returns_tenant_sales_order", "sales_returns", ["tenant_id", "sales_order_id"])

    op.create_table(
        "sales_return_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sales_return_id", sa.Integer(), nullable=False),
        sa.Column("sales_order_item_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("warehouse_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["sales_return_id"], ["sales_returns.id"]),
        sa.ForeignKeyConstraint(["sales_order_item_id"], ["sales_order_items.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"]),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_sales_return_items_id", "sales_return_items", ["id"])
    op.create_index("ix_sales_return_items_sales_return_id", "sales_return_items", ["sales_return_id"])
    op.create_index("ix_sales_return_items_sales_order_item_id", "sales_return_items", ["sales_order_item_id"])
    op.create_index("ix_sales_return_items_product_id", "sales_return_items", ["product_id"])
    op.create_index("ix_sales_return_items_warehouse_id", "sales_return_items", ["warehouse_id"])

    op.create_table(
        "purchase_receives",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("purchase_order_id", sa.Integer(), nullable=False),
        sa.Column("vendor_id", sa.Integer(), nullable=False),
        sa.Column("receive_number", sa.String(length=100), nullable=False),
        sa.Column("received_at", sa.Date(), nullable=False),
        sa.Column("status", purchase_receive_status_enum, nullable=False, server_default="POSTED"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["purchase_order_id"], ["purchase_orders.id"]),
        sa.ForeignKeyConstraint(["vendor_id"], ["vendors.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.UniqueConstraint("tenant_id", "receive_number", name="uq_purchase_receives_tenant_number"),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_purchase_receives_id", "purchase_receives", ["id"])
    op.create_index("ix_purchase_receives_receive_number", "purchase_receives", ["receive_number"])
    op.create_index("ix_purchase_receives_received_at", "purchase_receives", ["received_at"])
    op.create_index("ix_purchase_receives_status", "purchase_receives", ["status"])
    op.create_index("ix_purchase_receives_purchase_order_id", "purchase_receives", ["purchase_order_id"])
    op.create_index("ix_purchase_receives_vendor_id", "purchase_receives", ["vendor_id"])
    op.create_index("ix_purchase_receives_created_by", "purchase_receives", ["created_by"])
    op.create_index("ix_purchase_receives_tenant_status", "purchase_receives", ["tenant_id", "status"])
    op.create_index("ix_purchase_receives_tenant_purchase_order", "purchase_receives", ["tenant_id", "purchase_order_id"])

    op.create_table(
        "purchase_receive_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("purchase_receive_id", sa.Integer(), nullable=False),
        sa.Column("purchase_order_item_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("warehouse_id", sa.Integer(), nullable=False),
        sa.Column("quantity_received", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["purchase_receive_id"], ["purchase_receives.id"]),
        sa.ForeignKeyConstraint(["purchase_order_item_id"], ["purchase_order_items.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"]),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_purchase_receive_items_id", "purchase_receive_items", ["id"])
    op.create_index("ix_purchase_receive_items_purchase_receive_id", "purchase_receive_items", ["purchase_receive_id"])
    op.create_index("ix_purchase_receive_items_purchase_order_item_id", "purchase_receive_items", ["purchase_order_item_id"])
    op.create_index("ix_purchase_receive_items_product_id", "purchase_receive_items", ["product_id"])
    op.create_index("ix_purchase_receive_items_warehouse_id", "purchase_receive_items", ["warehouse_id"])

    op.create_table(
        "bills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("purchase_order_id", sa.Integer(), nullable=False),
        sa.Column("vendor_id", sa.Integer(), nullable=False),
        sa.Column("bill_number", sa.String(length=100), nullable=False),
        sa.Column("bill_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("status", bill_status_enum, nullable=False, server_default="DRAFT"),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("tax_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["purchase_order_id"], ["purchase_orders.id"]),
        sa.ForeignKeyConstraint(["vendor_id"], ["vendors.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.UniqueConstraint("tenant_id", "bill_number", name="uq_bills_tenant_number"),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_bills_id", "bills", ["id"])
    op.create_index("ix_bills_bill_number", "bills", ["bill_number"])
    op.create_index("ix_bills_bill_date", "bills", ["bill_date"])
    op.create_index("ix_bills_status", "bills", ["status"])
    op.create_index("ix_bills_purchase_order_id", "bills", ["purchase_order_id"])
    op.create_index("ix_bills_vendor_id", "bills", ["vendor_id"])
    op.create_index("ix_bills_created_by", "bills", ["created_by"])
    op.create_index("ix_bills_tenant_status", "bills", ["tenant_id", "status"])
    op.create_index("ix_bills_tenant_purchase_order", "bills", ["tenant_id", "purchase_order_id"])


def downgrade() -> None:
    op.drop_index("ix_bills_tenant_purchase_order", table_name="bills")
    op.drop_index("ix_bills_tenant_status", table_name="bills")
    op.drop_index("ix_bills_created_by", table_name="bills")
    op.drop_index("ix_bills_vendor_id", table_name="bills")
    op.drop_index("ix_bills_purchase_order_id", table_name="bills")
    op.drop_index("ix_bills_status", table_name="bills")
    op.drop_index("ix_bills_bill_date", table_name="bills")
    op.drop_index("ix_bills_bill_number", table_name="bills")
    op.drop_index("ix_bills_id", table_name="bills")
    op.drop_table("bills")

    op.drop_index("ix_purchase_receive_items_warehouse_id", table_name="purchase_receive_items")
    op.drop_index("ix_purchase_receive_items_product_id", table_name="purchase_receive_items")
    op.drop_index("ix_purchase_receive_items_purchase_order_item_id", table_name="purchase_receive_items")
    op.drop_index("ix_purchase_receive_items_purchase_receive_id", table_name="purchase_receive_items")
    op.drop_index("ix_purchase_receive_items_id", table_name="purchase_receive_items")
    op.drop_table("purchase_receive_items")

    op.drop_index("ix_purchase_receives_tenant_purchase_order", table_name="purchase_receives")
    op.drop_index("ix_purchase_receives_tenant_status", table_name="purchase_receives")
    op.drop_index("ix_purchase_receives_created_by", table_name="purchase_receives")
    op.drop_index("ix_purchase_receives_vendor_id", table_name="purchase_receives")
    op.drop_index("ix_purchase_receives_purchase_order_id", table_name="purchase_receives")
    op.drop_index("ix_purchase_receives_status", table_name="purchase_receives")
    op.drop_index("ix_purchase_receives_received_at", table_name="purchase_receives")
    op.drop_index("ix_purchase_receives_receive_number", table_name="purchase_receives")
    op.drop_index("ix_purchase_receives_id", table_name="purchase_receives")
    op.drop_table("purchase_receives")

    op.drop_index("ix_sales_return_items_warehouse_id", table_name="sales_return_items")
    op.drop_index("ix_sales_return_items_product_id", table_name="sales_return_items")
    op.drop_index("ix_sales_return_items_sales_order_item_id", table_name="sales_return_items")
    op.drop_index("ix_sales_return_items_sales_return_id", table_name="sales_return_items")
    op.drop_index("ix_sales_return_items_id", table_name="sales_return_items")
    op.drop_table("sales_return_items")

    op.drop_index("ix_sales_returns_tenant_sales_order", table_name="sales_returns")
    op.drop_index("ix_sales_returns_tenant_status", table_name="sales_returns")
    op.drop_index("ix_sales_returns_created_by", table_name="sales_returns")
    op.drop_index("ix_sales_returns_customer_id", table_name="sales_returns")
    op.drop_index("ix_sales_returns_sales_order_id", table_name="sales_returns")
    op.drop_index("ix_sales_returns_status", table_name="sales_returns")
    op.drop_index("ix_sales_returns_return_date", table_name="sales_returns")
    op.drop_index("ix_sales_returns_return_number", table_name="sales_returns")
    op.drop_index("ix_sales_returns_id", table_name="sales_returns")
    op.drop_table("sales_returns")

    op.drop_index("ix_invoices_tenant_sales_order", table_name="invoices")
    op.drop_index("ix_invoices_tenant_status", table_name="invoices")
    op.drop_index("ix_invoices_created_by", table_name="invoices")
    op.drop_index("ix_invoices_customer_id", table_name="invoices")
    op.drop_index("ix_invoices_sales_order_id", table_name="invoices")
    op.drop_index("ix_invoices_status", table_name="invoices")
    op.drop_index("ix_invoices_invoice_date", table_name="invoices")
    op.drop_index("ix_invoices_invoice_number", table_name="invoices")
    op.drop_index("ix_invoices_id", table_name="invoices")
    op.drop_table("invoices")

    op.drop_index("ix_package_items_warehouse_id", table_name="package_items")
    op.drop_index("ix_package_items_product_id", table_name="package_items")
    op.drop_index("ix_package_items_sales_order_item_id", table_name="package_items")
    op.drop_index("ix_package_items_package_id", table_name="package_items")
    op.drop_index("ix_package_items_id", table_name="package_items")
    op.drop_table("package_items")

    op.drop_index("ix_packages_tenant_sales_order", table_name="packages")
    op.drop_index("ix_packages_tenant_status", table_name="packages")
    op.drop_index("ix_packages_created_by", table_name="packages")
    op.drop_index("ix_packages_sales_order_id", table_name="packages")
    op.drop_index("ix_packages_status", table_name="packages")
    op.drop_index("ix_packages_package_number", table_name="packages")
    op.drop_index("ix_packages_id", table_name="packages")
    op.drop_table("packages")

    bill_status_enum.drop(op.get_bind(), checkfirst=False)
    purchase_receive_status_enum.drop(op.get_bind(), checkfirst=False)
    sales_return_status_enum.drop(op.get_bind(), checkfirst=False)
    invoice_status_enum.drop(op.get_bind(), checkfirst=False)
    package_status_enum.drop(op.get_bind(), checkfirst=False)
