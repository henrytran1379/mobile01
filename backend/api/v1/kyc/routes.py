import os
import hashlib
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.core.config import settings
from backend.services.kyc_service import KYCService
from backend.services.ekyc_service import EKYCService
from backend.security.permissions import get_current_user_id
from backend.schemas.ekyc import EKYCResultRequest

router = APIRouter(tags=["kyc"])


async def save_upload(file: UploadFile, user_id: str, doc_type: str) -> str:
    content = await file.read()
    ext = os.path.splitext(file.filename or "file")[1] or ".bin"
    filename = f"{user_id}_{doc_type}_{datetime.now(timezone.utc).timestamp()}{ext}"
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    path = os.path.join(upload_dir, filename)
    with open(path, "wb") as f:
        f.write(content)
    return f"/uploads/{filename}"


@router.post("/kyc/submit", status_code=201)
async def submit_kyc(
    request: Request,
    front: UploadFile = File(...),
    back: UploadFile = File(...),
    selfie: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    front_url = await save_upload(front, user_id, "front")
    back_url = await save_upload(back, user_id, "back")
    selfie_url = await save_upload(selfie, user_id, "selfie")

    svc = KYCService(db)
    return await svc.submit_kyc(
        user_id, front_url, back_url, selfie_url,
        ip_address=request.client.host if request.client else None,
    )


@router.get("/kyc/status")
async def kyc_status(db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    svc = KYCService(db)
    return await svc.get_status(user_id)


EKYC_ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp"}


@router.post("/ekyc/upload", status_code=201)
async def upload_ekyc(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in EKYC_ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed: {', '.join(sorted(EKYC_ALLOWED_EXTENSIONS))}",
        )

    file_url = await save_upload(file, user_id, "ekyc")
    svc = EKYCService(db)
    return await svc.upload_pdf(
        user_id, file_url,
        ip_address=request.client.host if request.client else None,
    )


@router.get("/ekyc/status")
async def ekyc_status(db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    svc = EKYCService(db)
    return await svc.get_status(user_id)


@router.post("/ekyc/submit-result", status_code=201)
async def submit_ekyc_result(
    body: EKYCResultRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    svc = EKYCService(db)
    return await svc.save_result(
        user_id, body,
        ip_address=request.client.host if request.client else None,
    )
