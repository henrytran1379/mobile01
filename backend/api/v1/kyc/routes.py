"""KYC API routes — full implementation."""
import asyncio
import logging
import os
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.config import settings
from backend.kyc import pipeline as kyc_pipeline
from backend.kyc import storage as kyc_storage
from backend.kyc.extractors.image_validator import validate_image, image_info
from backend.services.kyc_full_service import KYCFullService, KYCError
from backend.services.ekyc_service import EKYCService
from backend.services.kyc_vneid_service import save_confirmed, get_status as get_vneid_status
from backend.services.kycvneid2_service import upsert_session as upsert_kycvneid2, get_latest_session as get_kycvneid2_session
from backend.security.permissions import get_current_user_id, require_admin

logger = logging.getLogger(__name__)
router = APIRouter(tags=["kyc"])


# ── Helper ────────────────────────────────────────────────────────────────────

def _kyc_error(e: KYCError) -> HTTPException:
    code_map = {"NOT_FOUND": 404, "DUPLICATE_ID": 409}
    raise HTTPException(status_code=code_map.get(e.code, 400), detail={"error_code": e.code, "message": e.message})


# ── User: submit KYC ──────────────────────────────────────────────────────────

@router.post("/kyc/submit", status_code=201)
async def submit_kyc(
    request: Request,
    front: UploadFile = File(...),
    back: UploadFile = File(...),
    portrait: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    front_bytes    = await front.read()
    back_bytes     = await back.read()
    portrait_bytes = await portrait.read()

    for label, data in [("front", front_bytes), ("back", back_bytes), ("portrait", portrait_bytes)]:
        ok, err = validate_image(data)
        if not ok:
            raise HTTPException(status_code=422, detail={"error_code": "INVALID_IMAGE", "field": label, "message": err})

    tg_uid_header = request.headers.get("X-Telegram-User-Id")
    telegram_user_id = int(tg_uid_header) if tg_uid_header else 0
    storage_uid = telegram_user_id or int(user_id.replace("-", ""), 16) % (10**10)

    front_path    = kyc_storage.save_document(storage_uid, "FRONT", front_bytes)
    back_path     = kyc_storage.save_document(storage_uid, "BACK", back_bytes)
    portrait_path = kyc_storage.save_document(storage_uid, "PORTRAIT", portrait_bytes)

    front_inf    = image_info(front_bytes)
    back_inf     = image_info(back_bytes)
    portrait_inf = image_info(portrait_bytes)

    kyc_storage.save_metadata(telegram_user_id or 0, {
        "user_id": user_id,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    })

    # Pipeline chạy trong thread — không dùng face matching
    extraction = await asyncio.to_thread(
        kyc_pipeline.run_pipeline, front_bytes, back_bytes, portrait_bytes
    )

    svc = KYCFullService(db)
    try:
        result = await svc.submit(
            user_id_str=user_id,
            telegram_user_id=telegram_user_id,
            front_path=front_path,
            back_path=back_path,
            portrait_path=portrait_path,
            front_info=front_inf,
            back_info=back_inf,
            portrait_info=portrait_inf,
            extraction=extraction,
            ip_address=request.client.host if request.client else None,
        )
        return result
    except KYCError as e:
        _kyc_error(e)


@router.get("/kyc/status")
async def kyc_status(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    svc = KYCFullService(db)
    return await svc.get_status(user_id)


# ── Admin: queue ──────────────────────────────────────────────────────────────

@router.get("/kyc/admin/queue")
async def kyc_queue(
    db: AsyncSession = Depends(get_db),
    admin_payload: dict = Depends(require_admin),
):
    svc = KYCFullService(db)
    return {"queue": await svc.get_queue()}


@router.get("/kyc/admin/{kyc_profile_id}")
async def kyc_detail(
    kyc_profile_id: str,
    db: AsyncSession = Depends(get_db),
    admin_payload: dict = Depends(require_admin),
):
    svc = KYCFullService(db)
    try:
        return await svc.get_submission_detail(kyc_profile_id)
    except KYCError as e:
        _kyc_error(e)


@router.post("/kyc/admin/{kyc_profile_id}/approve")
async def kyc_approve(
    kyc_profile_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin_payload: dict = Depends(require_admin),
):
    admin_id = admin_payload["sub"]
    svc = KYCFullService(db)
    try:
        return await svc.approve(
            kyc_profile_id, admin_id,
            ip_address=request.client.host if request.client else None,
        )
    except KYCError as e:
        _kyc_error(e)


class RejectBody(BaseModel):
    reason: str


@router.post("/kyc/admin/{kyc_profile_id}/reject")
async def kyc_reject(
    kyc_profile_id: str,
    body: RejectBody,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin_payload: dict = Depends(require_admin),
):
    if not body.reason.strip():
        raise HTTPException(status_code=400, detail={"error_code": "REASON_REQUIRED", "message": "Rejection reason is required"})
    admin_id = admin_payload["sub"]
    svc = KYCFullService(db)
    try:
        return await svc.reject(
            kyc_profile_id, admin_id, body.reason.strip(),
            ip_address=request.client.host if request.client else None,
        )
    except KYCError as e:
        _kyc_error(e)


# ── eKYC (unchanged) ─────────────────────────────────────────────────────────

async def _save_upload(file: UploadFile, user_id: str, doc_type: str) -> str:
    content = await file.read()
    ext = os.path.splitext(file.filename or "file")[1] or ".bin"
    filename = f"{user_id}_{doc_type}_{datetime.now(timezone.utc).timestamp()}{ext}"
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    path = os.path.join(upload_dir, filename)
    with open(path, "wb") as f:
        f.write(content)
    return f"/uploads/{filename}"


@router.post("/ekyc/upload", status_code=201)
async def upload_ekyc(
    request: Request,
    pdf: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    if not (pdf.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files accepted")
    pdf_url = await _save_upload(pdf, user_id, "ekyc")
    svc = EKYCService(db)
    return await svc.upload_pdf(
        user_id, pdf_url,
        ip_address=request.client.host if request.client else None,
    )


@router.get("/ekyc/status")
async def ekyc_status(db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    svc = EKYCService(db)
    return await svc.get_status(user_id)


# ── KYC VNeID — Live Text flow ────────────────────────────────────────────────

class VNeIDSubmitBody(BaseModel):
    id_number:          str | None = None
    full_name:          str | None = None
    date_of_birth:      str | None = None
    gender:             str | None = None
    nationality:        str | None = None
    place_of_residence: str | None = None
    place_of_birth:     str | None = None
    issue_date:         str | None = None
    expiry_date:        str | None = None
    source:             str        = "iphone_live_text"
    kyc_method:         str        = "vneid_screenshot_plus_live_text"
    parse_status:       str | None = None
    missing_fields:     list[str]  = []
    kyc_session_id:     str        = ""
    screenshot_path:    str        = ""
    portrait_path:      str        = ""


@router.post("/kyc/vneid/submit", status_code=201)
async def submit_kyc_vneid(
    body: VNeIDSubmitBody,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Lưu KYC VNeID sau khi user xác nhận Live Text + ảnh."""
    from uuid import UUID
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id")

    result = await save_confirmed(
        db=db,
        user_id=uid,
        data=body.model_dump(),
        session_id=body.kyc_session_id,
        screenshot_path=body.screenshot_path,
        portrait_path=body.portrait_path,
    )
    return result


@router.get("/kyc/vneid/status")
async def kyc_vneid_status(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Lấy trạng thái KYC VNeID mới nhất của user."""
    from uuid import UUID
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id")

    status = await get_vneid_status(db, uid)
    if not status:
        return {"status": "NOT_SUBMITTED"}
    return status


# ── KYC VNeID v2 — Live Text + QR verify ─────────────────────────────────────

class KycVneid2Body(BaseModel):
    session_id:             str
    status:                 str
    verify_method:          str | None = None
    live_data:              dict | None = None
    qr_data:                dict | None = None
    mismatch_detail:        dict | None = None
    vneid_image_file_id:    str = ""
    vneid_image_path:       str = ""
    portrait_image_file_id: str = ""
    portrait_image_path:    str = ""
    portrait_uploaded:      bool = False
    verified_at:            str | None = None


@router.post("/kyc/vneid2/submit", status_code=201)
async def submit_kycvneid2(
    body: KycVneid2Body,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Tạo hoặc cập nhật phiên KYC VNeID v2."""
    from uuid import UUID
    from datetime import datetime
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id")

    verified_at = None
    if body.verified_at:
        try:
            verified_at = datetime.fromisoformat(body.verified_at)
        except Exception:
            pass

    return await upsert_kycvneid2(
        db,
        user_id=uid,
        session_id=body.session_id,
        status=body.status,
        verify_method=body.verify_method,
        live_data=body.live_data,
        qr_data=body.qr_data,
        mismatch_detail=body.mismatch_detail,
        vneid_image_file_id=body.vneid_image_file_id,
        vneid_image_path=body.vneid_image_path,
        portrait_image_file_id=body.portrait_image_file_id,
        portrait_image_path=body.portrait_image_path,
        portrait_uploaded=body.portrait_uploaded,
        verified_at=verified_at,
    )


@router.get("/kyc/vneid2/status")
async def kycvneid2_status(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Lấy phiên KYC VNeID v2 mới nhất."""
    from uuid import UUID
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id")

    session = await get_kycvneid2_session(db, uid)
    if not session:
        return {"status": "NOT_SUBMITTED"}
    return session
