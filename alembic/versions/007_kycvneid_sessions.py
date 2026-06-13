"""Bảng kycvneid_sessions — KYC tự động qua Live Text + QR VNeID.

Revision ID: 007_kycvneid_sessions
"""
from alembic import op
import sqlalchemy as sa

revision      = "007_kycvneid_sessions"
down_revision = "006_kyc_vneid_photo_paths"
branch_labels = None
depends_on    = None


def upgrade():
    op.create_table(
        "kycvneid_sessions",
        sa.Column("id",           sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id",      sa.String(36), nullable=False, index=True),
        sa.Column("session_id",   sa.String(32), nullable=False, unique=True),
        sa.Column("kyc_type",     sa.String(20),  nullable=False, server_default="VNEID"),

        # Trạng thái phiên
        sa.Column("status",         sa.String(30), nullable=False, server_default="WAITING_LIVE_TEXT"),
        sa.Column("verify_method",  sa.String(40), nullable=True),

        # Thông tin từ Live Text (nguồn chính)
        sa.Column("cccd",               sa.String(20),  nullable=True),
        sa.Column("full_name",          sa.String(200), nullable=True),
        sa.Column("date_of_birth",      sa.Date,        nullable=True),
        sa.Column("gender",             sa.String(10),  nullable=True),
        sa.Column("nationality",        sa.String(50),  nullable=True),
        sa.Column("place_of_residence", sa.Text,        nullable=True),
        sa.Column("place_of_birth",     sa.Text,        nullable=True),
        sa.Column("issue_date",         sa.Date,        nullable=True),
        sa.Column("expiry_date",        sa.Date,        nullable=True),

        # Dữ liệu gốc (JSON) — từ parser và QR
        sa.Column("live_text_data_json",   sa.Text, nullable=True),
        sa.Column("qr_data_json",          sa.Text, nullable=True),
        sa.Column("mismatch_detail_json",  sa.Text, nullable=True),

        # Ảnh VNeID
        sa.Column("vneid_image_file_id",  sa.String(200), nullable=True),
        sa.Column("vneid_image_path",     sa.Text,        nullable=True),

        # Ảnh chân dung
        sa.Column("portrait_image_file_id", sa.String(200), nullable=True),
        sa.Column("portrait_image_path",    sa.Text,        nullable=True),
        sa.Column("portrait_uploaded",      sa.Boolean,     nullable=False, server_default="false"),

        # Thời gian
        sa.Column("verified_at",  sa.DateTime, nullable=True),
        sa.Column("created_at",   sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at",   sa.DateTime, nullable=False, server_default=sa.func.now(),
                  onupdate=sa.func.now()),
    )


def downgrade():
    op.drop_table("kycvneid_sessions")
