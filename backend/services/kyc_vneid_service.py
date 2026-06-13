"""Service lưu KYC VNeID vào database sau khi user xác nhận."""
import logging
from datetime import datetime, date
from typing import Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def save_confirmed(
    db: AsyncSession,
    user_id: UUID,
    data: dict,
    session_id: str = "",
    screenshot_path: str = "",
    portrait_path: str = "",
) -> dict:
    """Lưu KYC đã xác nhận vào bảng kyc_vneid.

    Args:
        db:               AsyncSession
        user_id:          UUID của user
        data:             dict từ parse_cccd_live_text()
        session_id:       kyc_session_id (để admin truy vết file)
        screenshot_path:  đường dẫn ảnh VNeID screenshot
        portrait_path:    đường dẫn ảnh chân dung

    Chỉ gọi hàm này sau khi user bấm 'Xác nhận'.
    """
    now = datetime.utcnow()

    def _d(s: Optional[str]) -> Optional[date]:
        if not s:
            return None
        try:
            return date.fromisoformat(s)
        except Exception:
            return None

    # raw_text không được lưu lâu dài — chỉ lưu thông tin đã parse
    row = await db.execute(
        text("""
            INSERT INTO kyc_vneid (
                user_id, id_number, full_name, date_of_birth, gender,
                nationality, place_of_residence, place_of_birth,
                issue_date, expiry_date, raw_text, source, kyc_method,
                kyc_status, kyc_session_id,
                screenshot_path, portrait_path,
                created_at, confirmed_at
            ) VALUES (
                :user_id, :id_number, :full_name, :dob, :gender,
                :nationality, :place_of_residence, :place_of_birth,
                :issue_date, :expiry_date, NULL, :source, :kyc_method,
                'CONFIRMED', :session_id,
                :screenshot_path, :portrait_path,
                :now, :now
            )
            RETURNING id
        """),
        {
            "user_id":            str(user_id),
            "id_number":          data.get("id_number"),
            "full_name":          data.get("full_name"),
            "dob":                _d(data.get("date_of_birth")),
            "gender":             data.get("gender"),
            "nationality":        data.get("nationality"),
            "place_of_residence": data.get("place_of_residence"),
            "place_of_birth":     data.get("place_of_birth"),
            "issue_date":         _d(data.get("issue_date")),
            "expiry_date":        _d(data.get("expiry_date")),
            "source":             data.get("source", "iphone_live_text"),
            "kyc_method":         data.get("kyc_method", "vneid_screenshot_plus_live_text"),
            "session_id":         session_id,
            "screenshot_path":    screenshot_path,
            "portrait_path":      portrait_path,
            "now":                now,
        },
    )
    await db.commit()
    inserted_id = row.scalar()
    logger.info(
        "KYC VNeID saved: id=%s user=%s id_number=%s session=%s "
        "screenshot=%s portrait=%s",
        inserted_id, user_id, data.get("id_number"),
        session_id, bool(screenshot_path), bool(portrait_path),
    )
    return {"kyc_vneid_id": str(inserted_id), "kyc_status": "CONFIRMED"}


async def get_status(db: AsyncSession, user_id: UUID) -> Optional[dict]:
    """Lấy trạng thái KYC VNeID mới nhất của user."""
    r = await db.execute(
        text("""
            SELECT id, id_number, full_name, kyc_status, confirmed_at,
                   screenshot_path, portrait_path
            FROM kyc_vneid
            WHERE user_id = :uid
            ORDER BY confirmed_at DESC NULLS LAST
            LIMIT 1
        """),
        {"uid": str(user_id)},
    )
    row = r.fetchone()
    if not row:
        return None
    return {
        "kyc_vneid_id":    str(row[0]),
        "id_number":       row[1],
        "full_name":       row[2],
        "kyc_status":      row[3],
        "confirmed_at":    row[4].isoformat() if row[4] else None,
        "has_screenshot":  bool(row[5]),
        "has_portrait":    bool(row[6]),
    }
