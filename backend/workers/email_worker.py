from celery import Celery
from backend.core.config import settings
from backend.integrations.smtp.sender import send_registration_email

celery_app = Celery("p2psuperbot", broker=settings.REDIS_URL, backend=settings.REDIS_URL)


@celery_app.task(name="workers.send_registration_email", bind=True, max_retries=3)
def task_send_registration_email(self, to: str, user_code: str, temp_password: str):
    import asyncio
    try:
        asyncio.run(send_registration_email(to, user_code, temp_password))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
