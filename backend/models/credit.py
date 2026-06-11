import uuid
from datetime import datetime
from sqlalchemy import String, BigInteger, ForeignKey, DateTime, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from backend.core.database import Base
from backend.models.base import TimestampMixin, UUIDPrimaryKey


class CreditAccount(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "credit_accounts"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    balance: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    total_earned: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    total_spent: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)


class CreditLedger(Base, UUIDPrimaryKey):
    __tablename__ = "credit_ledger"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    ledger_type: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    balance_before: Mapped[int] = mapped_column(BigInteger, nullable=False)
    balance_after: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reference_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("ix_credit_ledger_user_id", "user_id"),
    )


class LedgerType:
    TRX_TOPUP = "TRX_TOPUP"
    BNB_TOPUP = "BNB_TOPUP"
    WALLET_VERIFICATION = "WALLET_VERIFICATION"
    CHECK_WALLET = "CHECK_WALLET"
    CHECK_USER = "CHECK_USER"
    ADMIN_ADJUSTMENT = "ADMIN_ADJUSTMENT"
