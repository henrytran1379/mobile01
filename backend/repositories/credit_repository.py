import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from backend.models.credit import CreditAccount, CreditLedger
from backend.repositories.base import BaseRepository


class CreditAccountRepository(BaseRepository[CreditAccount]):
    def __init__(self, session: AsyncSession):
        super().__init__(CreditAccount, session)

    async def get_by_user(self, user_id: uuid.UUID) -> CreditAccount | None:
        result = await self.session.execute(
            select(CreditAccount).where(CreditAccount.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create(self, user_id: uuid.UUID) -> CreditAccount:
        account = await self.get_by_user(user_id)
        if not account:
            account = await self.create(user_id=user_id, balance=0, total_earned=0, total_spent=0)
        return account

    async def adjust_balance(self, user_id: uuid.UUID, delta: int) -> CreditAccount:
        account = await self.get_or_create(user_id)
        new_balance = account.balance + delta
        if new_balance < 0:
            raise ValueError("Insufficient credits")
        values = {"balance": new_balance}
        if delta > 0:
            values["total_earned"] = account.total_earned + delta
        else:
            values["total_spent"] = account.total_spent + abs(delta)
        await self.session.execute(
            update(CreditAccount).where(CreditAccount.user_id == user_id).values(**values)
        )
        account.balance = new_balance
        return account


class CreditLedgerRepository(BaseRepository[CreditLedger]):
    def __init__(self, session: AsyncSession):
        super().__init__(CreditLedger, session)

    async def get_by_user(self, user_id: uuid.UUID, limit: int = 50, offset: int = 0) -> list[CreditLedger]:
        result = await self.session.execute(
            select(CreditLedger)
            .where(CreditLedger.user_id == user_id)
            .order_by(CreditLedger.created_at.desc())
            .limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def record(
        self,
        user_id: uuid.UUID,
        ledger_type: str,
        amount: int,
        balance_before: int,
        balance_after: int,
        reference_id: uuid.UUID | None = None,
        description: str | None = None,
    ) -> CreditLedger:
        return await self.create(
            user_id=user_id,
            ledger_type=ledger_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            reference_id=reference_id,
            description=description,
            created_at=datetime.now(timezone.utc),
        )
