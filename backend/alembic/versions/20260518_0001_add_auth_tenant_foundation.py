"""add auth tenant foundation

Revision ID: 20260518_0001
Revises:
Create Date: 2026-05-18 00:01:00
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260518_0001"
down_revision = None
branch_labels = None
depends_on = None


tenant_status_enum = sa.Enum("ACTIVE", "DISABLED", name="tenant_status_enum")
user_role_enum = sa.Enum(
    "SUPER_ADMIN",
    "TENANT_ADMIN",
    "INVENTORY_MANAGER",
    "SALES_STAFF",
    "PURCHASE_STAFF",
    "VIEWER",
    name="user_role_enum",
)
user_status_enum = sa.Enum("ACTIVE", "INACTIVE", name="user_status_enum")


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("company_name", sa.String(length=255), nullable=False),
        sa.Column("contact_email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("gst_number", sa.String(length=64), nullable=True),
        sa.Column("business_type", sa.String(length=128), nullable=True),
        sa.Column("status", tenant_status_enum, nullable=False, server_default="ACTIVE"),
        sa.Column("subscription_plan_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_tenants_company_name", "tenants", ["company_name"])
    op.create_index("ix_tenants_contact_email", "tenants", ["contact_email"])
    op.create_index("ix_tenants_status", "tenants", ["status"])

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", user_role_enum, nullable=False),
        sa.Column("status", user_status_enum, nullable=False, server_default="ACTIVE"),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.UniqueConstraint("email", name="uq_users_email"),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_status", "users", ["status"])
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])
    op.create_index("ix_users_tenant_role", "users", ["tenant_id", "role"])
    op.create_index("ix_users_tenant_status", "users", ["tenant_id", "status"])


def downgrade() -> None:
    op.drop_index("ix_users_tenant_status", table_name="users")
    op.drop_index("ix_users_tenant_role", table_name="users")
    op.drop_index("ix_users_tenant_id", table_name="users")
    op.drop_index("ix_users_status", table_name="users")
    op.drop_index("ix_users_role", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.drop_index("ix_tenants_status", table_name="tenants")
    op.drop_index("ix_tenants_contact_email", table_name="tenants")
    op.drop_index("ix_tenants_company_name", table_name="tenants")
    op.drop_table("tenants")

    user_status_enum.drop(op.get_bind(), checkfirst=False)
    user_role_enum.drop(op.get_bind(), checkfirst=False)
    tenant_status_enum.drop(op.get_bind(), checkfirst=False)
