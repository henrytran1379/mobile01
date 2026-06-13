import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from backend.models.security import UserSecurity, RegistrationSession, UserSession, RecoveryCode
from backend.repositories.base import BaseRepository


class UserSecurityRepository(BaseRepository[UserSecurity]):
    def __init__(self, session: AsyncSession):
        super().__init__(UserSecurity, session)

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserSecurity | None:
        result = await self.session.execute(
            select(UserSecurity).where(UserSecurity.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def increment_failed_login(self, user_id: uuid.UUID) -> None:
        await self.session.execute(
            update(UserSecurity)
            .where(UserSecurity.user_id == user_id)
            .values(failed_login_count=UserSecurity.failed_login_count + 1)
        )

    async def reset_failed_login(self, user_id: uuid.UUID) -> None:
        await self.session.execute(
            update(UserSecurity)
            .where(UserSecurity.user_id == user_id)
            .values(failed_login_count=0, locked_until=None)
        )

    async def set_locked_until(self, user_id: uuid.UUID, locked_until: datetime) -> None:
        await self.session.execute(
            update(UserSecurity)
            .where(UserSecurity.user_id == user_id)
            .values(locked_until=locked_until)
        )

    async def update_last_login(self, user_id: uuid.UUID, last_login: datetime) -> None:
        await self.session.execute(
            update(UserSecurity)
            .where(UserSecurity.user_id == user_id)
            .values(last_login_at=last_login, failed_login_count=0, locked_until=None)
        )

    async def enable_2fa(self, user_id: uuid.UUID, secret: str) -> None:
        await self.session.execute(
            update(UserSecurity)
            .where(UserSecurity.user_id == user_id)
            .values(two_factor_enabled=True, two_factor_secret=secret)
        )

    async def disable_2fa(self, user_id: uuid.UUID) -> None:
        await self.session.execute(
            update(UserSecurity)
            .where(UserSecurity.user_id == user_id)
            .values(two_factor_enabled=False, two_factor_secret=None)
        )

    async def set_password(self, user_id: uuid.UUID, new_hash: str) -> None:
        """Set password hash (dùng khi tạo mới hoặc resend credentials)."""
        await self.session.execute(
            update(UserSecurity)
            .where(UserSecurity.user_id == user_id)
            .values(password_hash=new_hash)
        )

    async def change_password(self, user_id: uuid.UUID, new_hash: str) -> None:
        await self.session.execute(
            update(UserSecurity)
            .where(UserSecurity.user_id == user_id)
            .values(password_hash=new_hash, password_changed_at=datetime.utcnow())
        )


class RegistrationSessionRepository(BaseRepository[RegistrationSession]):
    def __init__(self, session: AsyncSession):
        super().__init__(RegistrationSession, session)

    async def get_active_by_user(self, user_id: uuid.UUID) -> RegistrationSession | None:
        result = await self.session.execute(
            select(RegistrationSession)
            .where(RegistrationSession.user_id == user_id, RegistrationSession.used == False)
        )
        return result.scalar_one_or_none()

    async def mark_used(self, session_id: uuid.UUID) -> None:
        await self.session.execute(
            update(RegistrationSession)
            .where(RegistrationSession.id == session_id)
            .values(used=True)
        )


class UserSessionRepository(BaseRepository[UserSession]):
    def __init__(self, session: AsyncSession):
        super().__init__(UserSession, session)

    async def get_active_sessions(self, user_id: uuid.UUID) -> list[UserSession]:
        result = await self.session.execute(
            select(UserSession)
            .where(UserSession.user_id == user_id, UserSession.is_active == True)
        )
        return list(result.scalars().all())

    async def deactivate_all(self, user_id: uuid.UUID) -> None:
        await self.session.execute(
            update(UserSession)
            .where(UserSession.user_id == user_id)
            .values(is_active=False)
        )


class RecoveryCodeRepository(BaseRepository[RecoveryCode]):
    def __init__(self, session: AsyncSession):
        super().__init__(RecoveryCode, session)

    async def get_unused_by_user(self, user_id: uuid.UUID) -> list[RecoveryCode]:
        result = await self.session.execute(
            select(RecoveryCode)
            .where(RecoveryCode.user_id == user_id, RecoveryCode.used == False)
        )
        return list(result.scalars().all())

    async def mark_used(self, code_id: uuid.UUID) -> None:
        await self.session.execute(
            update(RecoveryCode)
            .where(RecoveryCode.id == code_id)
            .values(used=True, used_at=datetime.utcnow())
        )
