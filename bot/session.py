"""Quản lý session JWT của user Telegram trong Redis."""
import json
import redis as sync_redis
from backend.core.config import settings

_r = sync_redis.from_url(settings.REDIS_URL, decode_responses=True, protocol=2)

SESSION_TTL = 3600  # 1 giờ


def save_session(telegram_id: int, data: dict) -> None:
    _r.setex(f"bot:session:{telegram_id}", SESSION_TTL, json.dumps(data))


def get_session(telegram_id: int) -> dict | None:
    raw = _r.get(f"bot:session:{telegram_id}")
    return json.loads(raw) if raw else None


def delete_session(telegram_id: int) -> None:
    _r.delete(f"bot:session:{telegram_id}")


def get_token(telegram_id: int) -> str | None:
    session = get_session(telegram_id)
    return session.get("access_token") if session else None


def is_logged_in(telegram_id: int) -> bool:
    return get_token(telegram_id) is not None


def get_role(telegram_id: int) -> str:
    session = get_session(telegram_id)
    return session.get("role", "USER") if session else "USER"
