import logging
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from backend.core.database import get_db
from backend.schemas.auth import (
    RegisterRequest, LoginRequest, ChangePasswordRequest,
    TwoFASetupVerifyRequest, TwoFALoginRequest, TwoFADisableRequest,
    SuccessResponse, ErrorResponse,
)
from backend.services.auth_service import AuthService, AuthError
from backend.security.permissions import get_current_user_id
from backend.integrations.smtp.sender import send_registration_email, send_resend_verification_email

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


def _auth_error_to_http(e: AuthError) -> HTTPException:
    status_map = {
        "EMAIL_REGISTERED": 409,
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

        is_resend = result.get("resent", False)
        sender = send_resend_verification_email if is_resend else send_registration_email
        email_ok = await sender(body.email, result["user_code"], result["temp_password"])
        logger.info("register email_sent=%s resent=%s to=%s", email_ok, is_resend, body.email)

        if is_resend:
            msg = "Email already registered but not verified. A new verification email has been sent."
            return_status = 200
        else:
            msg = "Registration successful. Please check your email for login credentials."
            return_status = 201

        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=return_status,
            content={"success": True, "message": msg, "email_sent": email_ok},
        )
    except AuthError as e:
        _auth_error_to_http(e)


class ResendRequest(BaseModel):
    email: EmailStr


@router.post("/resend-verification-email")
async def resend_verification(body: ResendRequest, request: Request, db: AsyncSession = Depends(get_db)):
    svc = AuthService(db)
    # _resend_credentials gửi email bên trong service nếu user tồn tại và chưa verified
    user = await svc.user_repo.get_by_email(body.email)
    from backend.models.user import UserStatus
    if user and user.status in UserStatus.UNVERIFIED:
        result = await svc._resend_credentials(user, request.client.host if request.client else None, is_resend=True)
        email_ok = await send_resend_verification_email(body.email, result["user_code"], result["temp_password"])
        logger.info("resend email_sent=%s to=%s", email_ok, body.email)
    # Luôn trả generic response
    return {"success": True, "message": "If the email exists and is unverified, a new email has been sent."}


@router.post("/login")
async def login(body: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    try:
        svc = AuthService(db)
        return await svc.login(body.email, body.password, ip_address=request.client.host if request.client else None)
    except AuthError as e:
        _auth_error_to_http(e)


class FirstLoginChangePasswordRequest(BaseModel):
    user_id: str
    old_password: str
    new_password: str


@router.post("/first-login-change-password")
async def first_login_change_password(
    body: FirstLoginChangePasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Đổi mật khẩu lần đầu — không cần JWT, dùng user_id + mật khẩu tạm thời."""
    try:
        svc = AuthService(db)
        return await svc.first_login_change_password(
            body.user_id, body.old_password, body.new_password,
            ip_address=request.client.host if request.client else None,
        )
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
