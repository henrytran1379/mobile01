"""Full KYC business logic service."""
import hashlib
import uuid
import unicodedata
import logging
from datetime import datetime, date
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.kyc_v2 import KYCStatus, KYCLevel, DocType
from backend.repositories.kyc_v2_repository import (
    KYCProfileRepository, KYCDocumentRepository,
    KYCReviewQueueRepository, KYCAuditLogRepository, KYCEventRepository,
)
from backend.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

_REQUIRED_FIELDS = [
    "personal_id", "full_name", "date_of_birth", "gender", "nationality",
    "place_of_birth", "place_of_residence", "issue_date", "expiry_date",
]


class KYCError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class KYCFullService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.profile_repo = KYCProfileRepository(session)
        self.doc_repo = KYCDocumentRepository(session)
        self.queue_repo = KYCReviewQueueRepository(session)
        self.audit_repo = KYCAuditLogRepository(session)
        self.event_repo = KYCEventRepository(session)
        self.user_repo = UserRepository(session)

    # ── Submission ────────────────────────────────────────────────────────────

    async def submit(
        self,
        user_id_str: str,
        telegram_user_id: int,
        front_path: str,
        back_path: str,
        portrait_path: str,
        front_info: dict,
        back_info: dict,
        portrait_info: dict,
        extraction: "ExtractionResult",
        ip_address: Optional[str] = None,
    ) -> dict:
        uid = uuid.UUID(user_id_str)
        now = datetime.utcnow()

        # Duplicate ID check
        if extraction.personal_id:
            id_hash = _sha256(extraction.personal_id)
            dup = await self.profile_repo.get_by_personal_id_hash(id_hash)
            if dup and dup.user_id != uid and dup.status == KYCStatus.VERIFIED:
                raise KYCError("DUPLICATE_ID", "Số CCCD/CMND này đã được đăng ký bởi tài khoản khác.")

        # Xác định ownership
        ownership_status = await self._check_ownership(uid, extraction)

        # Xác định trạng thái KYC
        status = _determine_status(extraction)

        # Chuẩn hóa họ tên
        full_name_normalized = _normalize_name(extraction.full_name) if extraction.full_name else None

        # Upsert KYC profile
        profile = await self.profile_repo.upsert(
            uid,
            telegram_user_id=telegram_user_id,
            personal_id_hash=_sha256(extraction.personal_id) if extraction.personal_id else None,
            personal_id_encrypted=_simple_encrypt(extraction.personal_id) if extraction.personal_id else None,
            personal_id_masked=_mask_id(extraction.personal_id) if extraction.personal_id else None,
            full_name=extraction.full_name,
            full_name_normalized=full_name_normalized,
            date_of_birth=_parse_date(extraction.date_of_birth),
            gender=extraction.gender,
            nationality=extraction.nationality,
            place_of_birth=extraction.place_of_birth,
            place_of_residence=extraction.place_of_residence,
            address=extraction.place_of_residence,   # backward compat
            issue_date=_parse_date(extraction.issue_date),
            expiry_date=_parse_date(extraction.expiry_date),
            issuing_authority=extraction.issuing_authority,
            document_type=extraction.document_type,
            # Raw data
            qr_raw_data=extraction.qr_raw_data or None,
            mrz_line_1=extraction.mrz_line_1 or None,
            mrz_line_2=extraction.mrz_line_2 or None,
            mrz_line_3=extraction.mrz_line_3 or None,
            ocr_raw_text=extraction.ocr_raw_text[:5000] if extraction.ocr_raw_text else None,
            # Metadata
            ocr_success=extraction.ocr_success,
            qr_success=extraction.qr_success,
            mrz_success=extraction.mrz_success,
            ocr_confidence=extraction.ocr_confidence,
            qr_confidence=extraction.qr_confidence,
            mrz_confidence=extraction.mrz_confidence,
            extraction_source=extraction.extraction_source,
            verification_method=extraction.verification_method,
            # Status
            status=status,
            ownership_status=ownership_status,
            verification_level=KYCLevel.NONE,
            submitted_at=now,
        )

        # Lưu documents
        for doc_type, path, info in [
            (DocType.FRONT, front_path, front_info),
            (DocType.BACK, back_path, back_info),
            ("PORTRAIT", portrait_path, portrait_info),
        ]:
            await self.doc_repo.create(
                kyc_profile_id=profile.id,
                user_id=uid,
                doc_type=doc_type,
                file_path=path,
                file_hash=info.get("hash"),
                file_size=info.get("size"),
                width=info.get("width"),
                height=info.get("height"),
                uploaded_at=now,
            )

        # Queue cho admin review nếu đủ điều kiện
        if status in (KYCStatus.UNDER_REVIEW, KYCStatus.PENDING):
            existing_queue = await self.queue_repo.get_by_profile(profile.id)
            priority = 1 if not extraction.missing_fields else 0
            if existing_queue:
                from sqlalchemy import update as sa_update
                from backend.models.kyc_v2 import KYCReviewQueue
                await self.queue_repo.session.execute(
                    sa_update(KYCReviewQueue)
                    .where(KYCReviewQueue.kyc_profile_id == profile.id)
                    .values(status="PENDING", priority=priority, updated_at=now)
                )
            else:
                await self.queue_repo.create(
                    kyc_profile_id=profile.id,
                    user_id=uid,
                    priority=priority,
                    status="PENDING",
                    created_at=now,
                    updated_at=now,
                )

        await self.audit_repo.log(
            action="KYC_SUBMITTED",
            user_id=uid,
            kyc_profile_id=profile.id,
            new_value=status,
            ip_address=ip_address,
        )
        await self.event_repo.emit(
            "KYC_SUBMITTED",
            user_id=uid,
            kyc_profile_id=profile.id,
            payload={
                "status": status,
                "ownership_status": ownership_status,
                "extraction_source": extraction.extraction_source,
                "missing_fields": extraction.missing_fields,
            },
        )

        # Chuyển fields_meta sang dict serializable
        fields_meta_out = {}
        for fname, fv in (extraction.fields_meta or {}).items():
            fields_meta_out[fname] = {
                "value": fv.value if hasattr(fv, "value") else str(fv),
                "source": fv.source if hasattr(fv, "source") else "unknown",
                "confidence": fv.confidence if hasattr(fv, "confidence") else 1.0,
            }

        return {
            "submission_id": str(profile.id),
            "status": status,
            "ownership_status": ownership_status,
            "missing_fields": extraction.missing_fields,
            "extraction_source": extraction.extraction_source,
            "verification_method": extraction.verification_method,
            "fields_meta": fields_meta_out,
            "extracted": {
                "personal_id_masked": _mask_id(extraction.personal_id),
                "full_name": extraction.full_name,
                "date_of_birth": extraction.date_of_birth,
                "gender": extraction.gender,
                "nationality": extraction.nationality,
                "place_of_birth": extraction.place_of_birth,
                "place_of_residence": extraction.place_of_residence,
                "issue_date": extraction.issue_date,
                "expiry_date": extraction.expiry_date,
                "issuing_authority": extraction.issuing_authority,
                "document_type": extraction.document_type,
            },
        }

    # ── Ownership check ───────────────────────────────────────────────────────

    async def _check_ownership(self, uid: uuid.UUID, extraction: "ExtractionResult") -> str:
        """So khớp họ tên + ngày sinh với profile người dùng."""
        user = await self.user_repo.get_by_id(uid)
        if not user:
            return "unknown"

        # Lấy profile người dùng
        try:
            from backend.repositories.profile_repository import ProfileRepository
            profile_repo = ProfileRepository(self.session)
            profile = await profile_repo.get_by_user_id(uid)
        except Exception:
            profile = None

        if not profile:
            return "unknown"

        profile_name = getattr(profile, "full_name", None)
        profile_dob = getattr(profile, "date_of_birth", None)

        if not profile_name or not profile_dob:
            return "unknown"

        # Chuẩn hóa và so khớp
        norm_profile_name = _normalize_name(profile_name)
        norm_kyc_name = _normalize_name(extraction.full_name or "")
        profile_dob_str = _date_to_str(profile_dob)
        kyc_dob_str = _parse_dob_to_ymd(extraction.date_of_birth or "")

        name_match = norm_profile_name == norm_kyc_name
        dob_match = profile_dob_str == kyc_dob_str

        if name_match and dob_match:
            return "self"
        return "not_self"

    # ── Status ────────────────────────────────────────────────────────────────

    async def get_status(self, user_id_str: str) -> dict:
        uid = uuid.UUID(user_id_str)
        profile = await self.profile_repo.get_by_user_id(uid)
        if not profile:
            return {"status": "NOT_SUBMITTED", "verification_level": 0}
        return {
            "status": profile.status,
            "ownership_status": profile.ownership_status,
            "verification_level": profile.verification_level,
            "full_name": profile.full_name,
            "personal_id_masked": profile.personal_id_masked,
            "submitted_at": profile.submitted_at.isoformat() if profile.submitted_at else None,
            "reviewed_at": profile.reviewed_at.isoformat() if profile.reviewed_at else None,
            "reject_reason": profile.reject_reason,
        }

    # ── Admin: queue ──────────────────────────────────────────────────────────

    async def get_queue(self, limit: int = 20) -> list[dict]:
        items = await self.queue_repo.get_pending(limit=limit)
        result = []
        for item in items:
            profile = await self.profile_repo.get_by_id(item.kyc_profile_id)
            user = await self.user_repo.get_by_id(item.user_id)
            result.append({
                "queue_id": str(item.id),
                "kyc_profile_id": str(item.kyc_profile_id),
                "user_id": str(item.user_id),
                "user_code": user.user_code if user else None,
                "telegram_user_id": profile.telegram_user_id if profile else None,
                "full_name": profile.full_name if profile else None,
                "status": profile.status if profile else None,
                "ownership_status": profile.ownership_status if profile else None,
                "extraction_source": profile.extraction_source if profile else None,
                "submitted_at": profile.submitted_at.isoformat() if profile and profile.submitted_at else None,
                "priority": item.priority,
            })
        return result

    async def get_submission_detail(self, kyc_profile_id_str: str) -> dict:
        pid = uuid.UUID(kyc_profile_id_str)
        profile = await self.profile_repo.get_by_id(pid)
        if not profile:
            raise KYCError("NOT_FOUND", "KYC submission not found")
        docs = await self.doc_repo.list_by_profile(pid)
        return {
            "kyc_profile_id": str(profile.id),
            "user_id": str(profile.user_id),
            "telegram_user_id": profile.telegram_user_id,
            "status": profile.status,
            "ownership_status": profile.ownership_status,
            "identity": {
                "personal_id_masked": profile.personal_id_masked,
                "full_name": profile.full_name,
                "full_name_normalized": profile.full_name_normalized,
                "date_of_birth": str(profile.date_of_birth) if profile.date_of_birth else None,
                "gender": profile.gender,
                "nationality": profile.nationality,
                "place_of_birth": profile.place_of_birth,
                "place_of_residence": profile.place_of_residence,
                "issue_date": str(profile.issue_date) if profile.issue_date else None,
                "expiry_date": str(profile.expiry_date) if profile.expiry_date else None,
                "document_type": profile.document_type,
                "issuing_authority": profile.issuing_authority,
            },
            "documents": [
                {"doc_type": d.doc_type, "file_path": d.file_path,
                 "uploaded_at": d.uploaded_at.isoformat()}
                for d in docs
            ],
            "raw_data": {
                "qr_raw_data": profile.qr_raw_data,
                "mrz_line_1": profile.mrz_line_1,
                "mrz_line_2": profile.mrz_line_2,
                "mrz_line_3": profile.mrz_line_3,
            },
            "metadata": {
                "ocr_success": profile.ocr_success,
                "qr_success": profile.qr_success,
                "mrz_success": profile.mrz_success,
                "ocr_confidence": profile.ocr_confidence,
                "qr_confidence": profile.qr_confidence,
                "mrz_confidence": profile.mrz_confidence,
                "extraction_source": profile.extraction_source,
                "verification_method": profile.verification_method,
                "submitted_at": profile.submitted_at.isoformat() if profile.submitted_at else None,
            },
        }

    # ── Admin: approve / reject ───────────────────────────────────────────────

    async def approve(self, kyc_profile_id_str: str, admin_user_id_str: str,
                      ip_address: Optional[str] = None) -> dict:
        pid = uuid.UUID(kyc_profile_id_str)
        admin_uid = uuid.UUID(admin_user_id_str)

        profile = await self.profile_repo.get_by_id(pid)
        if not profile:
            raise KYCError("NOT_FOUND", "KYC submission not found")

        old_status = profile.status
        await self.profile_repo.set_status(
            pid, KYCStatus.VERIFIED,
            verification_level=KYCLevel.MANUAL_APPROVED,
            reviewed_by=admin_uid,
            reviewed_at=datetime.utcnow(),
            reject_reason=None,
        )
        await self.queue_repo.mark_done(pid)
        await self.audit_repo.log(
            action="KYC_APPROVED", user_id=profile.user_id, actor_id=admin_uid,
            kyc_profile_id=pid, old_value=old_status, new_value=KYCStatus.VERIFIED,
            ip_address=ip_address,
        )
        await self.event_repo.emit("KYC_APPROVED", user_id=profile.user_id, kyc_profile_id=pid,
                                   payload={"admin_id": str(admin_uid)})
        return {"success": True, "user_id": str(profile.user_id),
                "telegram_user_id": profile.telegram_user_id}

    async def reject(self, kyc_profile_id_str: str, admin_user_id_str: str,
                     reason: str, ip_address: Optional[str] = None) -> dict:
        pid = uuid.UUID(kyc_profile_id_str)
        admin_uid = uuid.UUID(admin_user_id_str)

        profile = await self.profile_repo.get_by_id(pid)
        if not profile:
            raise KYCError("NOT_FOUND", "KYC submission not found")

        old_status = profile.status
        await self.profile_repo.set_status(
            pid, KYCStatus.REJECTED,
            reviewed_by=admin_uid,
            reviewed_at=datetime.utcnow(),
            reject_reason=reason,
        )
        await self.queue_repo.mark_done(pid)
        await self.audit_repo.log(
            action="KYC_REJECTED", user_id=profile.user_id, actor_id=admin_uid,
            kyc_profile_id=pid, old_value=old_status, new_value=KYCStatus.REJECTED,
            reason=reason, ip_address=ip_address,
        )
        await self.event_repo.emit("KYC_REJECTED", user_id=profile.user_id, kyc_profile_id=pid,
                                   payload={"admin_id": str(admin_uid), "reason": reason})
        return {"success": True, "user_id": str(profile.user_id),
                "telegram_user_id": profile.telegram_user_id, "reason": reason}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _mask_id(personal_id: Optional[str]) -> Optional[str]:
    if not personal_id:
        return None
    visible = min(6, len(personal_id))
    return personal_id[:visible] + "*" * (len(personal_id) - visible)


