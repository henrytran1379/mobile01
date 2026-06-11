"""Initial schema - Phase 1

Revision ID: 001
Revises:
Create Date: 2026-06-11
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_code", sa.String(50), unique=True, nullable=False),
        sa.Column("telegram_id", sa.BigInteger, unique=True, nullable=True),
        sa.Column("telegram_username", sa.String(100), nullable=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("status", sa.String(50), nullable=False, default="ACCOUNT_CREATED"),
        sa.Column("role", sa.String(50), nullable=False, default="USER"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"])
    op.create_index("ix_users_user_code", "users", ["user_code"])

    op.create_table(
        "user_security",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), unique=True, nullable=False),
        sa.Column("password_hash", sa.Text, nullable=False),
        sa.Column("password_changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("two_factor_enabled", sa.Boolean, default=False),
        sa.Column("two_factor_secret", sa.Text, nullable=True),
        sa.Column("failed_login_count", sa.Integer, default=0),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "registration_sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("temporary_password_hash", sa.Text, nullable=False),
        sa.Column("activation_token_hash", sa.Text, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "user_sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("session_token_hash", sa.Text, nullable=False),
        sa.Column("refresh_token_hash", sa.Text, nullable=True),
        sa.Column("ip_address", sa.String(100), nullable=True),
        sa.Column("device_info", sa.Text, nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "recovery_codes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("code_hash", sa.Text, nullable=False),
        sa.Column("used", sa.Boolean, default=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "user_profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), unique=True, nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("date_of_birth", sa.Date, nullable=True),
        sa.Column("gender", sa.String(20), nullable=True),
        sa.Column("nationality", sa.String(100), nullable=True),
        sa.Column("avatar_url", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "user_identity_documents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("identity_number", sa.String(50), nullable=True),
        sa.Column("issue_date", sa.Date, nullable=True),
        sa.Column("issue_place", sa.String(255), nullable=True),
        sa.Column("expiry_date", sa.Date, nullable=True),
        sa.Column("document_type", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_identity_documents_number", "user_identity_documents", ["identity_number"])

    op.create_table(
        "kyc_submissions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("front_image_url", sa.Text, nullable=True),
        sa.Column("back_image_url", sa.Text, nullable=True),
        sa.Column("selfie_image_url", sa.Text, nullable=True),
        sa.Column("ocr_data", JSONB, nullable=True),
        sa.Column("status", sa.String(50), nullable=False, default="PENDING"),
        sa.Column("submitted_at", sa.DateTime(timezone=True)),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "ekyc_submissions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("provider_name", sa.String(100), nullable=True),
        sa.Column("provider_reference", sa.String(255), nullable=True),
        sa.Column("pdf_url", sa.Text, nullable=True),
        sa.Column("parsed_data", JSONB, nullable=True),
        sa.Column("status", sa.String(50), nullable=False, default="PENDING"),
        sa.Column("submitted_at", sa.DateTime(timezone=True)),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "verification_reviews",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("review_type", sa.String(50), nullable=False),
        sa.Column("review_status", sa.String(50), nullable=False, default="PENDING"),
        sa.Column("admin_id", UUID(as_uuid=True), nullable=True),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "user_documents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("document_type", sa.String(50), nullable=False),
        sa.Column("file_url", sa.Text, nullable=False),
        sa.Column("file_hash", sa.Text, nullable=True),
        sa.Column("is_encrypted", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "user_wallets",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("network", sa.String(50), nullable=False),
        sa.Column("wallet_address", sa.String(255), nullable=False),
        sa.Column("wallet_type", sa.String(50), nullable=False, default="PRIMARY"),
        sa.Column("status", sa.String(50), nullable=False, default="PENDING"),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_user_wallets_address", "user_wallets", ["wallet_address"])

    op.create_table(
        "wallet_verifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("wallet_id", UUID(as_uuid=True), sa.ForeignKey("user_wallets.id"), nullable=False),
        sa.Column("verification_address", sa.String(255), nullable=True),
        sa.Column("txid", sa.String(255), nullable=True),
        sa.Column("amount", sa.Numeric(38, 18), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, default="PENDING"),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "credit_accounts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), unique=True, nullable=False),
        sa.Column("balance", sa.BigInteger, default=0, nullable=False),
        sa.Column("total_earned", sa.BigInteger, default=0, nullable=False),
        sa.Column("total_spent", sa.BigInteger, default=0, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "credit_ledger",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("ledger_type", sa.String(100), nullable=False),
        sa.Column("amount", sa.BigInteger, nullable=False),
        sa.Column("balance_before", sa.BigInteger, nullable=False),
        sa.Column("balance_after", sa.BigInteger, nullable=False),
        sa.Column("reference_id", UUID(as_uuid=True), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_credit_ledger_user_id", "credit_ledger", ["user_id"])

    op.create_table(
        "admin_users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), unique=True, nullable=False),
        sa.Column("admin_level", sa.String(50), nullable=False, default="ADMIN"),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "admin_roles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("role_name", sa.String(100), unique=True, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "review_queue",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("review_type", sa.String(50), nullable=False),
        sa.Column("target_id", UUID(as_uuid=True), nullable=False),
        sa.Column("priority", sa.Integer, default=0),
        sa.Column("status", sa.String(50), nullable=False, default="PENDING"),
        sa.Column("assigned_admin", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "security_alerts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), nullable=True),
        sa.Column("alert_type", sa.String(100), nullable=False),
        sa.Column("severity", sa.String(50), nullable=False, default="LOW"),
        sa.Column("status", sa.String(50), nullable=False, default="OPEN"),
        sa.Column("details", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("actor_id", UUID(as_uuid=True), nullable=True),
        sa.Column("actor_type", sa.String(50), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("target_id", UUID(as_uuid=True), nullable=True),
        sa.Column("target_type", sa.String(100), nullable=True),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column("ip_address", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_audit_logs_actor_id", "audit_logs", ["actor_id"])
    op.create_index("ix_audit_logs_target_id", "audit_logs", ["target_id"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("security_alerts")
    op.drop_table("review_queue")
    op.drop_table("admin_roles")
    op.drop_table("admin_users")
    op.drop_table("credit_ledger")
    op.drop_table("credit_accounts")
    op.drop_table("wallet_verifications")
    op.drop_table("user_wallets")
    op.drop_table("user_documents")
    op.drop_table("verification_reviews")
    op.drop_table("ekyc_submissions")
    op.drop_table("kyc_submissions")
    op.drop_table("user_identity_documents")
    op.drop_table("user_profiles")
    op.drop_table("recovery_codes")
    op.drop_table("user_sessions")
    op.drop_table("registration_sessions")
    op.drop_table("user_security")
    op.drop_table("users")
