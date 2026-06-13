"""Thêm cột lưu đường dẫn ảnh vào kyc_vneid.

screenshot_path  — ảnh màn hình VNeID app
portrait_path    — ảnh chân dung user

Revision ID: 006_kyc_vneid_photo_paths
"""
from alembic import op
import sqlalchemy as sa

revision = "006_kyc_vneid_photo_paths"
down_revision = "005_kyc_vneid"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("kyc_vneid", sa.Column("screenshot_path", sa.Text, nullable=True))
    op.add_column("kyc_vneid", sa.Column("portrait_path",   sa.Text, nullable=True))
    op.add_column("kyc_vneid", sa.Column("kyc_session_id",  sa.String(32), nullable=True))


def downgrade():
    op.drop_column("kyc_vneid", "screenshot_path")
    op.drop_column("kyc_vneid", "portrait_path")
    op.drop_column("kyc_vneid", "kyc_session_id")
