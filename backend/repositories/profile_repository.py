import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.profile import UserProfile, UserIdentityDocument
from backend.repositories.base import BaseRepository


class UserProfileRepository(BaseRepository[UserProfile]):
    def __init__(self, session: AsyncSession):
        super().__init__(UserProfile, session)

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserProfile | None:
        result = await self.session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, user_id: uuid.UUID, **kwargs) -> UserProfile:
        profile = await self.get_by_user_id(user_id)
        if profile:
            for key, value in kwargs.items():
                setattr(profile, key, value)
            await self.session.flush()
            return profile
        return await self.create(user_id=user_id, **kwargs)


class IdentityDocumentRepository(BaseRepository[UserIdentityDocument]):
    def __init__(self, session: AsyncSession):
        super().__init__(UserIdentityDocument, session)

    async def get_by_user_id(self, user_id: uuid.UUID) -> UserIdentityDocument | None:
        result = await self.session.execute(
            select(UserIdentityDocument).where(UserIdentityDocument.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def identity_number_exists(self, number: str) -> bool:
        result = await self.session.execute(
            select(UserIdentityDocument.id).where(UserIdentityDocument.identity_number == number)
        )
        return result.scalar_one_or_none() is not None

    async def upsert(self, user_id: uuid.UUID, **kwargs) -> UserIdentityDocument:
        doc = await self.get_by_user_id(user_id)
        if doc:
            for key, value in kwargs.items():
                setattr(doc, key, value)
            await self.session.flush()
            return doc
        return await self.create(user_id=user_id, **kwargs)
