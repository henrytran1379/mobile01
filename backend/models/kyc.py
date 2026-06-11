import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.core.database import Base
from backend.models.base import UUIDPrimaryKey


class KYCSubmission(Base, UUIDPrimaryKey):
    __tablename__ = "kyc_submissions"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    front_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    back_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    selfie_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class EKYCSubmission(Base, UUIDPrimaryKey):
    __tablename__ = "ekyc_submissions"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    provider_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    provider_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pdf_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class VerificationReview(Base, UUIDPrimaryKey):
    __tablename__ = "verification_reviews"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    review_type: Mapped[str] = mapped_column(String(50), nullable=False)
    review_status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    admin_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class UserDocument(Base, UUIDPrimaryKey):
    __tablename__ = "user_documents"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    file_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_encrypted: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ReviewStatus:
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ReviewType:
    KYC = "KYC"
    EKYC = "EKYC"
    WALLET = "WALLET"


class DocumentType:
    CCCD_FRONT = "CCCD_FRONT"
    CCCD_BACK = "CCCD_BACK"
    SELFIE = "SELFIE"
    EKYC_PDF = "EKYC_PDF"
