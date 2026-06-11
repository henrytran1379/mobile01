import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column
from backend.core.database import Base
from backend.models.base import TimestampMixin, UUIDPrimaryKey


class UserWallet(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "user_wallets"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    network: Mapped[str] = mapped_column(String(50), nullable=False)
    wallet_address: Mapped[str] = mapped_column(String(255), nullable=False)
    wallet_type: Mapped[str] = mapped_column(String(50), nullable=False, default="PRIMARY")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_user_wallets_address", "wallet_address"),
    )


class WalletVerification(Base, UUIDPrimaryKey):
    __tablename__ = "wallet_verifications"

    wallet_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user_wallets.id"), nullable=False)
    verification_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    txid: Mapped[str | None] = mapped_column(String(255), nullable=True)
    amount: Mapped[float | None] = mapped_column(Numeric(38, 18), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class WalletType:
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    EXCHANGE = "EXCHANGE"
    COLD = "COLD"


class WalletStatus:
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class WalletNetwork:
    TRON = "TRON"
    BSC = "BSC"
