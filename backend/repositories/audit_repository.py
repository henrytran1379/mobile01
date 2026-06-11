import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.audit import AuditLog, SecurityAlert
from backend.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, session: AsyncSession):
        super().__init__(AuditLog, session)

    async def log(
        self,
        action: str,
        actor_type: str,
        actor_id: uuid.UUID | None = None,
        target_id: uuid.UUID | None = None,
        target_type: str | None = None,
        reason: str | None = None,
        metadata: dict | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        return await self.create(
            actor_id=actor_id,
            actor_type=actor_type,
            action=action,
            target_id=target_id,
            target_type=target_type,
            reason=reason,
            metadata=metadata,
            ip_address=ip_address,
            created_at=datetime.now(timezone.utc),
        )

    async def get_by_actor(self, actor_id: uuid.UUID, limit: int = 50) -> list[AuditLog]:
        result = await self.session.execute(
            select(AuditLog)
            .where(AuditLog.actor_id == actor_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


class SecurityAlertRepository(BaseRepository[SecurityAlert]):
    def __init__(self, session: AsyncSession):
        super().__init__(SecurityAlert, session)

    async def create_alert(
        self,
        alert_type: str,
        severity: str,
        user_id: uuid.UUID | None = None,
        details: dict | None = None,
    ) -> SecurityAlert:
        return await self.create(
            user_id=user_id,
            alert_type=alert_type,
            severity=severity,
            status="OPEN",
            details=details,
            created_at=datetime.now(timezone.utc),
        )

    async def get_open_alerts(self, user_id: uuid.UUID | None = None) -> list[SecurityAlert]:
        query = select(SecurityAlert).where(SecurityAlert.status == "OPEN")
        if user_id:
            query = query.where(SecurityAlert.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())
