from fastapi import APIRouter, Depends, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.services.profile_service import ProfileService
from backend.security.permissions import get_current_user_id
from backend.schemas.profile import ProfileUpdateRequest

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("")
async def get_profile(db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    svc = ProfileService(db)
    return await svc.get_profile(user_id)


@router.put("")
async def update_profile(
    body: ProfileUpdateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    svc = ProfileService(db)
    return await svc.update_profile(
        user_id, body.model_dump(exclude_none=True),
        ip_address=request.client.host if request.client else None,
    )
