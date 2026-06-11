import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from backend.repositories.wallet_repository import WalletRepository, WalletVerificationRepository
from backend.repositories.kyc_repository import VerificationReviewRepository
from backend.repositories.audit_repository import AuditLogRepository
from backend.models.wallet import WalletNetwork, WalletStatus
from backend.models.kyc import ReviewType


class WalletService:
    def __init__(self, session: AsyncSession):
        self.wallet_repo = WalletRepository(session)
        self.verification_repo = WalletVerificationRepository(session)
        self.review_repo = VerificationReviewRepository(session)
        self.audit_repo = AuditLogRepository(session)

    VERIFICATION_AMOUNTS = {
        WalletNetwork.TRON: 50,
        WalletNetwork.BSC: 0.01,
    }

    async def add_wallet(
        self, user_id: str, network: str, address: str, wallet_type: str = "PRIMARY", ip_address: str | None = None
    ) -> dict:
        if network not in (WalletNetwork.TRON, WalletNetwork.BSC):
            raise ValueError(f"Unsupported network: {network}")

        uid = uuid.UUID(user_id)

        if await self.wallet_repo.address_exists(address, network):
            raise ValueError("Wallet address already registered")

        wallet = await self.wallet_repo.create(
            user_id=uid,
            network=network,
            wallet_address=address,
            wallet_type=wallet_type,
            status=WalletStatus.PENDING,
        )

        now = datetime.now(timezone.utc)
        verification_amount = self.VERIFICATION_AMOUNTS[network]
        await self.verification_repo.create(
            wallet_id=wallet.id,
            status="PENDING",
            created_at=now,
        )

        await self.review_repo.create(
            user_id=uid,
            review_type=ReviewType.WALLET,
            review_status="PENDING",
            created_at=now,
        )

        await self.audit_repo.log(
            action="WALLET_ADDED",
            actor_type="USER",
            actor_id=uid,
            target_id=wallet.id,
            target_type="WALLET",
            ip_address=ip_address,
            metadata={"network": network, "address": address},
        )

        return {
            "wallet_id": str(wallet.id),
            "network": network,
            "address": address,
            "status": WalletStatus.PENDING,
            "verification_amount": verification_amount,
        }

    async def list_wallets(self, user_id: str) -> list[dict]:
        uid = uuid.UUID(user_id)
        wallets = await self.wallet_repo.get_by_user(uid)
        return [
            {
                "wallet_id": str(w.id),
                "network": w.network,
                "address": w.wallet_address,
                "type": w.wallet_type,
                "status": w.status,
                "verified_at": w.verified_at.isoformat() if w.verified_at else None,
            }
            for w in wallets
        ]

    async def get_wallet(self, wallet_id: str) -> dict:
        wid = uuid.UUID(wallet_id)
        wallet = await self.wallet_repo.get_by_id(wid)
        if not wallet:
            raise ValueError("Wallet not found")
        return {
            "wallet_id": str(wallet.id),
            "network": wallet.network,
            "address": wallet.wallet_address,
            "type": wallet.wallet_type,
            "status": wallet.status,
            "verified_at": wallet.verified_at.isoformat() if wallet.verified_at else None,
        }

    async def request_verification(self, user_id: str, wallet_id: str, ip_address: str | None = None) -> dict:
        uid = uuid.UUID(user_id)
        wid = uuid.UUID(wallet_id)
        wallet = await self.wallet_repo.get_by_id(wid)
        if not wallet or str(wallet.user_id) != user_id:
            raise ValueError("Wallet not found")

        now = datetime.now(timezone.utc)
        verification_amount = self.VERIFICATION_AMOUNTS.get(wallet.network, 0)

        await self.audit_repo.log(
            action="WALLET_VERIFICATION_REQUESTED",
            actor_type="USER",
            actor_id=uid,
            target_id=wid,
            target_type="WALLET",
            ip_address=ip_address,
        )

        return {
            "wallet_id": wallet_id,
            "network": wallet.network,
            "verification_amount": verification_amount,
            "status": "VERIFICATION_PENDING",
        }
