from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.database import get_db
from backend.schemas.auth import (
    RegisterRequest, LoginRequest, ChangePasswordRequest,
    TwoFASetupVerifyRequest, TwoFALoginRequest, TwoFADisableRequest,
    SuccessResponse, ErrorResponse,
)
from backend.services.auth_service import AuthService, AuthError
from backend.security.permissions import get_current_user_id

router = APIRouter(prefix="/auth", tags=["auth"])


def _auth_error_to_http(e: AuthError) -> HTTPException:
    status_map = {
        "EMAIL_EXISTS": 409,
        "INVALID_CREDENTIALS": 401,
        "ACCOUNT_DISABLED": 403,
        "ACCOUNT_LOCKED": 429,
        "INVALID_PASSWORD": 400,
        "INVALID_CODE": 400,
        "SETUP_EXPIRED": 400,
        "INVALID_TOKEN": 401,
        "2FA_NOT_CONFIGURED": 400,
        "USER_NOT_FOUND": 404,
    }
    code = status_map.get(e.code, 400)
    raise HTTPException(status_code=code, detail={"error_code": e.code, "message": e.message})


@router.post("/register", status_code=201)
async def register(body: RegisterRequest, request: Request, db: AsyncSession = Depends(get_db)):
    try:
        svc = AuthService(db)
        result = await svc.register(body.email, ip_address=request.client.host if request.client else None)
        return {"success": True, "message": "Registration email sent", "user_code": result["user_code"]}
    except AuthError as e:
        _auth_error_to_http(e)


@router.post("/login")
async def login(body: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    try:
        svc = AuthService(db)
        return await svc.login(body.email, body.password, ip_address=request.client.host if request.client else None)
    except AuthError as e:
        _auth_error_to_http(e)


@router.post("/change-password")
async def change_password(
    body: ChangePasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    try:
        svc = AuthService(db)
        return await svc.change_password(
            user_id, body.old_password, body.new_password,
            ip_address=request.client.host if request.client else None,
        )
    except AuthError as e:
        _auth_error_to_http(e)


@router.post("/2fa/setup")
async def setup_2fa(db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    svc = AuthService(db)
    return await svc.setup_2fa(user_id)


@router.post("/2fa/verify")
async def verify_2fa_setup(
    body: TwoFASetupVerifyRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    try:
        svc = AuthService(db)
        return await svc.verify_2fa_setup(
            user_id, body.code,
            ip_address=request.client.host if request.client else None,
        )
    except AuthError as e:
        _auth_error_to_http(e)


@router.post("/2fa/login")
async def login_with_2fa(body: TwoFALoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    try:
        svc = AuthService(db)
        return await svc.verify_2fa_login(
            body.pending_token, body.code,
            ip_address=request.client.host if request.client else None,
        )
    except AuthError as e:
        _auth_error_to_http(e)
