import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from backend.repositories.kyc_repository import KYCRepository, UserDocumentRepository, VerificationReviewRepository
from backend.repositories.audit_repository import AuditLogRepository
from backend.models.kyc import ReviewType, DocumentType


class KYCService:
    def __init__(self, session: AsyncSession):
        self.kyc_repo = KYCRepository(session)
        self.doc_repo = UserDocumentRepository(session)
        self.review_repo = VerificationReviewRepository(session)
        self.audit_repo = AuditLogRepository(session)

    async def submit_kyc(
        self,
        user_id: str,
        front_url: str,
        back_url: str,
        selfie_url: str,
        ip_address: str | None = None,
    ) -> dict:
        uid = uuid.UUID(user_id)
        now = datetime.now(timezone.utc)

        submission = await self.kyc_repo.create(
            user_id=uid,
            front_image_url=front_url,
            back_image_url=back_url,
            selfie_image_url=selfie_url,
            status="PENDING",
            submitted_at=now,
        )

        for doc_type, url in [
            (DocumentType.CCCD_FRONT, front_url),
            (DocumentType.CCCD_BACK, back_url),
            (DocumentType.SELFIE, selfie_url),
        ]:
            await self.doc_repo.create(
                user_id=uid, document_type=doc_type, file_url=url, created_at=now
            )

        review = await self.review_repo.create(
            user_id=uid,
            review_type=ReviewType.KYC,
            review_status="PENDING",
            created_at=now,
        )

        await self.audit_repo.log(
            action="KYC_SUBMITTED",
            actor_type="USER",
            actor_id=uid,
            target_id=submission.id,
            target_type="KYC_SUBMISSION",
            ip_address=ip_address,
        )

        return {"submission_id": str(submission.id), "status": "PENDING"}

    async def get_status(self, user_id: str) -> dict:
        uid = uuid.UUID(user_id)
        submission = await self.kyc_repo.get_latest_by_user(uid)
        if not submission:
            return {"status": "NOT_SUBMITTED"}
        return {
            "submission_id": str(submission.id),
            "status": submission.status,
            "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
            "reviewed_at": submission.reviewed_at.isoformat() if submission.reviewed_at else None,
        }
