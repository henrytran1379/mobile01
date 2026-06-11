import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from backend.models.wallet import UserWallet, WalletVerification
from backend.repositories.base import BaseRepository


class WalletRepository(BaseRepository[UserWallet]):
    def __init__(self, session: AsyncSession):
        super().__init__(UserWallet, session)

    async def get_by_user(self, user_id: uuid.UUID) -> list[UserWallet]:
        result = await self.session.execute(
            select(UserWallet).where(UserWallet.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_by_address(self, address: str, network: str) -> UserWallet | None:
        result = await self.session.execute(
            select(UserWallet).where(
                UserWallet.wallet_address == address,
                UserWallet.network == network,
            )
        )
        return result.scalar_one_or_none()

    async def address_exists(self, address: str, network: str) -> bool:
        return await self.get_by_address(address, network) is not None

    async def update_status(self, wallet_id: uuid.UUID, status: str, verified_at: datetime | None = None) -> None:
        values = {"status": status}
        if verified_at:
            values["verified_at"] = verified_at
        await self.session.execute(
            update(UserWallet).where(UserWallet.id == wallet_id).values(**values)
        )


class WalletVerificationRepository(BaseRepository[WalletVerification]):
    def __init__(self, session: AsyncSession):
        super().__init__(WalletVerification, session)

    async def get_by_wallet(self, wallet_id: uuid.UUID) -> list[WalletVerification]:
        result = await self.session.execute(
            select(WalletVerification).where(WalletVerification.wallet_id == wallet_id)
        )
        return list(result.scalars().all())

    async def get_pending_by_wallet(self, wallet_id: uuid.UUID) -> WalletVerification | None:
        result = await self.session.execute(
            select(WalletVerification).where(
                WalletVerification.wallet_id == wallet_id,
                WalletVerification.status == "PENDING",
            )
        )
        return result.scalar_one_or_none()
