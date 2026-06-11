import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.core.database import Base
from backend.models.base import UUIDPrimaryKey


class AuditLog(Base, UUIDPrimaryKey):
    __tablename__ = "audit_logs"

    actor_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    actor_type: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    target_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    target_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra_data: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("ix_audit_logs_actor_id", "actor_id"),
        Index("ix_audit_logs_target_id", "target_id"),
    )


class SecurityAlert(Base, UUIDPrimaryKey):
    __tablename__ = "security_alerts"

    user_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    alert_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="LOW")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="OPEN")
    extra_data: Mapped[dict | None] = mapped_column("details", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ActorType:
    USER = "USER"
    ADMIN = "ADMIN"
    SYSTEM = "SYSTEM"


class AlertSeverity:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
