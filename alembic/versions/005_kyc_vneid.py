"""KYC VNeID submissions table.

Revision ID: 005_kyc_vneid
"""
from alembic import op
import sqlalchemy as sa

revision = "005_kyc_vneid"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "kyc_vneid",
        sa.Column("id",           sa.UUID,         primary_key=True,  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id",      sa.UUID,         sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("id_number",    sa.String(20),   nullable=False),
        sa.Column("full_name",    sa.String(255),  nullable=False),
        sa.Column("date_of_birth",sa.Date,         nullable=True),
        sa.Column("gender",       sa.String(10),   nullable=True),      # male / female
        sa.Column("nationality",  sa.String(50),   nullable=True),
        sa.Column("place_of_residence", sa.Text,   nullable=True),
        sa.Column("place_of_birth",     sa.Text,   nullable=True),
        sa.Column("issue_date",   sa.Date,         nullable=True),
        sa.Column("expiry_date",  sa.Date,         nullable=True),
        sa.Column("raw_text",     sa.Text,         nullable=True),
        sa.Column("source",       sa.String(60),   server_default="vneid_screenshot_live_text"),
        sa.Column("kyc_method",   sa.String(60),   server_default="vneid_screenshot_plus_live_text"),
        sa.Column("kyc_status",   sa.String(30),   server_default="CONFIRMED"),
        sa.Column("created_at",   sa.DateTime,     server_default=sa.text("NOW()")),
        sa.Column("confirmed_at", sa.DateTime,     nullable=True),
    )
    op.create_index("ix_kyc_vneid_user_id",   "kyc_vneid", ["user_id"])
    op.create_index("ix_kyc_vneid_id_number",  "kyc_vneid", ["id_number"])


def downgrade():
    op.drop_table("kyc_vneid")
