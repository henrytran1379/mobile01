import uuid
from datetime import date, datetime
from sqlalchemy import String, Date, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from backend.core.database import Base
from backend.models.base import TimestampMixin, UUIDPrimaryKey


class UserProfile(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)


class UserIdentityDocument(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "user_identity_documents"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    identity_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    issue_place: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
