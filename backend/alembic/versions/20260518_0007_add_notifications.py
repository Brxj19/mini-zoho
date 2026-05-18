"""add notifications

Revision ID: 20260518_0007
Revises: 20260518_0006
Create Date: 2026-05-18 00:07:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260518_0007"
down_revision = "20260518_0006"
branch_labels = None
depends_on = None


notification_type_enum = sa.Enum(
    "LOW_STOCK",
    "ORDER_STATUS",
    "PURCHASE_RECEIVE",
    "STOCK_ALERT",
    "SYSTEM",
    name="notification_type_enum",
)


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("type", notification_type_enum, nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        mysql_engine="InnoDB",
    )
    op.create_index("ix_notifications_id", "notifications", ["id"])
    op.create_index("ix_notifications_tenant_id", "notifications", ["tenant_id"])
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_type", "notifications", ["type"])
    op.create_index("ix_notifications_is_read", "notifications", ["is_read"])
    op.create_index("ix_notifications_tenant_user", "notifications", ["tenant_id", "user_id"])
    op.create_index("ix_notifications_tenant_read", "notifications", ["tenant_id", "is_read"])
    op.create_index("ix_notifications_user_read", "notifications", ["user_id", "is_read"])


def downgrade() -> None:
    op.drop_index("ix_notifications_user_read", table_name="notifications")
    op.drop_index("ix_notifications_tenant_read", table_name="notifications")
    op.drop_index("ix_notifications_tenant_user", table_name="notifications")
    op.drop_index("ix_notifications_is_read", table_name="notifications")
    op.drop_index("ix_notifications_type", table_name="notifications")
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_index("ix_notifications_tenant_id", table_name="notifications")
    op.drop_index("ix_notifications_id", table_name="notifications")
    op.drop_table("notifications")

    notification_type_enum.drop(op.get_bind(), checkfirst=False)
