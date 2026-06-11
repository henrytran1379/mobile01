import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from backend.repositories.audit_repository import SecurityAlertRepository, AuditLogRepository
from backend.repositories.security_repository import UserSecurityRepository
from backend.core.redis import get_redis
from backend.core.config import settings


class SecurityService:
    def __init__(self, session: AsyncSession):
        self.alert_repo = SecurityAlertRepository(session)
        self.audit_repo = AuditLogRepository(session)
        self.security_repo = UserSecurityRepository(session)

    async def check_rate_limit(self, key: str, limit: int, window_seconds: int) -> bool:
        r = await get_redis()
        current = await r.incr(key)
        if current == 1:
            await r.expire(key, window_seconds)
        return current <= limit

    async def detect_suspicious_login(
        self, user_id: uuid.UUID, ip_address: str | None, failed_count: int
    ) -> None:
        if failed_count >= 3:
            await self.alert_repo.create_alert(
                alert_type="SUSPICIOUS_LOGIN_ATTEMPTS",
                severity="MEDIUM" if failed_count < 5 else "HIGH",
                user_id=user_id,
                details={"failed_count": failed_count, "ip_address": ip_address},
            )

    async def get_open_alerts(self, user_id: str | None = None) -> list[dict]:
        uid = uuid.UUID(user_id) if user_id else None
        alerts = await self.alert_repo.get_open_alerts(uid)
        return [
            {
                "id": str(a.id),
                "type": a.alert_type,
                "severity": a.severity,
                "status": a.status,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in alerts
        ]
