from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.services.credit_service import CreditService
from backend.security.permissions import get_current_user_id

router = APIRouter(prefix="/credits", tags=["credits"])


@router.get("/balance")
async def get_balance(db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    svc = CreditService(db)
    return await svc.get_balance(user_id)


@router.get("/ledger")
async def get_ledger(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    svc = CreditService(db)
    return await svc.get_ledger(user_id, limit=limit, offset=offset)
