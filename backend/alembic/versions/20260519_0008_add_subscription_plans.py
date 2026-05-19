"""add subscription plans

Revision ID: 20260519_0008
Revises: 20260518_0007
Create Date: 2026-05-19 00:08:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260519_0008"
down_revision = "20260518_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "subscription_plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("monthly_price", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("annual_price", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("max_users", sa.Integer(), nullable=True),
        sa.Column("max_products", sa.Integer(), nullable=True),
        sa.Column("max_warehouses", sa.Integer(), nullable=True),
        sa.Column("max_monthly_sales_orders", sa.Integer(), nullable=True),
        sa.Column("max_monthly_purchase_orders", sa.Integer(), nullable=True),
        sa.Column("max_monthly_stock_transfers", sa.Integer(), nullable=True),
        sa.Column("barcode_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("advanced_inventory_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("integrations_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("ai_assistant_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("code", name="uq_subscription_plans_code"),
        sa.UniqueConstraint("name", name="uq_subscription_plans_name"),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_subscription_plans_id", "subscription_plans", ["id"])
    op.create_index("ix_subscription_plans_code", "subscription_plans", ["code"])
    op.create_index("ix_subscription_plans_name", "subscription_plans", ["name"])

    subscription_plans = sa.table(
        "subscription_plans",
        sa.column("id", sa.Integer()),
        sa.column("code", sa.String()),
        sa.column("name", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("monthly_price", sa.Numeric()),
        sa.column("annual_price", sa.Numeric()),
        sa.column("max_users", sa.Integer()),
        sa.column("max_products", sa.Integer()),
        sa.column("max_warehouses", sa.Integer()),
        sa.column("max_monthly_sales_orders", sa.Integer()),
        sa.column("max_monthly_purchase_orders", sa.Integer()),
        sa.column("max_monthly_stock_transfers", sa.Integer()),
        sa.column("barcode_enabled", sa.Boolean()),
        sa.column("advanced_inventory_enabled", sa.Boolean()),
        sa.column("integrations_enabled", sa.Boolean()),
        sa.column("ai_assistant_enabled", sa.Boolean()),
    )
    op.bulk_insert(
        subscription_plans,
        [
            {
                "id": 1,
                "code": "STARTER",
                "name": "Starter",
                "description": "For smaller teams getting started with inventory operations.",
                "monthly_price": 1999,
                "annual_price": 19990,
                "max_users": 5,
                "max_products": 150,
                "max_warehouses": 2,
                "max_monthly_sales_orders": 150,
                "max_monthly_purchase_orders": 90,
                "max_monthly_stock_transfers": 60,
                "barcode_enabled": True,
                "advanced_inventory_enabled": False,
                "integrations_enabled": False,
                "ai_assistant_enabled": False,
            },
            {
                "id": 2,
                "code": "GROWTH",
                "name": "Growth",
                "description": "For scaling multi-channel retail teams needing deeper controls.",
                "monthly_price": 4999,
                "annual_price": 49990,
                "max_users": 20,
                "max_products": 1500,
                "max_warehouses": 8,
                "max_monthly_sales_orders": 1500,
                "max_monthly_purchase_orders": 750,
                "max_monthly_stock_transfers": 400,
                "barcode_enabled": True,
                "advanced_inventory_enabled": True,
                "integrations_enabled": True,
                "ai_assistant_enabled": True,
            },
            {
                "id": 3,
                "code": "SCALE",
                "name": "Scale",
                "description": "For mature operations with broad teams, advanced inventory, and integrations.",
                "monthly_price": 9999,
                "annual_price": 99990,
                "max_users": None,
                "max_products": None,
                "max_warehouses": None,
                "max_monthly_sales_orders": None,
                "max_monthly_purchase_orders": None,
                "max_monthly_stock_transfers": None,
                "barcode_enabled": True,
                "advanced_inventory_enabled": True,
                "integrations_enabled": True,
                "ai_assistant_enabled": True,
            },
        ],
    )

    op.execute("UPDATE tenants SET subscription_plan_id = 1 WHERE subscription_plan_id IS NULL")
    op.create_foreign_key(
        "fk_tenants_subscription_plan_id",
        "tenants",
        "subscription_plans",
        ["subscription_plan_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_tenants_subscription_plan_id", "tenants", type_="foreignkey")
    op.drop_index("ix_subscription_plans_name", table_name="subscription_plans")
    op.drop_index("ix_subscription_plans_code", table_name="subscription_plans")
    op.drop_index("ix_subscription_plans_id", table_name="subscription_plans")
    op.drop_table("subscription_plans")
