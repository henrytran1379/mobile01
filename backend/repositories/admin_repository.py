import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.admin import AdminUser, ReviewQueue
from backend.repositories.base import BaseRepository


class AdminUserRepository(BaseRepository[AdminUser]):
    def __init__(self, session: AsyncSession):
        super().__init__(AdminUser, session)

    async def get_by_user_id(self, user_id: uuid.UUID) -> AdminUser | None:
        result = await self.session.execute(
            select(AdminUser).where(AdminUser.user_id == user_id, AdminUser.is_active == True)
        )
        return result.scalar_one_or_none()

    async def is_admin(self, user_id: uuid.UUID) -> bool:
        return await self.get_by_user_id(user_id) is not None


class ReviewQueueRepository(BaseRepository[ReviewQueue]):
    def __init__(self, session: AsyncSession):
        super().__init__(ReviewQueue, session)

    async def get_pending(self, review_type: str | None = None) -> list[ReviewQueue]:
        query = select(ReviewQueue).where(ReviewQueue.status == "PENDING").order_by(
            ReviewQueue.priority.desc(), ReviewQueue.created_at.asc()
        )
        if review_type:
            query = query.where(ReviewQueue.review_type == review_type)
        result = await self.session.execute(query)
        return list(result.scalars().all())
