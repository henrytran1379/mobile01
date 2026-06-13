import asyncio
import logging
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.core.config import settings

logger = logging.getLogger(__name__)

_SMTP_TIMEOUT = 10   # giây — timeout mỗi lần kết nối
_MAX_RETRIES  = 2    # số lần thử lại khi lỗi tạm thời


async def _smtp_send(message) -> bool:
    """Gửi email với retry tự động."""
    for attempt in range(1, _MAX_RETRIES + 2):
        try:
            use_ssl = settings.SMTP_PORT == 465
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                use_tls=use_ssl,          # SSL trực tiếp (port 465)
                start_tls=not use_ssl,    # STARTTLS (port 587)
                timeout=_SMTP_TIMEOUT,
            )
            return True
        except aiosmtplib.SMTPAuthenticationError as e:
            logger.error("SMTP auth failed (no retry): %s", e)
            return False  # auth sai → không retry
        except (aiosmtplib.SMTPConnectError, aiosmtplib.SMTPServerDisconnected, asyncio.TimeoutError) as e:
            logger.warning("SMTP attempt %d/%d failed: %s", attempt, _MAX_RETRIES + 1, e)
            if attempt <= _MAX_RETRIES:
                await asyncio.sleep(1)   # chờ 1 giây rồi thử lại
            else:
                logger.error("SMTP failed after %d attempts to=%s", _MAX_RETRIES + 1, message["To"])
                return False
        except Exception as e:
            logger.error("SMTP unexpected error to=%s: %s", message["To"], e)
            return False
    return False


async def send_email(to: str, subject: str, body_html: str, body_text: str = "") -> bool:
    message = MIMEMultipart("alternative")
    message["From"]    = settings.SMTP_FROM
    message["To"]      = to
    message["Subject"] = subject
    # Plain text trước — Gmail ưu tiên hiển thị nhanh hơn
    if body_text:
        message.attach(MIMEText(body_text, "plain", "utf-8"))
    message.attach(MIMEText(body_html, "html", "utf-8"))

    ok = await _smtp_send(message)
    if ok:
        logger.info("Email sent to=%s subject=%s", to, subject)
    return ok


# ── Templates ─────────────────────────────────────────────────────────────────

def _creds_html(title: str, user_code: str, temp_password: str, note: str = "") -> str:
    return f"""
<div style="font-family:Arial,sans-serif;max-width:500px;margin:auto;padding:24px;
            border:1px solid #e0e0e0;border-radius:8px;">
  <h2 style="color:#2c3e50;">{title}</h2>
  <table style="width:100%;border-collapse:collapse;margin:16px 0;">
    <tr>
      <td style="padding:10px;background:#f5f5f5;font-weight:bold;width:45%;">User Code</td>
      <td style="padding:10px;font-family:monospace;font-size:18px;letter-spacing:1px;">{user_code}</td>
    </tr>
    <tr>
      <td style="padding:10px;background:#f5f5f5;font-weight:bold;">Temporary Password</td>
      <td style="padding:10px;font-family:monospace;font-size:18px;letter-spacing:1px;">{temp_password}</td>
    </tr>
  </table>
  <p style="color:#e74c3c;"><strong>⚠️ Đăng nhập và đổi mật khẩu ngay lập tức.</strong></p>
  {f'<p style="color:#555;">{note}</p>' if note else ''}
  <p style="color:#999;font-size:12px;">Nếu bạn không thực hiện yêu cầu này, hãy bỏ qua email này.</p>
</div>"""


def _creds_text(user_code: str, temp_password: str) -> str:
    return (
        f"P2PSuperBot — Thong tin dang nhap\n"
        f"{'='*40}\n"
        f"User Code        : {user_code}\n"
        f"Temporary Password: {temp_password}\n"
        f"{'='*40}\n"
        f"Vui long dang nhap va doi mat khau ngay.\n"
        f"Bot Telegram: @p2psuperbot\n"
    )


async def send_registration_email(to: str, user_code: str, temp_password: str) -> bool:
    return await send_email(
        to=to,
        subject="[P2PSuperBot] Tài khoản đã được tạo — Thông tin đăng nhập",
        body_html=_creds_html(
            title="🤖 Chào mừng đến P2PSuperBot!",
            user_code=user_code,
            temp_password=temp_password,
            note="Tài khoản của bạn đã được tạo thành công.",
        ),
        body_text=_creds_text(user_code, temp_password),
    )


async def send_resend_verification_email(to: str, user_code: str, temp_password: str) -> bool:
    return await send_email(
        to=to,
        subject="[P2PSuperBot] Gửi lại thông tin đăng nhập",
        body_html=_creds_html(
            title="🔄 P2PSuperBot — Gửi lại thông tin đăng nhập",
            user_code=user_code,
            temp_password=temp_password,
            note="Bạn đã yêu cầu gửi lại thông tin đăng nhập.",
        ),
        body_text=_creds_text(user_code, temp_password),
    )
