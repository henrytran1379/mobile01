import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from backend.models.kyc_v2 import (
    KYCProfile, KYCDocument, KYCFaceMatch,
    KYCReviewQueue, KYCAuditLog, KYCEvent,
)
from backend.repositories.base import BaseRepository


class KYCProfileRepository(BaseRepository[KYCProfile]):
    def __init__(self, session: AsyncSession):
        super().__init__(KYCProfile, session)

    async def get_by_user_id(self, user_id: uuid.UUID) -> KYCProfile | None:
        r = await self.session.execute(
            select(KYCProfile).where(KYCProfile.user_id == user_id)
        )
        return r.scalar_one_or_none()

    async def get_by_personal_id_hash(self, id_hash: str) -> KYCProfile | None:
        r = await self.session.execute(
            select(KYCProfile).where(KYCProfile.personal_id_hash == id_hash)
        )
        return r.scalar_one_or_none()

    async def upsert(self, user_id: uuid.UUID, **kwargs) -> KYCProfile:
        profile = await self.get_by_user_id(user_id)
        now = datetime.utcnow()
        if profile:
            kwargs["updated_at"] = now
            await self.session.execute(
                update(KYCProfile).where(KYCProfile.user_id == user_id).values(**kwargs)
            )
            await self.session.flush()
            return await self.get_by_user_id(user_id)
        kwargs.update({"user_id": user_id, "created_at": now, "updated_at": now})
        return await self.create(**kwargs)

    async def set_status(self, profile_id: uuid.UUID, status: str, **extra) -> None:
        values = {"status": status, "updated_at": datetime.utcnow(), **extra}
        await self.session.execute(
            update(KYCProfile).where(KYCProfile.id == profile_id).values(**values)
        )

    async def list_by_status(self, status: str, limit: int = 50) -> list[KYCProfile]:
        r = await self.session.execute(
            select(KYCProfile)
            .where(KYCProfile.status == status)
            .order_by(KYCProfile.submitted_at.asc())
            .limit(limit)
        )
        return list(r.scalars().all())


class KYCDocumentRepository(BaseRepository[KYCDocument]):
    def __init__(self, session: AsyncSession):
        super().__init__(KYCDocument, session)

    async def get_by_profile_and_type(self, profile_id: uuid.UUID, doc_type: str) -> KYCDocument | None:
        r = await self.session.execute(
            select(KYCDocument)
            .where(KYCDocument.kyc_profile_id == profile_id, KYCDocument.doc_type == doc_type)
            .order_by(desc(KYCDocument.uploaded_at))
            .limit(1)
        )
        return r.scalar_one_or_none()

    async def list_by_profile(self, profile_id: uuid.UUID) -> list[KYCDocument]:
        r = await self.session.execute(
            select(KYCDocument).where(KYCDocument.kyc_profile_id == profile_id)
        )
        return list(r.scalars().all())


class KYCFaceMatchRepository(BaseRepository[KYCFaceMatch]):
    def __init__(self, session: AsyncSession):
        super().__init__(KYCFaceMatch, session)

    async def get_latest_by_profile(self, profile_id: uuid.UUID) -> KYCFaceMatch | None:
        r = await self.session.execute(
            select(KYCFaceMatch)
            .where(KYCFaceMatch.kyc_profile_id == profile_id)
            .order_by(desc(KYCFaceMatch.created_at))
            .limit(1)
        )
        return r.scalar_one_or_none()


class KYCReviewQueueRepository(BaseRepository[KYCReviewQueue]):
    def __init__(self, session: AsyncSession):
        super().__init__(KYCReviewQueue, session)

    async def get_by_profile(self, profile_id: uuid.UUID) -> KYCReviewQueue | None:
        r = await self.session.execute(
            select(KYCReviewQueue).where(KYCReviewQueue.kyc_profile_id == profile_id)
        )
        return r.scalar_one_or_none()

    async def get_pending(self, limit: int = 20) -> list[KYCReviewQueue]:
        r = await self.session.execute(
            select(KYCReviewQueue)
            .where(KYCReviewQueue.status == "PENDING")
            .order_by(desc(KYCReviewQueue.priority), KYCReviewQueue.created_at.asc())
            .limit(limit)
        )
        return list(r.scalars().all())

    async def mark_done(self, profile_id: uuid.UUID) -> None:
        now = datetime.utcnow()
        await self.session.execute(
            update(KYCReviewQueue)
            .where(KYCReviewQueue.kyc_profile_id == profile_id)
            .values(status="DONE", updated_at=now)
        )


class KYCAuditLogRepository(BaseRepository[KYCAuditLog]):
    def __init__(self, session: AsyncSession):
        super().__init__(KYCAuditLog, session)

    async def log(
        self,
        action: str,
        user_id: uuid.UUID | None = None,
        actor_id: uuid.UUID | None = None,
        kyc_profile_id: uuid.UUID | None = None,
        old_value: str | None = None,
        new_value: str | None = None,
        reason: str | None = None,
        ip_address: str | None = None,
    ) -> None:
        await self.create(
            action=action,
            user_id=user_id,
            actor_id=actor_id,
            kyc_profile_id=kyc_profile_id,
            old_value=old_value,
            new_value=new_value,
            reason=reason,
            ip_address=ip_address,
            created_at=datetime.utcnow(),
        )

    async def list_by_user(self, user_id: uuid.UUID, limit: int = 50) -> list[KYCAuditLog]:
        r = await self.session.execute(
            select(KYCAuditLog)
            .where(KYCAuditLog.user_id == user_id)
            .order_by(desc(KYCAuditLog.created_at))
            .limit(limit)
        )
        return list(r.scalars().all())


class KYCEventRepository(BaseRepository[KYCEvent]):
    def __init__(self, session: AsyncSession):
        super().__init__(KYCEvent, session)

    async def emit(
        self,
        event_type: str,
        user_id: uuid.UUID | None = None,
        kyc_profile_id: uuid.UUID | None = None,
        payload: dict | None = None,
    ) -> None:
        await self.create(
            event_type=event_type,
            user_id=user_id,
            kyc_profile_id=kyc_profile_id,
            payload=payload or {},
            created_at=datetime.utcnow(),
        )
