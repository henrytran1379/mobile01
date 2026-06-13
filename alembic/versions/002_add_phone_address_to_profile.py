"""Add phone and address to user_profiles

Revision ID: 002
Revises: 001
Create Date: 2026-06-12
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user_profiles", sa.Column("phone", sa.String(20), nullable=True))
    op.add_column("user_profiles", sa.Column("address", sa.Text, nullable=True))


def downgrade() -> None:
    op.drop_column("user_profiles", "address")
    op.drop_column("user_profiles", "phone")
