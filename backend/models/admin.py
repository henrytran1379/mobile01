import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.core.database import Base
from backend.models.base import TimestampMixin, UUIDPrimaryKey


class AdminUser(Base, UUIDPrimaryKey):
    __tablename__ = "admin_users"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    admin_level: Mapped[str] = mapped_column(String(50), nullable=False, default="ADMIN")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AdminRole(Base, UUIDPrimaryKey):
    __tablename__ = "admin_roles"

    role_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ReviewQueue(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "review_queue"

    review_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    assigned_admin: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
