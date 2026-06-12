import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from backend.repositories.kyc_repository import EKYCRepository, UserDocumentRepository, VerificationReviewRepository
from backend.repositories.profile_repository import UserProfileRepository, IdentityDocumentRepository
from backend.repositories.audit_repository import AuditLogRepository
from backend.models.kyc import ReviewType, DocumentType
from backend.schemas.ekyc import EKYCResultRequest


class EKYCService:
    def __init__(self, session: AsyncSession):
        self.ekyc_repo = EKYCRepository(session)
        self.doc_repo = UserDocumentRepository(session)
        self.review_repo = VerificationReviewRepository(session)
        self.profile_repo = UserProfileRepository(session)
        self.identity_repo = IdentityDocumentRepository(session)
        self.audit_repo = AuditLogRepository(session)

    async def upload_pdf(
        self, user_id: str, pdf_url: str, provider_name: str | None = None, ip_address: str | None = None
    ) -> dict:
        uid = uuid.UUID(user_id)
        now = datetime.now(timezone.utc)

        submission = await self.ekyc_repo.create(
            user_id=uid,
            pdf_url=pdf_url,
            provider_name=provider_name,
            status="PENDING",
            submitted_at=now,
        )

        await self.doc_repo.create(
            user_id=uid, document_type=DocumentType.EKYC_PDF, file_url=pdf_url, created_at=now
        )

        await self.review_repo.create(
            user_id=uid,
            review_type=ReviewType.EKYC,
            review_status="PENDING",
            created_at=now,
        )

        await self.audit_repo.log(
            action="EKYC_SUBMITTED",
            actor_type="USER",
            actor_id=uid,
            target_id=submission.id,
            target_type="EKYC_SUBMISSION",
            ip_address=ip_address,
        )

        return {"submission_id": str(submission.id), "status": "PENDING"}

    async def save_result(
        self, user_id: str, data: EKYCResultRequest, ip_address: str | None = None
    ) -> dict:
        uid = uuid.UUID(user_id)
        now = datetime.now(timezone.utc)

        dob = datetime.strptime(data.date_of_birth, "%d/%m/%Y").date()
        issue_date = datetime.strptime(data.issue_date, "%d/%m/%Y").date()
        expiry_date = datetime.strptime(data.expiry_date, "%d/%m/%Y").date()

        parsed_data = {
            "identity_number": data.identity_number,
            "full_name": data.full_name,
            "date_of_birth": data.date_of_birth,
            "gender": data.gender,
            "hometown": data.hometown,
            "issue_date": data.issue_date,
            "expiry_date": data.expiry_date,
            "permanent_address": data.permanent_address,
            "is_real_person": data.is_real_person,
            "face_matched": data.face_matched,
        }

        submission = await self.ekyc_repo.create(
            user_id=uid,
            provider_name=data.provider_name,
            provider_reference=data.provider_reference,
            parsed_data=parsed_data,
            status="PENDING",
            submitted_at=now,
        )

        await self.profile_repo.upsert(
            uid,
            full_name=data.full_name,
            date_of_birth=dob,
            gender=data.gender,
        )

        await self.identity_repo.upsert(
            uid,
            identity_number=data.identity_number,
            issue_date=issue_date,
            expiry_date=expiry_date,
            document_type="CCCD",
        )

        await self.review_repo.create(
            user_id=uid,
            review_type=ReviewType.EKYC,
            review_status="PENDING",
            created_at=now,
        )

        await self.audit_repo.log(
            action="EKYC_SUBMITTED",
            actor_type="USER",
            actor_id=uid,
            target_id=submission.id,
            target_type="EKYC_SUBMISSION",
            ip_address=ip_address,
        )

        return {"submission_id": str(submission.id), "status": "PENDING"}

    async def get_status(self, user_id: str) -> dict:
        uid = uuid.UUID(user_id)
        submission = await self.ekyc_repo.get_latest_by_user(uid)
        if not submission:
            return {"status": "NOT_SUBMITTED"}
        return {
            "submission_id": str(submission.id),
            "status": submission.status,
            "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
            "reviewed_at": submission.reviewed_at.isoformat() if submission.reviewed_at else None,
        }
