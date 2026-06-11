import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from backend.repositories.kyc_repository import VerificationReviewRepository
from backend.repositories.admin_repository import AdminUserRepository, ReviewQueueRepository
from backend.repositories.user_repository import UserRepository
from backend.repositories.audit_repository import AuditLogRepository
from backend.repositories.credit_repository import CreditAccountRepository, CreditLedgerRepository
from backend.models.kyc import ReviewType
from backend.models.credit import LedgerType


class AdminService:
    def __init__(self, session: AsyncSession):
        self.review_repo = VerificationReviewRepository(session)
        self.admin_repo = AdminUserRepository(session)
        self.queue_repo = ReviewQueueRepository(session)
        self.user_repo = UserRepository(session)
        self.audit_repo = AuditLogRepository(session)
        self.credit_account_repo = CreditAccountRepository(session)
        self.credit_ledger_repo = CreditLedgerRepository(session)

    async def get_pending_reviews(self, review_type: str | None = None) -> list[dict]:
        reviews = await self.review_repo.get_pending(review_type)
        return [
            {
                "review_id": str(r.id),
                "user_id": str(r.user_id),
                "review_type": r.review_type,
                "status": r.review_status,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in reviews
        ]

    async def approve_review(self, review_id: str, admin_user_id: str, ip_address: str | None = None) -> dict:
        rid = uuid.UUID(review_id)
        aid = uuid.UUID(admin_user_id)

        await self.review_repo.approve(rid, aid)

        review = await self.review_repo.get_by_id(rid)
        await self.audit_repo.log(
            action="REVIEW_APPROVED",
            actor_type="ADMIN",
            actor_id=aid,
            target_id=rid,
            target_type="VERIFICATION_REVIEW",
            ip_address=ip_address,
            metadata={"review_type": review.review_type if review else None},
        )
        return {"success": True}

    async def reject_review(
        self, review_id: str, admin_user_id: str, reason: str, ip_address: str | None = None
    ) -> dict:
        rid = uuid.UUID(review_id)
        aid = uuid.UUID(admin_user_id)

        await self.review_repo.reject(rid, aid, reason)

        await self.audit_repo.log(
            action="REVIEW_REJECTED",
            actor_type="ADMIN",
            actor_id=aid,
            target_id=rid,
            target_type="VERIFICATION_REVIEW",
            reason=reason,
            ip_address=ip_address,
        )
        return {"success": True}

    async def adjust_credits(
        self,
        target_user_id: str,
        admin_user_id: str,
        amount: int,
        reason: str,
        ip_address: str | None = None,
    ) -> dict:
        uid = uuid.UUID(target_user_id)
        aid = uuid.UUID(admin_user_id)

        account = await self.credit_account_repo.get_or_create(uid)
        new_balance = account.balance + amount
        if new_balance < 0:
            raise ValueError("Adjustment would result in negative balance")

        await self.credit_account_repo.adjust_balance(uid, amount)
        await self.credit_ledger_repo.record(
            user_id=uid,
            ledger_type=LedgerType.ADMIN_ADJUSTMENT,
            amount=amount,
            balance_before=account.balance,
            balance_after=new_balance,
            description=reason,
        )

        await self.audit_repo.log(
            action="ADMIN_CREDIT_ADJUSTMENT",
            actor_type="ADMIN",
            actor_id=aid,
            target_id=uid,
            target_type="USER",
            reason=reason,
            metadata={"amount": amount, "new_balance": new_balance},
            ip_address=ip_address,
        )
        return {"new_balance": new_balance}
