"""Full KYC system tables

Revision ID: 003
Revises: 002
Create Date: 2026-06-12
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── kyc_profiles ─────────────────────────────────────────────────────────
    op.create_table(
        "kyc_profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), unique=True, nullable=False),
        sa.Column("telegram_user_id", sa.BigInteger, nullable=True),
        sa.Column("personal_id_hash", sa.String(64), nullable=True),      # SHA-256 of plain ID
        sa.Column("personal_id_encrypted", sa.Text, nullable=True),       # Fernet-encrypted
        sa.Column("personal_id_masked", sa.String(20), nullable=True),    # e.g. 042079******
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("date_of_birth", sa.Date, nullable=True),
        sa.Column("gender", sa.String(10), nullable=True),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("issue_date", sa.Date, nullable=True),
        sa.Column("expiry_date", sa.Date, nullable=True),
        sa.Column("nationality", sa.String(100), nullable=True),
        sa.Column("verification_level", sa.Integer, nullable=False, server_default="0"),
        sa.Column("status", sa.String(30), nullable=False, server_default="PENDING"),
        sa.Column("reject_reason", sa.Text, nullable=True),
        sa.Column("face_match_score", sa.Float, nullable=True),
        sa.Column("extraction_source", sa.String(20), nullable=True),     # QR / OCR / MANUAL
        sa.Column("reviewed_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_kyc_profiles_user_id", "kyc_profiles", ["user_id"])
    op.create_index("ix_kyc_profiles_status", "kyc_profiles", ["status"])
    op.create_index("ix_kyc_profiles_personal_id_hash", "kyc_profiles", ["personal_id_hash"])

    # ── kyc_documents ─────────────────────────────────────────────────────────
    op.create_table(
        "kyc_documents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("kyc_profile_id", UUID(as_uuid=True), sa.ForeignKey("kyc_profiles.id"), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("doc_type", sa.String(30), nullable=False),   # FRONT / BACK / SELFIE
        sa.Column("file_path", sa.Text, nullable=False),
        sa.Column("file_hash", sa.String(64), nullable=True),
        sa.Column("file_size", sa.Integer, nullable=True),
        sa.Column("width", sa.Integer, nullable=True),
        sa.Column("height", sa.Integer, nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_kyc_documents_kyc_profile_id", "kyc_documents", ["kyc_profile_id"])

    # ── kyc_face_match ────────────────────────────────────────────────────────
    op.create_table(
        "kyc_face_match",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("kyc_profile_id", UUID(as_uuid=True), sa.ForeignKey("kyc_profiles.id"), nullable=False),
        sa.Column("score", sa.Float, nullable=False),
        sa.Column("result", sa.String(10), nullable=False),     # PASS / REVIEW / FAIL
        sa.Column("algorithm", sa.String(50), nullable=False),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── kyc_review_queue ──────────────────────────────────────────────────────
    op.create_table(
        "kyc_review_queue",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("kyc_profile_id", UUID(as_uuid=True), sa.ForeignKey("kyc_profiles.id"), unique=True, nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("priority", sa.Integer, nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("assigned_to", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_kyc_review_queue_status", "kyc_review_queue", ["status"])
    op.create_index("ix_kyc_review_queue_priority", "kyc_review_queue", ["priority"])

    # ── kyc_audit_logs ────────────────────────────────────────────────────────
    op.create_table(
        "kyc_audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("kyc_profile_id", UUID(as_uuid=True), sa.ForeignKey("kyc_profiles.id"), nullable=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("actor_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(60), nullable=False),
        sa.Column("old_value", sa.Text, nullable=True),
        sa.Column("new_value", sa.Text, nullable=True),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("ip_address", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_kyc_audit_logs_user_id", "kyc_audit_logs", ["user_id"])
    op.create_index("ix_kyc_audit_logs_action", "kyc_audit_logs", ["action"])

    # ── kyc_events ────────────────────────────────────────────────────────────
    op.create_table(
        "kyc_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("kyc_profile_id", UUID(as_uuid=True), sa.ForeignKey("kyc_profiles.id"), nullable=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("event_type", sa.String(60), nullable=False),
        sa.Column("payload", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_kyc_events_user_id", "kyc_events", ["user_id"])
    op.create_index("ix_kyc_events_event_type", "kyc_events", ["event_type"])


def downgrade() -> None:
    op.drop_table("kyc_events")
    op.drop_table("kyc_audit_logs")
    op.drop_table("kyc_review_queue")
    op.drop_table("kyc_face_match")
    op.drop_table("kyc_documents")
    op.drop_table("kyc_profiles")
