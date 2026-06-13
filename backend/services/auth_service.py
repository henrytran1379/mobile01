import asyncio
import logging
import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.user import User, UserStatus

logger = logging.getLogger(__name__)
from backend.repositories.user_repository import UserRepository
from backend.repositories.security_repository import (
    UserSecurityRepository, RegistrationSessionRepository,
    UserSessionRepository, RecoveryCodeRepository,
)
from backend.repositories.audit_repository import AuditLogRepository
from backend.security.password import (
    hash_password, verify_password, generate_temp_password,
    generate_activation_token, generate_user_code,
)
from backend.security.jwt import create_access_token, create_refresh_token
from backend.security.totp import (
    generate_totp_secret, get_totp_uri, verify_totp,
    generate_qr_base64, generate_recovery_codes, hash_recovery_codes,
)
from backend.core.config import settings


class AuthError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.security_repo = UserSecurityRepository(session)
        self.reg_session_repo = RegistrationSessionRepository(session)
        self.user_session_repo = UserSessionRepository(session)
        self.recovery_repo = RecoveryCodeRepository(session)
        self.audit_repo = AuditLogRepository(session)

    async def register(self, email: str, ip_address: str | None = None) -> dict:
        existing = await self.user_repo.get_by_email(email)

        if existing:
            # Email đã tồn tại nhưng chưa xác minh → resend
            if existing.status in UserStatus.UNVERIFIED:
                return await self._resend_credentials(existing, ip_address, is_resend=True)
            # Email đã active → block
            raise AuthError(
                "EMAIL_REGISTERED",
                "Email already registered. Please login or reset your password.",
            )

        # Tạo user mới
        user_code = generate_user_code()
        while await self.user_repo.get_by_user_code(user_code):
            user_code = generate_user_code()

        user = await self.user_repo.create(
            email=email,
            user_code=user_code,
            status=UserStatus.PENDING_EMAIL_VERIFICATION,
            role="USER",
        )

        await self.security_repo.create(
            user_id=user.id,
            password_hash="",  # placeholder, set bên dưới
        )

        return await self._resend_credentials(user, ip_address, is_resend=False)

    async def _resend_credentials(self, user, ip_address: str | None, is_resend: bool) -> dict:
        """Tạo/làm mới registration session và gửi email credentials."""
        temp_password = generate_temp_password()
        activation_token = generate_activation_token()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.TEMP_PASSWORD_EXPIRE_HOURS)
        now = datetime.now(timezone.utc)

        # Invalidate session cũ (mark used)
        old_session = await self.reg_session_repo.get_active_by_user(user.id)
        if old_session:
            await self.reg_session_repo.mark_used(old_session.id)

        await self.reg_session_repo.create(
            user_id=user.id,
            temporary_password_hash=hash_password(temp_password),
            activation_token_hash=hash_password(activation_token),
            expires_at=expires_at,
            used=False,
            created_at=now,
        )

        # Cập nhật password hash trong security
        await self.security_repo.set_password(user.id, hash_password(temp_password))

        await self.audit_repo.log(
            action="USER_REGISTERED" if not is_resend else "VERIFICATION_EMAIL_RESENT",
            actor_type="SYSTEM",
            target_id=user.id,
            target_type="USER",
            ip_address=ip_address,
            metadata={"email": user.email, "user_code": user.user_code},
        )

        return {
            "user_id": str(user.id),
            "user_code": user.user_code,
            "temp_password": temp_password,
            "activation_token": activation_token,
            "resent": is_resend,
        }

    async def resend_verification(self, email: str, ip_address: str | None = None) -> dict:
        """Resend credentials — luôn trả về generic response để tránh user enumeration."""
        user = await self.user_repo.get_by_email(email)
        if user and user.status in UserStatus.UNVERIFIED:
            await self._resend_credentials(user, ip_address, is_resend=True)
        # Trả về generic dù email có tồn tại hay không
        return {"success": True, "message": "If the email exists and is unverified, a new email has been sent."}

    async def login(self, email: str, password: str, ip_address: str | None = None) -> dict:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise AuthError("INVALID_CREDENTIALS", "Invalid email or password")

        if user.status in (UserStatus.DISABLED, UserStatus.SUSPENDED):
            raise AuthError("ACCOUNT_DISABLED", "Account is disabled")

        security = await self.security_repo.get_by_user_id(user.id)
        if not security:
            raise AuthError("INVALID_CREDENTIALS", "Invalid email or password")

        now = datetime.now(timezone.utc)
        if security.locked_until and security.locked_until.replace(tzinfo=timezone.utc) > now:
            raise AuthError("ACCOUNT_LOCKED", "Account is temporarily locked")

        if not verify_password(password, security.password_hash):
            await self.security_repo.increment_failed_login(user.id)
            if security.failed_login_count + 1 >= settings.MAX_LOGIN_ATTEMPTS:
                locked_until = now + timedelta(minutes=settings.LOCKOUT_MINUTES)
                await self.security_repo.set_locked_until(user.id, locked_until)
                raise AuthError("ACCOUNT_LOCKED", "Too many failed attempts. Account locked.")
            raise AuthError("INVALID_CREDENTIALS", "Invalid email or password")

        await self.security_repo.update_last_login(user.id, now)

        if user.status in (UserStatus.ACCOUNT_CREATED, UserStatus.PENDING_EMAIL_VERIFICATION):
            # Nâng status lên ACCOUNT_CREATED nếu vẫn còn PENDING
            if user.status == UserStatus.PENDING_EMAIL_VERIFICATION:
                await self.user_repo.update_status(user.id, UserStatus.ACCOUNT_CREATED)
            await self.audit_repo.log(
                action="FIRST_LOGIN_ATTEMPT",
                actor_type="USER",
                actor_id=user.id,
                ip_address=ip_address,
            )
            return {"requires_password_change": True, "user_id": str(user.id)}

        if security.two_factor_enabled:
            pending_token = create_access_token(
                str(user.id), extra={"pending_2fa": True, "role": user.role}
            )
            return {"requires_2fa": True, "pending_token": pending_token}

        return await self._create_full_session(user, security, ip_address)

    async def first_login_change_password(
        self, user_id: str, old_password: str, new_password: str, ip_address: str | None = None
    ) -> dict:
        """Đổi mật khẩu lần đầu (không cần JWT). Trả về access token luôn."""
        uid = uuid.UUID(user_id)
        user = await self.user_repo.get_by_id(uid)
        if not user:
            raise AuthError("USER_NOT_FOUND", "User not found")
        if user.status not in UserStatus.UNVERIFIED:
            raise AuthError("INVALID_CREDENTIALS", "Invalid request")

        security = await self.security_repo.get_by_user_id(uid)
        if not security or not verify_password(old_password, security.password_hash):
            raise AuthError("INVALID_CREDENTIALS", "Invalid email or password")

        await self.security_repo.change_password(uid, hash_password(new_password))
        await self.user_repo.update_status(uid, UserStatus.WAITING_FIRST_LOGIN)
        await self.audit_repo.log(
            action="FIRST_LOGIN_PASSWORD_CHANGED",
            actor_type="USER",
            actor_id=uid,
            ip_address=ip_address,
        )
        # Trả về full session ngay
        return await self._create_full_session(user, security, ip_address)

    async def change_password(
        self, user_id: str, old_password: str, new_password: str, ip_address: str | None = None
    ) -> dict:
        uid = uuid.UUID(user_id)
        security = await self.security_repo.get_by_user_id(uid)
        if not security:
            raise AuthError("USER_NOT_FOUND", "User not found")

        if not verify_password(old_password, security.password_hash):
            raise AuthError("INVALID_PASSWORD", "Old password is incorrect")

        await self.security_repo.change_password(uid, hash_password(new_password))

        user = await self.user_repo.get_by_id(uid)
        if user.status == UserStatus.ACCOUNT_CREATED:
            await self.user_repo.update_status(uid, UserStatus.WAITING_FIRST_LOGIN)

        await self.audit_repo.log(
            action="PASSWORD_CHANGED",
            actor_type="USER",
            actor_id=uid,
            ip_address=ip_address,
        )
        return {"success": True}

    async def setup_2fa(self, user_id: str) -> dict:
        uid = uuid.UUID(user_id)
        user = await self.user_repo.get_by_id(uid)
        if not user:
            raise AuthError("USER_NOT_FOUND", "User not found")

        secret = generate_totp_secret()
        uri = get_totp_uri(secret, user.email)
        qr_base64 = generate_qr_base64(uri)

        from backend.core.redis import get_redis
        r = await get_redis()
        await r.setex(f"2fa_setup:{user_id}", 1800, secret)

        return {"secret": secret, "qr_code": qr_base64, "uri": uri}

    async def verify_2fa_setup(self, user_id: str, code: str, ip_address: str | None = None) -> dict:
        from backend.core.redis import get_redis
        r = await get_redis()
        secret = await r.get(f"2fa_setup:{user_id}")
        if not secret:
            raise AuthError("SETUP_EXPIRED", "2FA setup session expired")

        if not verify_totp(secret, code):
            raise AuthError("INVALID_CODE", "Invalid TOTP code")

        uid = uuid.UUID(user_id)
        await self.security_repo.enable_2fa(uid, secret)
        await r.delete(f"2fa_setup:{user_id}")

        plain_codes = generate_recovery_codes()
        hashed_codes = hash_recovery_codes(plain_codes)
        now = datetime.now(timezone.utc)
        for hashed in hashed_codes:
            await self.recovery_repo.create(
                user_id=uid, code_hash=hashed, used=False, created_at=now
            )

        await self.user_repo.update_status(uid, UserStatus.ACTIVE)

        await self.audit_repo.log(
            action="2FA_ENABLED",
            actor_type="USER",
            actor_id=uid,
            ip_address=ip_address,
        )
        return {"success": True, "recovery_codes": plain_codes}

    async def verify_2fa_login(self, pending_token: str, code: str, ip_address: str | None = None) -> dict:
        from backend.security.jwt import decode_token
        try:
            payload = decode_token(pending_token)
            if not payload.get("pending_2fa"):
                raise AuthError("INVALID_TOKEN", "Invalid token")
            user_id = payload["sub"]
        except ValueError:
            raise AuthError("INVALID_TOKEN", "Invalid or expired token")

        uid = uuid.UUID(user_id)
        security = await self.security_repo.get_by_user_id(uid)
        if not security or not security.two_factor_secret:
            raise AuthError("2FA_NOT_CONFIGURED", "2FA not configured")

        if not verify_totp(security.two_factor_secret, code):
            # Try recovery codes
            if not await self._try_recovery_code(uid, code):
                raise AuthError("INVALID_CODE", "Invalid TOTP code")

        user = await self.user_repo.get_by_id(uid)
        return await self._create_full_session(user, security, ip_address)

    async def _try_recovery_code(self, user_id: uuid.UUID, code: str) -> bool:
        unused = await self.recovery_repo.get_unused_by_user(user_id)
        for rc in unused:
            if verify_password(code.upper(), rc.code_hash):
                await self.recovery_repo.mark_used(rc.id)
                return True
        return False

    async def _create_full_session(self, user, security, ip_address: str | None) -> dict:
        access_token = create_access_token(str(user.id), extra={"role": user.role})
        refresh_token = create_refresh_token(str(user.id))

        from datetime import timedelta, timezone
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)

        await self.user_session_repo.create(
            user_id=user.id,
            session_token_hash=hash_password(access_token[:50]),
            refresh_token_hash=hash_password(refresh_token[:50]),
            ip_address=ip_address,
            expires_at=expires_at,
            is_active=True,
            created_at=now,
        )

        await self.audit_repo.log(
            action="LOGIN_SUCCESS",
            actor_type="USER",
            actor_id=user.id,
            ip_address=ip_address,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": str(user.id),
            "user_code": user.user_code,
            "role": user.role,
        }


async def _send_reg_email(email: str, user_code: str, temp_password: str) -> None:
    try:
        from backend.integrations.smtp.sender import send_registration_email
        ok = await send_registration_email(email, user_code, temp_password)
        if ok:
            logger.info("Registration email sent to %s", email)
        else:
            logger.warning("Failed to send registration email to %s", email)
    except Exception as e:
        logger.error("Email error for %s: %s", email, e)
