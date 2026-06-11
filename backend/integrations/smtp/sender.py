import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.core.config import settings


async def send_email(to: str, subject: str, body_html: str) -> bool:
    message = MIMEMultipart("alternative")
    message["From"] = settings.SMTP_FROM
    message["To"] = to
    message["Subject"] = subject
    message.attach(MIMEText(body_html, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        return True
    except Exception:
        return False


async def send_registration_email(to: str, user_code: str, temp_password: str) -> bool:
    body = f"""
    <h2>Welcome to P2PSuperBot</h2>
    <p>Your account has been created.</p>
    <p><strong>User Code:</strong> {user_code}</p>
    <p><strong>Temporary Password:</strong> {temp_password}</p>
    <p>Please login and change your password immediately.</p>
    """
    return await send_email(to, "Welcome to P2PSuperBot", body)
