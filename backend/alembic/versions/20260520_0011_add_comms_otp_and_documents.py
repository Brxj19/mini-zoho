"""add comms otp and documents

Revision ID: 20260520_0011
Revises: 20260519_0010
Create Date: 2026-05-20 18:30:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260520_0011"
down_revision = "20260519_0010"
branch_labels = None
depends_on = None


otp_channel_enum = sa.Enum("EMAIL", "SMS", name="otp_channel_enum")
otp_purpose_enum = sa.Enum("SIGNUP_VERIFY", "LOGIN_2FA", "PHONE_VERIFY", "PASSWORD_RESET", name="otp_purpose_enum")
otp_challenge_status_enum = sa.Enum("PENDING", "VERIFIED", "EXPIRED", "BLOCKED", name="otp_challenge_status_enum")


def upgrade() -> None:
    bind = op.get_bind()
    otp_channel_enum.create(bind, checkfirst=True)
    otp_purpose_enum.create(bind, checkfirst=True)
    otp_challenge_status_enum.create(bind, checkfirst=True)

    op.add_column("users", sa.Column("phone", sa.String(length=32), nullable=True))
    op.add_column("users", sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("phone_verified_at", sa.DateTime(timezone=True), nullable=True))

    op.create_table(
        "otp_challenges",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("channel", otp_channel_enum, nullable=False),
        sa.Column("purpose", otp_purpose_enum, nullable=False),
        sa.Column("destination", sa.String(length=255), nullable=False),
        sa.Column("otp_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("status", otp_challenge_status_enum, nullable=False, server_default="PENDING"),
        sa.Column("dev_plaintext_code", sa.String(length=16), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_otp_challenges_id", "otp_challenges", ["id"])
    op.create_index("ix_otp_challenges_tenant_id", "otp_challenges", ["tenant_id"])
    op.create_index("ix_otp_challenges_user_id", "otp_challenges", ["user_id"])
    op.create_index("ix_otp_challenges_channel", "otp_challenges", ["channel"])
    op.create_index("ix_otp_challenges_purpose", "otp_challenges", ["purpose"])
    op.create_index("ix_otp_challenges_destination", "otp_challenges", ["destination"])
    op.create_index("ix_otp_challenges_status", "otp_challenges", ["status"])
    op.create_index("ix_otp_challenges_expires_at", "otp_challenges", ["expires_at"])
    op.create_index("ix_otp_challenges_tenant_status", "otp_challenges", ["tenant_id", "status"])
    op.create_index("ix_otp_challenges_destination_status", "otp_challenges", ["destination", "status"])

    op.create_table(
        "sms_outbox",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("to_phone", sa.String(length=32), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="QUEUED"),
        sa.Column("provider_message_id", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sms_outbox_id", "sms_outbox", ["id"])
    op.create_index("ix_sms_outbox_tenant_id", "sms_outbox", ["tenant_id"])
    op.create_index("ix_sms_outbox_to_phone", "sms_outbox", ["to_phone"])
    op.create_index("ix_sms_outbox_status", "sms_outbox", ["status"])
    op.create_index("ix_sms_outbox_tenant_status", "sms_outbox", ["tenant_id", "status"])
    op.create_index("ix_sms_outbox_phone_created", "sms_outbox", ["to_phone", "created_at"])

    op.create_table(
        "email_outbox",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("to_email", sa.String(length=255), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("html_body", sa.Text(), nullable=False),
        sa.Column("text_body", sa.Text(), nullable=True),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="QUEUED"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_email_outbox_id", "email_outbox", ["id"])
    op.create_index("ix_email_outbox_tenant_id", "email_outbox", ["tenant_id"])
    op.create_index("ix_email_outbox_user_id", "email_outbox", ["user_id"])
    op.create_index("ix_email_outbox_to_email", "email_outbox", ["to_email"])
    op.create_index("ix_email_outbox_status", "email_outbox", ["status"])
    op.create_index("ix_email_outbox_tenant_status", "email_outbox", ["tenant_id", "status"])
    op.create_index("ix_email_outbox_recipient_created", "email_outbox", ["to_email", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_email_outbox_recipient_created", table_name="email_outbox")
    op.drop_index("ix_email_outbox_tenant_status", table_name="email_outbox")
    op.drop_index("ix_email_outbox_status", table_name="email_outbox")
    op.drop_index("ix_email_outbox_to_email", table_name="email_outbox")
    op.drop_index("ix_email_outbox_user_id", table_name="email_outbox")
    op.drop_index("ix_email_outbox_tenant_id", table_name="email_outbox")
    op.drop_index("ix_email_outbox_id", table_name="email_outbox")
    op.drop_table("email_outbox")

    op.drop_index("ix_sms_outbox_phone_created", table_name="sms_outbox")
    op.drop_index("ix_sms_outbox_tenant_status", table_name="sms_outbox")
    op.drop_index("ix_sms_outbox_status", table_name="sms_outbox")
    op.drop_index("ix_sms_outbox_to_phone", table_name="sms_outbox")
    op.drop_index("ix_sms_outbox_tenant_id", table_name="sms_outbox")
    op.drop_index("ix_sms_outbox_id", table_name="sms_outbox")
    op.drop_table("sms_outbox")

    op.drop_index("ix_otp_challenges_destination_status", table_name="otp_challenges")
    op.drop_index("ix_otp_challenges_tenant_status", table_name="otp_challenges")
    op.drop_index("ix_otp_challenges_expires_at", table_name="otp_challenges")
    op.drop_index("ix_otp_challenges_status", table_name="otp_challenges")
    op.drop_index("ix_otp_challenges_destination", table_name="otp_challenges")
    op.drop_index("ix_otp_challenges_purpose", table_name="otp_challenges")
    op.drop_index("ix_otp_challenges_channel", table_name="otp_challenges")
    op.drop_index("ix_otp_challenges_user_id", table_name="otp_challenges")
    op.drop_index("ix_otp_challenges_tenant_id", table_name="otp_challenges")
    op.drop_index("ix_otp_challenges_id", table_name="otp_challenges")
    op.drop_table("otp_challenges")

    op.drop_column("users", "phone_verified_at")
    op.drop_column("users", "email_verified_at")
    op.drop_column("users", "phone")

    otp_challenge_status_enum.drop(op.get_bind(), checkfirst=False)
    otp_purpose_enum.drop(op.get_bind(), checkfirst=False)
    otp_channel_enum.drop(op.get_bind(), checkfirst=False)