def _simple_encrypt(value: str) -> str:
    import base64
    return base64.b64encode(value.encode()).decode()


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    from datetime import datetime as dt
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y"):
        try:
            return dt.strptime(value.strip(), fmt).date()
        except (ValueError, AttributeError):
            continue
    return None


def _date_to_str(d) -> str:
    """Chuyển date object → YYYY-MM-DD string."""
    if d is None:
        return ""
    if isinstance(d, date):
        return d.strftime("%Y-%m-%d")
    return str(d)[:10]


def _parse_dob_to_ymd(dob_str: str) -> str:
    """Chuyển DD/MM/YYYY → YYYY-MM-DD."""
    if not dob_str:
        return ""
    import re
    m = re.match(r"(\d{2})[/\-\.](\d{2})[/\-\.](\d{4})", dob_str.strip())
    if m:
        dd, mm, yyyy = m.groups()
        return f"{yyyy}-{mm}-{dd}"
    return dob_str.strip()


def _normalize_name(name: str) -> str:
    """Bỏ dấu tiếng Việt, viết hoa, bỏ khoảng trắng thừa."""
    if not name:
        return ""
    # NFD decomposition → loại bỏ combining marks
    nfd = unicodedata.normalize("NFD", name)
    ascii_name = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    return " ".join(ascii_name.upper().split())


def _determine_status(extraction: "ExtractionResult") -> str:
    if extraction.missing_fields:
        return KYCStatus.NEED_REUPLOAD
    return KYCStatus.UNDER_REVIEW
