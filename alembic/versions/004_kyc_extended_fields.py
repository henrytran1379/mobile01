"""Extended KYC fields for full CCCD data

Revision ID: 004
Revises: 003
Create Date: 2026-06-12
"""
from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None

_NEW_COLS = [
    ("place_of_birth",      sa.Text,          {}),
    ("place_of_residence",  sa.Text,          {}),
    ("issuing_authority",   sa.String(255),   {}),
    ("document_type",       sa.String(20),    {"server_default": "CCCD"}),
    ("full_name_normalized",sa.String(255),   {}),
    ("qr_raw_data",         sa.Text,          {}),
    ("mrz_line_1",          sa.Text,          {}),
    ("mrz_line_2",          sa.Text,          {}),
    ("mrz_line_3",          sa.Text,          {}),
    ("ocr_raw_text",        sa.Text,          {}),
    ("ocr_success",         sa.Boolean,       {}),
    ("qr_success",          sa.Boolean,       {}),
    ("mrz_success",         sa.Boolean,       {}),
    ("ocr_confidence",      sa.Float,         {}),
    ("qr_confidence",       sa.Float,         {}),
    ("mrz_confidence",      sa.Float,         {}),
    ("verification_method", sa.String(50),    {}),
    ("ownership_status",    sa.String(20),    {"server_default": "unknown"}),
]


def upgrade():
    for col_name, col_type, kwargs in _NEW_COLS:
        op.add_column(
            "kyc_profiles",
            sa.Column(col_name, col_type, nullable=True, **kwargs),
        )


def downgrade():
    for col_name, _, __ in reversed(_NEW_COLS):
        op.drop_column("kyc_profiles", col_name)
