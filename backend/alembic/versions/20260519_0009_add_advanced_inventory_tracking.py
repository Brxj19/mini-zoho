"""add advanced inventory tracking

Revision ID: 20260519_0009
Revises: 20260519_0008
Create Date: 2026-05-19 00:09:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260519_0009"
down_revision = "20260519_0008"
branch_labels = None
depends_on = None


inventory_serial_status_enum = sa.Enum(
    "IN_STOCK",
    "ALLOCATED",
    "SOLD",
    "RETURNED",
    name="inventory_serial_status_enum",
)


def upgrade() -> None:
    op.add_column("products", sa.Column("serial_tracking_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("products", sa.Column("batch_tracking_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("products", sa.Column("expiry_tracking_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("products", sa.Column("warranty_tracking_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))

    op.create_table(
        "inventory_batches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("warehouse_id", sa.Integer(), nullable=False),
        sa.Column("batch_number", sa.String(length=128), nullable=False),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("warranty_until", sa.Date(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("available_quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"]),
        sa.UniqueConstraint("tenant_id", "warehouse_id", "product_id", "batch_number", name="uq_inventory_batches_scope"),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_inventory_batches_id", "inventory_batches", ["id"])
    op.create_index("ix_inventory_batches_batch_number", "inventory_batches", ["batch_number"])
    op.create_index("ix_inventory_batches_product_id", "inventory_batches", ["product_id"])
    op.create_index("ix_inventory_batches_warehouse_id", "inventory_batches", ["warehouse_id"])
    op.create_index("ix_inventory_batches_tenant_product", "inventory_batches", ["tenant_id", "product_id"])
    op.create_index("ix_inventory_batches_tenant_warehouse", "inventory_batches", ["tenant_id", "warehouse_id"])

    op.create_table(
        "inventory_serials",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("warehouse_id", sa.Integer(), nullable=False),
        sa.Column("batch_id", sa.Integer(), nullable=True),
        sa.Column("serial_number", sa.String(length=128), nullable=False),
        sa.Column("expires_on", sa.Date(), nullable=True),
        sa.Column("warranty_until", sa.Date(), nullable=True),
        sa.Column("status", inventory_serial_status_enum, nullable=False, server_default="IN_STOCK"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"]),
        sa.ForeignKeyConstraint(["batch_id"], ["inventory_batches.id"]),
        sa.UniqueConstraint("tenant_id", "serial_number", name="uq_inventory_serials_tenant_serial"),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_inventory_serials_id", "inventory_serials", ["id"])
    op.create_index("ix_inventory_serials_serial_number", "inventory_serials", ["serial_number"])
    op.create_index("ix_inventory_serials_batch_id", "inventory_serials", ["batch_id"])
    op.create_index("ix_inventory_serials_product_id", "inventory_serials", ["product_id"])
    op.create_index("ix_inventory_serials_warehouse_id", "inventory_serials", ["warehouse_id"])
    op.create_index("ix_inventory_serials_status", "inventory_serials", ["status"])
    op.create_index("ix_inventory_serials_tenant_product", "inventory_serials", ["tenant_id", "product_id"])
    op.create_index("ix_inventory_serials_tenant_warehouse", "inventory_serials", ["tenant_id", "warehouse_id"])
    op.create_index("ix_inventory_serials_tenant_status", "inventory_serials", ["tenant_id", "status"])


def downgrade() -> None:
    op.drop_index("ix_inventory_serials_tenant_status", table_name="inventory_serials")
    op.drop_index("ix_inventory_serials_tenant_warehouse", table_name="inventory_serials")
    op.drop_index("ix_inventory_serials_tenant_product", table_name="inventory_serials")
    op.drop_index("ix_inventory_serials_status", table_name="inventory_serials")
    op.drop_index("ix_inventory_serials_warehouse_id", table_name="inventory_serials")
    op.drop_index("ix_inventory_serials_product_id", table_name="inventory_serials")
    op.drop_index("ix_inventory_serials_batch_id", table_name="inventory_serials")
    op.drop_index("ix_inventory_serials_serial_number", table_name="inventory_serials")
    op.drop_index("ix_inventory_serials_id", table_name="inventory_serials")
    op.drop_table("inventory_serials")

    op.drop_index("ix_inventory_batches_tenant_warehouse", table_name="inventory_batches")
    op.drop_index("ix_inventory_batches_tenant_product", table_name="inventory_batches")
    op.drop_index("ix_inventory_batches_warehouse_id", table_name="inventory_batches")
    op.drop_index("ix_inventory_batches_product_id", table_name="inventory_batches")
    op.drop_index("ix_inventory_batches_batch_number", table_name="inventory_batches")
    op.drop_index("ix_inventory_batches_id", table_name="inventory_batches")
    op.drop_table("inventory_batches")

    op.drop_column("products", "warranty_tracking_enabled")
    op.drop_column("products", "expiry_tracking_enabled")
    op.drop_column("products", "batch_tracking_enabled")
    op.drop_column("products", "serial_tracking_enabled")

    inventory_serial_status_enum.drop(op.get_bind(), checkfirst=False)
