import uuid
from datetime import date, datetime
from sqlalchemy import String, BigInteger, Integer, Float, Boolean, Date, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from backend.core.database import Base
from backend.models.base import TimestampMixin, UUIDPrimaryKey


class KYCProfile(Base, UUIDPrimaryKey, TimestampMixin):
    __tablename__ = "kyc_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    telegram_user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    personal_id_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    personal_id_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    personal_id_masked: Mapped[str | None] = mapped_column(String(20), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(10), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(100), nullable=True)
    verification_level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING")
    reject_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    face_match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    extraction_source: Mapped[str | None] = mapped_column(String(20), nullable=True)
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Extended CCCD fields (migration 004)
    place_of_birth: Mapped[str | None] = mapped_column(Text, nullable=True)
    place_of_residence: Mapped[str | None] = mapped_column(Text, nullable=True)
    issuing_authority: Mapped[str | None] = mapped_column(String(255), nullable=True)
    document_type: Mapped[str | None] = mapped_column(String(20), nullable=True, default="CCCD")
    full_name_normalized: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Raw extraction data
    qr_raw_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    mrz_line_1: Mapped[str | None] = mapped_column(Text, nullable=True)
    mrz_line_2: Mapped[str | None] = mapped_column(Text, nullable=True)
    mrz_line_3: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Extraction metadata
    ocr_success: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    qr_success: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    mrz_success: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    ocr_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    qr_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    mrz_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    verification_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ownership_status: Mapped[str | None] = mapped_column(String(20), nullable=True, default="unknown")

    __table_args__ = (
        Index("ix_kyc_profiles_user_id", "user_id"),
        Index("ix_kyc_profiles_status", "status"),
        Index("ix_kyc_profiles_personal_id_hash", "personal_id_hash"),
    )


class KYCDocument(Base, UUIDPrimaryKey):
    __tablename__ = "kyc_documents"

    kyc_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("kyc_profiles.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(30), nullable=False)   # FRONT / BACK / SELFIE
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(nullable=False)

    __table_args__ = (Index("ix_kyc_documents_kyc_profile_id", "kyc_profile_id"),)


class KYCFaceMatch(Base, UUIDPrimaryKey):
    __tablename__ = "kyc_face_match"

    kyc_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("kyc_profiles.id"), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    result: Mapped[str] = mapped_column(String(10), nullable=False)    # PASS / REVIEW / FAIL
    algorithm: Mapped[str] = mapped_column(String(50), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False)


class KYCReviewQueue(Base, UUIDPrimaryKey):
    __tablename__ = "kyc_review_queue"

    kyc_profile_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("kyc_profiles.id"), unique=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDING")
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False)

    __table_args__ = (
        Index("ix_kyc_review_queue_status", "status"),
        Index("ix_kyc_review_queue_priority", "priority"),
    )


class KYCAuditLog(Base, UUIDPrimaryKey):
    __tablename__ = "kyc_audit_logs"

    kyc_profile_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("kyc_profiles.id"), nullable=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(60), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False)

    __table_args__ = (
        Index("ix_kyc_audit_logs_user_id", "user_id"),
        Index("ix_kyc_audit_logs_action", "action"),
    )


class KYCEvent(Base, UUIDPrimaryKey):
    __tablename__ = "kyc_events"

    kyc_profile_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("kyc_profiles.id"), nullable=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    event_type: Mapped[str] = mapped_column(String(60), nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False)

    __table_args__ = (
        Index("ix_kyc_events_user_id", "user_id"),
        Index("ix_kyc_events_event_type", "event_type"),
    )


# ── Status / Level constants ──────────────────────────────────────────────────

class KYCStatus:
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    NEED_REUPLOAD = "NEED_REUPLOAD"
    UNDER_REVIEW = "UNDER_REVIEW"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class KYCLevel:
    NONE = 0
    PHONE = 1
    IDENTITY = 2
    MANUAL_APPROVED = 3
    TRUSTED = 4


class DocType:
    FRONT = "FRONT"
    BACK = "BACK"
    SELFIE = "SELFIE"


class FaceMatchResult:
    PASS = "PASS"
    REVIEW = "REVIEW"
    FAIL = "FAIL"
