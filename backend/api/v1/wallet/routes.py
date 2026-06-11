from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.services.wallet_service import WalletService
from backend.security.permissions import get_current_user_id
from backend.schemas.wallet import AddWalletRequest, WalletVerifyRequest

router = APIRouter(prefix="/wallets", tags=["wallets"])


@router.post("", status_code=201)
async def add_wallet(
    body: AddWalletRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    try:
        svc = WalletService(db)
        return await svc.add_wallet(
            user_id, body.network, body.address, body.wallet_type,
            ip_address=request.client.host if request.client else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
async def list_wallets(db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    svc = WalletService(db)
    return await svc.list_wallets(user_id)


@router.get("/{wallet_id}")
async def get_wallet(wallet_id: str, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    try:
        svc = WalletService(db)
        return await svc.get_wallet(wallet_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{wallet_id}/verify")
async def request_verification(
    wallet_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    try:
        svc = WalletService(db)
        return await svc.request_verification(
            user_id, wallet_id,
            ip_address=request.client.host if request.client else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
