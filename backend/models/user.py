import uuid
from datetime import datetime
from sqlalchemy import String, BigInteger, Index
from sqlalchemy.orm import Mapped, mapped_column
from backend.core.database import Base
from backend.models.base import TimestampMixin, UUIDPrimaryKey


class User(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "users"

    user_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, nullable=True)
    telegram_username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACCOUNT_CREATED")
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="USER")

    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_telegram_id", "telegram_id"),
        Index("ix_users_user_code", "user_code"),
    )


class UserStatus:
    ACCOUNT_CREATED = "ACCOUNT_CREATED"
    WAITING_FIRST_LOGIN = "WAITING_FIRST_LOGIN"
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    SUSPENDED = "SUSPENDED"
    DISABLED = "DISABLED"


class UserRole:
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"
