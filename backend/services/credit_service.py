import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from backend.repositories.credit_repository import CreditAccountRepository, CreditLedgerRepository
from backend.repositories.audit_repository import AuditLogRepository
from backend.models.credit import LedgerType


class CreditService:
    def __init__(self, session: AsyncSession):
        self.account_repo = CreditAccountRepository(session)
        self.ledger_repo = CreditLedgerRepository(session)
        self.audit_repo = AuditLogRepository(session)

    async def get_balance(self, user_id: str) -> dict:
        uid = uuid.UUID(user_id)
        account = await self.account_repo.get_or_create(uid)
        return {
            "balance": account.balance,
            "total_earned": account.total_earned,
            "total_spent": account.total_spent,
        }

    async def get_ledger(self, user_id: str, limit: int = 50, offset: int = 0) -> list[dict]:
        uid = uuid.UUID(user_id)
        entries = await self.ledger_repo.get_by_user(uid, limit=limit, offset=offset)
        return [
            {
                "id": str(e.id),
                "type": e.ledger_type,
                "amount": e.amount,
                "balance_before": e.balance_before,
                "balance_after": e.balance_after,
                "description": e.description,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in entries
        ]

    async def issue_credits(
        self,
        user_id: str,
        amount: int,
        ledger_type: str,
        reference_id: uuid.UUID | None = None,
        description: str | None = None,
        admin_id: str | None = None,
        ip_address: str | None = None,
    ) -> dict:
        uid = uuid.UUID(user_id)
        account = await self.account_repo.get_or_create(uid)
        balance_before = account.balance

        await self.account_repo.adjust_balance(uid, amount)

        await self.ledger_repo.record(
            user_id=uid,
            ledger_type=ledger_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_before + amount,
            reference_id=reference_id,
            description=description,
        )

        actor_id = uuid.UUID(admin_id) if admin_id else uid
        await self.audit_repo.log(
            action="CREDITS_ISSUED",
            actor_type="ADMIN" if admin_id else "SYSTEM",
            actor_id=actor_id,
            target_id=uid,
            target_type="USER",
            metadata={"amount": amount, "type": ledger_type},
            ip_address=ip_address,
        )
        return {"new_balance": balance_before + amount}

    async def consume_credits(
        self,
        user_id: str,
        amount: int,
        ledger_type: str,
        reference_id: uuid.UUID | None = None,
        description: str | None = None,
    ) -> dict:
        uid = uuid.UUID(user_id)
        account = await self.account_repo.get_or_create(uid)
        if account.balance < amount:
            raise ValueError("Insufficient credits")
        balance_before = account.balance

        await self.account_repo.adjust_balance(uid, -amount)

        await self.ledger_repo.record(
            user_id=uid,
            ledger_type=ledger_type,
            amount=-amount,
            balance_before=balance_before,
            balance_after=balance_before - amount,
            reference_id=reference_id,
            description=description,
        )
        return {"new_balance": balance_before - amount}
