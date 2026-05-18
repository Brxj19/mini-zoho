"""add master data modules

Revision ID: 20260518_0002
Revises: 20260518_0001
Create Date: 2026-05-18 00:02:00
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260518_0002"
down_revision = "20260518_0001"
branch_labels = None
depends_on = None


record_status_enum = sa.Enum("ACTIVE", "ARCHIVED", name="record_status_enum")


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", record_status_enum, nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.UniqueConstraint("tenant_id", "name", name="uq_categories_tenant_name"),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_categories_id", "categories", ["id"])
    op.create_index("ix_categories_status", "categories", ["status"])
    op.create_index("ix_categories_tenant_id", "categories", ["tenant_id"])
    op.create_index("ix_categories_tenant_status", "categories", ["tenant_id", "status"])

    op.create_table(
        "brands",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", record_status_enum, nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.UniqueConstraint("tenant_id", "name", name="uq_brands_tenant_name"),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_brands_id", "brands", ["id"])
    op.create_index("ix_brands_status", "brands", ["status"])
    op.create_index("ix_brands_tenant_id", "brands", ["tenant_id"])
    op.create_index("ix_brands_tenant_status", "brands", ["tenant_id", "status"])

    op.create_table(
        "vendors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("gst_number", sa.String(length=64), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("opening_balance", sa.Numeric(12, 2), nullable=True),
        sa.Column("status", record_status_enum, nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_vendors_id", "vendors", ["id"])
    op.create_index("ix_vendors_status", "vendors", ["status"])
    op.create_index("ix_vendors_tenant_id", "vendors", ["tenant_id"])
    op.create_index("ix_vendors_tenant_name", "vendors", ["tenant_id", "name"])
    op.create_index("ix_vendors_tenant_status", "vendors", ["tenant_id", "status"])

    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("gst_number", sa.String(length=64), nullable=True),
        sa.Column("billing_address", sa.Text(), nullable=True),
        sa.Column("shipping_address", sa.Text(), nullable=True),
        sa.Column("status", record_status_enum, nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_customers_id", "customers", ["id"])
    op.create_index("ix_customers_status", "customers", ["status"])
    op.create_index("ix_customers_tenant_id", "customers", ["tenant_id"])
    op.create_index("ix_customers_tenant_name", "customers", ["tenant_id", "name"])
    op.create_index("ix_customers_tenant_status", "customers", ["tenant_id", "status"])

    op.create_table(
        "warehouses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(length=128), nullable=True),
        sa.Column("state", sa.String(length=128), nullable=True),
        sa.Column("country", sa.String(length=128), nullable=True),
        sa.Column("manager_name", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", record_status_enum, nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.UniqueConstraint("tenant_id", "code", name="uq_warehouses_tenant_code"),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_warehouses_id", "warehouses", ["id"])
    op.create_index("ix_warehouses_status", "warehouses", ["status"])
    op.create_index("ix_warehouses_tenant_id", "warehouses", ["tenant_id"])
    op.create_index("ix_warehouses_tenant_default", "warehouses", ["tenant_id", "is_default"])
    op.create_index("ix_warehouses_tenant_name", "warehouses", ["tenant_id", "name"])
    op.create_index("ix_warehouses_tenant_status", "warehouses", ["tenant_id", "status"])


def downgrade() -> None:
    op.drop_index("ix_warehouses_tenant_status", table_name="warehouses")
    op.drop_index("ix_warehouses_tenant_name", table_name="warehouses")
    op.drop_index("ix_warehouses_tenant_default", table_name="warehouses")
    op.drop_index("ix_warehouses_tenant_id", table_name="warehouses")
    op.drop_index("ix_warehouses_status", table_name="warehouses")
    op.drop_index("ix_warehouses_id", table_name="warehouses")
    op.drop_table("warehouses")

    op.drop_index("ix_customers_tenant_status", table_name="customers")
    op.drop_index("ix_customers_tenant_name", table_name="customers")
    op.drop_index("ix_customers_tenant_id", table_name="customers")
    op.drop_index("ix_customers_status", table_name="customers")
    op.drop_index("ix_customers_id", table_name="customers")
    op.drop_table("customers")

    op.drop_index("ix_vendors_tenant_status", table_name="vendors")
    op.drop_index("ix_vendors_tenant_name", table_name="vendors")
    op.drop_index("ix_vendors_tenant_id", table_name="vendors")
    op.drop_index("ix_vendors_status", table_name="vendors")
    op.drop_index("ix_vendors_id", table_name="vendors")
    op.drop_table("vendors")

    op.drop_index("ix_brands_tenant_status", table_name="brands")
    op.drop_index("ix_brands_tenant_id", table_name="brands")
    op.drop_index("ix_brands_status", table_name="brands")
    op.drop_index("ix_brands_id", table_name="brands")
    op.drop_table("brands")

    op.drop_index("ix_categories_tenant_status", table_name="categories")
    op.drop_index("ix_categories_tenant_id", table_name="categories")
    op.drop_index("ix_categories_status", table_name="categories")
    op.drop_index("ix_categories_id", table_name="categories")
    op.drop_table("categories")

    record_status_enum.drop(op.get_bind(), checkfirst=False)
