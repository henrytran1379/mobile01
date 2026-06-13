"""Service lưu KYC VNeID v2 (Live Text + QR verify) vào database."""
from __future__ import annotations

import json
import logging
from datetime import datetime, date
from typing import Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


def _d(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except Exception:
        return None


async def upsert_session(
    db: AsyncSession,
    *,
    user_id: UUID,
    session_id: str,
    status: str,
    verify_method: Optional[str],
    live_data: Optional[dict],
    qr_data: Optional[dict],
    mismatch_detail: Optional[dict],
    vneid_image_file_id: str,
    vneid_image_path: str,
    portrait_image_file_id: str,
    portrait_image_path: str,
    portrait_uploaded: bool,
    verified_at: Optional[datetime],
) -> dict:
    """INSERT hoặc UPDATE kycvneid_sessions theo session_id."""
    now = datetime.utcnow()
    ld = live_data or {}

    await db.execute(
        text("""
            INSERT INTO kycvneid_sessions (
                user_id, session_id, kyc_type, status, verify_method,
                cccd, full_name, date_of_birth, gender, nationality,
                place_of_residence, place_of_birth, issue_date, expiry_date,
                live_text_data_json, qr_data_json, mismatch_detail_json,
                vneid_image_file_id, vneid_image_path,
                portrait_image_file_id, portrait_image_path, portrait_uploaded,
                verified_at, created_at, updated_at
            ) VALUES (
                :user_id, :session_id, 'VNEID', :status, :verify_method,
                :cccd, :full_name, :dob, :gender, :nationality,
                :place_of_residence, :place_of_birth, :issue_date, :expiry_date,
                :live_json, :qr_json, :mismatch_json,
                :vneid_file_id, :vneid_path,
                :portrait_file_id, :portrait_path, :portrait_uploaded,
                :verified_at, :now, :now
            )
            ON CONFLICT (session_id) DO UPDATE SET
                status                  = EXCLUDED.status,
                verify_method           = EXCLUDED.verify_method,
                cccd                    = EXCLUDED.cccd,
                full_name               = EXCLUDED.full_name,
                date_of_birth           = EXCLUDED.date_of_birth,
                gender                  = EXCLUDED.gender,
                nationality             = EXCLUDED.nationality,
                place_of_residence      = EXCLUDED.place_of_residence,
                place_of_birth          = EXCLUDED.place_of_birth,
                issue_date              = EXCLUDED.issue_date,
                expiry_date             = EXCLUDED.expiry_date,
                live_text_data_json     = EXCLUDED.live_text_data_json,
                qr_data_json            = EXCLUDED.qr_data_json,
                mismatch_detail_json    = EXCLUDED.mismatch_detail_json,
                vneid_image_file_id     = EXCLUDED.vneid_image_file_id,
                vneid_image_path        = EXCLUDED.vneid_image_path,
                portrait_image_file_id  = EXCLUDED.portrait_image_file_id,
                portrait_image_path     = EXCLUDED.portrait_image_path,
                portrait_uploaded       = EXCLUDED.portrait_uploaded,
                verified_at             = EXCLUDED.verified_at,
                updated_at              = :now
        """),
        {
            "user_id":          str(user_id),
            "session_id":       session_id,
            "status":           status,
            "verify_method":    verify_method,
            "cccd":             ld.get("id_number"),
            "full_name":        ld.get("full_name"),
            "dob":              _d(ld.get("date_of_birth")),
            "gender":           ld.get("gender"),
            "nationality":      ld.get("nationality"),
            "place_of_residence": ld.get("place_of_residence"),
            "place_of_birth":   ld.get("place_of_birth"),
            "issue_date":       _d(ld.get("issue_date")),
            "expiry_date":      _d(ld.get("expiry_date")),
            "live_json":        json.dumps(live_data,    ensure_ascii=False) if live_data else None,
            "qr_json":          json.dumps(qr_data,     ensure_ascii=False) if qr_data   else None,
            "mismatch_json":    json.dumps(mismatch_detail, ensure_ascii=False) if mismatch_detail else None,
            "vneid_file_id":    vneid_image_file_id,
            "vneid_path":       vneid_image_path,
            "portrait_file_id": portrait_image_file_id,
            "portrait_path":    portrait_image_path,
            "portrait_uploaded": portrait_uploaded,
            "verified_at":      verified_at,
            "now":              now,
        },
    )
    await db.commit()
    logger.info(
        "kycvneid2 upsert session=%s user=%s status=%s portrait=%s",
        session_id, str(user_id)[:8], status, portrait_uploaded,
    )
    return {"session_id": session_id, "status": status}


async def get_latest_session(db: AsyncSession, user_id: UUID) -> Optional[dict]:
    """Lấy phiên KYC VNeID v2 mới nhất của user."""
    r = await db.execute(
        text("""
            SELECT session_id, status, verify_method,
                   cccd, full_name, date_of_birth,
                   portrait_uploaded, verified_at, created_at
            FROM kycvneid_sessions
            WHERE user_id = :uid
            ORDER BY created_at DESC
            LIMIT 1
        """),
        {"uid": str(user_id)},
    )
    row = r.fetchone()
    if not row:
        return None
    return {
        "session_id":       row[0],
        "status":           row[1],
        "verify_method":    row[2],
        "cccd":             row[3],
        "full_name":        row[4],
        "date_of_birth":    row[5].isoformat() if row[5] else None,
        "portrait_uploaded": row[6],
        "verified_at":      row[7].isoformat() if row[7] else None,
        "created_at":       row[8].isoformat() if row[8] else None,
    }
