import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from backend.models.kyc import KYCSubmission, EKYCSubmission, VerificationReview, UserDocument
from backend.repositories.base import BaseRepository


class KYCRepository(BaseRepository[KYCSubmission]):
    def __init__(self, session: AsyncSession):
        super().__init__(KYCSubmission, session)

    async def get_latest_by_user(self, user_id: uuid.UUID) -> KYCSubmission | None:
        result = await self.session.execute(
            select(KYCSubmission)
            .where(KYCSubmission.user_id == user_id)
            .order_by(KYCSubmission.submitted_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


class EKYCRepository(BaseRepository[EKYCSubmission]):
    def __init__(self, session: AsyncSession):
        super().__init__(EKYCSubmission, session)

    async def get_latest_by_user(self, user_id: uuid.UUID) -> EKYCSubmission | None:
        result = await self.session.execute(
            select(EKYCSubmission)
            .where(EKYCSubmission.user_id == user_id)
            .order_by(EKYCSubmission.submitted_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


class VerificationReviewRepository(BaseRepository[VerificationReview]):
    def __init__(self, session: AsyncSession):
        super().__init__(VerificationReview, session)

    async def get_pending(self, review_type: str | None = None) -> list[VerificationReview]:
        query = select(VerificationReview).where(VerificationReview.review_status == "PENDING")
        if review_type:
            query = query.where(VerificationReview.review_type == review_type)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def approve(self, review_id: uuid.UUID, admin_id: uuid.UUID) -> None:
        await self.session.execute(
            update(VerificationReview)
            .where(VerificationReview.id == review_id)
            .values(review_status="APPROVED", admin_id=admin_id)
        )

    async def reject(self, review_id: uuid.UUID, admin_id: uuid.UUID, reason: str) -> None:
        await self.session.execute(
            update(VerificationReview)
            .where(VerificationReview.id == review_id)
            .values(review_status="REJECTED", admin_id=admin_id, reason=reason)
        )


class UserDocumentRepository(BaseRepository[UserDocument]):
    def __init__(self, session: AsyncSession):
        super().__init__(UserDocument, session)

    async def get_by_user_and_type(self, user_id: uuid.UUID, doc_type: str) -> list[UserDocument]:
        result = await self.session.execute(
            select(UserDocument)
            .where(UserDocument.user_id == user_id, UserDocument.document_type == doc_type)
        )
        return list(result.scalars().all())
