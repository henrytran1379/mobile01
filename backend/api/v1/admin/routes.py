from fastapi import APIRouter, Depends, Request, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.services.admin_service import AdminService
from backend.security.permissions import require_admin
from backend.schemas.admin import ReviewActionRequest, CreditAdjustRequest

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/reviews")
async def get_reviews(
    review_type: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    admin_payload: dict = Depends(require_admin),
):
    svc = AdminService(db)
    return await svc.get_pending_reviews(review_type)


@router.post("/reviews/{review_id}/approve")
async def approve_review(
    review_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin_payload: dict = Depends(require_admin),
):
    svc = AdminService(db)
    return await svc.approve_review(
        review_id, admin_payload["sub"],
        ip_address=request.client.host if request.client else None,
    )


@router.post("/reviews/{review_id}/reject")
async def reject_review(
    review_id: str,
    body: ReviewActionRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin_payload: dict = Depends(require_admin),
):
    if not body.reason:
        raise HTTPException(status_code=400, detail="Reason is required for rejection")
    svc = AdminService(db)
    return await svc.reject_review(
        review_id, admin_payload["sub"], body.reason,
        ip_address=request.client.host if request.client else None,
    )


@router.post("/credits/adjust")
async def adjust_credits(
    body: CreditAdjustRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin_payload: dict = Depends(require_admin),
):
    try:
        svc = AdminService(db)
        return await svc.adjust_credits(
            body.user_id, admin_payload["sub"], body.amount, body.reason,
            ip_address=request.client.host if request.client else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
