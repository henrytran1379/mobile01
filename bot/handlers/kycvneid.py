"""KYC VNeID v2 — Live Text + QR verify + ảnh chân dung.

Lệnh: /kycvneid

Flow:
  Bước 1 — User paste Live Text từ VNeID → bot parse, lưu session
  Bước 2 — User upload ảnh chụp màn hình VNeID có QR → bot decode QR, so sánh
  Bước 3 — Nếu khớp: VERIFIED; nếu không: NEED_MANUAL_REVIEW
  Bước 4 — User upload ảnh chân dung → hoàn tất hồ sơ

Hỗ trợ làm sai thứ tự: Bước 1 & 2 có thể đổi chỗ.
Không OCR, không face match, không liveness.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from bot.session import is_logged_in, get_token, get_role
from bot.keyboards import main_menu, cancel_keyboard
import bot.api_client as api
from backend.services.kyc_live_text_parser import parse_cccd_live_text, is_cccd_text
from backend.services.qr_decoder import decode_qr_from_image
from backend.services.kyc_compare_engine import compare_livetext_qr

logger = logging.getLogger(__name__)

# ── States ────────────────────────────────────────────────────────────────────
KV2_COLLECTING = 0   # nhận Live Text hoặc ảnh VNeID (theo thứ tự bất kỳ)
KV2_PORTRAIT   = 1   # nhận ảnh chân dung

# ── Storage ───────────────────────────────────────────────────────────────────
_FILE_BASE = Path("kyc_files") / "kycvneid2"

_LOGIN_REQ = (
    "🔒 *Cần đăng nhập trước*\n\n"
    "👉 Dùng /login để đăng nhập."
)
_PRIVATE_ONLY = (
    "🔒 Lệnh KYC chỉ dùng được trong *chat riêng* với bot.\n"
    "Vui lòng nhắn tin trực tiếp cho @P2PSuperBot."
)


# ── Entry point ───────────────────────────────────────────────────────────────

async def cmd_kycvneid(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Lệnh /kycvneid hoặc callback start_kycvneid2 — bắt đầu phiên KYC VNeID."""
    em = update.effective_message

    # Trả lời callback nếu có
    if update.callback_query:
        await update.callback_query.answer()

    # Chỉ cho phép trong private chat
    if update.effective_chat.type != "private":
        await em.reply_text(_PRIVATE_ONLY, parse_mode="Markdown")
        return ConversationHandler.END

    uid = update.effective_user.id
    if not is_logged_in(uid):
        await em.reply_text(_LOGIN_REQ, parse_mode="Markdown",
                            reply_markup=main_menu(False))
        return ConversationHandler.END

    token = get_token(uid)

    # Kiểm tra đã KYC VNeID v2 chưa
    existing = await api.get_kycvneid2_status(token)
    if existing and existing.get("status") in ("VERIFIED", "NEED_MANUAL_REVIEW"):
        st = existing["status"]
        icon = "✅" if st == "VERIFIED" else "⚠️"
        label = "Đã xác minh tự động" if st == "VERIFIED" else "Đang chờ xét duyệt thủ công"
        await em.reply_text(
            f"{icon} *Hồ sơ KYC VNeID của bạn*\n\n"
            f"📋 Trạng thái: *{label}*\n"
            f"👤 Họ tên: {existing.get('full_name') or '—'}\n"
            f"🔢 Số CCCD: `{_mask(existing.get('cccd') or '')}`\n\n"
            "ℹ️ _Nếu cần cập nhật, liên hệ hỗ trợ._",
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    # Khởi tạo session mới
    session_id = uuid.uuid4().hex[:16]
    _init_ctx(ctx, uid, session_id)

    await em.reply_text(
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🪪 *KYC VNeID — Xác minh tự động*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Quy trình gồm 3 bước:\n"
        "  📋 *Bước 1* — Paste Live Text từ VNeID\n"
        "  📷 *Bước 2* — Upload ảnh màn hình VNeID (có QR)\n"
        "  🤳 *Bước 3* — Upload ảnh chân dung\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📋 *Bước 1/3 — Paste Live Text*\n\n"
        "Mở VNeID → *Thông tin thẻ Căn cước* → dùng iPhone Live Text "
        "copy toàn bộ nội dung rồi paste vào đây.\n\n"
        "_Tin nhắn sẽ được xóa ngay sau khi đọc để bảo vệ dữ liệu cá nhân._",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard(),
    )
    return KV2_COLLECTING


# ── State: COLLECTING — nhận Live Text hoặc ảnh VNeID ────────────────────────

async def collecting_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Nhận text trong trạng thái COLLECTING — coi là Live Text."""
    text = (update.message.text or "").strip()
    if not text:
        return KV2_COLLECTING

    if not is_cccd_text(text):
        await update.message.reply_text(
            "⚠️ Không nhận ra nội dung CCCD trong tin nhắn này.\n\n"
            "Hãy copy *toàn bộ* text từ màn hình *Thông tin thẻ Căn cước* trong VNeID "
            "bằng tính năng Live Text của iPhone rồi paste vào đây.",
            parse_mode="Markdown",
        )
        return KV2_COLLECTING

    # Xóa tin nhắn gốc ngay
    try:
        await update.message.delete()
    except Exception:
        pass

    result = parse_cccd_live_text(text)
    result.pop("raw_text", None)   # không lưu raw text

    if result["parse_status"] == "failed":
        await update.message.reply_text(
            "❌ *Không đọc được thông tin CCCD*\n\n"
            "Hãy copy *toàn bộ* text từ màn hình VNeID (gồm cả mặt trước và mặt sau) rồi paste lại.",
            parse_mode="Markdown",
        )
        return KV2_COLLECTING

    ctx.user_data["kv2_live_data"] = result
    missing = result.get("missing_fields", [])

    # Hiển thị thông tin đã parse
    warn = ""
    if missing:
        warn = f"\n\n⚠️ _Thiếu trường: {', '.join(missing)} — sẽ do admin bổ sung._"

    await update.message.reply_text(
        "✅ *Đã trích xuất thông tin Live Text*\n\n"
        + _format_live_data(result)
        + warn,
        parse_mode="Markdown",
    )

    return await _check_and_proceed(update, ctx)


async def collecting_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Nhận ảnh trong trạng thái COLLECTING — coi là ảnh chụp màn hình VNeID."""
    if not update.message.photo:
        await update.message.reply_text(
            "⚠️ Vui lòng gửi *ảnh chụp màn hình VNeID* có chứa QR Code.",
            parse_mode="Markdown",
        )
        return KV2_COLLECTING

    await update.message.reply_text("⏳ Đang đọc QR Code từ ảnh...")

    # Download ảnh chất lượng cao nhất
    photo_file = await update.message.photo[-1].get_file()
    image_bytes = bytes(await photo_file.download_as_bytearray())
    file_id = update.message.photo[-1].file_id

    # Decode QR
    qr_data = decode_qr_from_image(image_bytes)
    if not qr_data:
        await update.message.reply_text(
            "❌ *Không đọc được QR Code*\n\n"
            "Vui lòng upload lại ảnh với yêu cầu:\n"
            "  • Ảnh chụp màn hình *Thông tin thẻ Căn cước* trong VNeID\n"
            "  • QR Code phải hiển thị rõ, không bị che hoặc cắt xén\n"
            "  • Không cần chụp lại — chỉ cần chụp màn hình điện thoại",
            parse_mode="Markdown",
        )
        return KV2_COLLECTING

    # Lưu ảnh vào đĩa
    uid        = ctx.user_data.get("kv2_uid")
    session_id = ctx.user_data.get("kv2_session_id", "unknown")
    saved_path = _save_file(uid, session_id, "vneid_screenshot.jpg", image_bytes)

    ctx.user_data["kv2_qr_data"]            = qr_data
    ctx.user_data["kv2_vneid_image_file_id"] = file_id
    ctx.user_data["kv2_vneid_image_path"]    = str(saved_path)

    await update.message.reply_text(
        "✅ *Đã đọc QR Code*\n\n"
        f"🔢 Số CCCD: `{_mask(qr_data['cccd'])}`\n"
        f"👤 Họ tên: {qr_data['full_name']}\n"
        f"🎂 Ngày sinh: {_fmt_date(qr_data['date_of_birth'])}",
        parse_mode="Markdown",
    )

    return await _check_and_proceed(update, ctx)


# ── State: PORTRAIT — nhận ảnh chân dung ─────────────────────────────────────

async def portrait_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Nhận ảnh chân dung."""
    if not update.message.photo:
        await update.message.reply_text(
            "⚠️ Vui lòng gửi *ảnh chân dung* (selfie hoặc ảnh thẻ).",
            parse_mode="Markdown",
        )
        return KV2_PORTRAIT

    await update.message.reply_text("⏳ Đang lưu ảnh chân dung...")

    photo_file = await update.message.photo[-1].get_file()
    image_bytes = bytes(await photo_file.download_as_bytearray())
    file_id = update.message.photo[-1].file_id

    uid        = ctx.user_data.get("kv2_uid")
    session_id = ctx.user_data.get("kv2_session_id", "unknown")
    saved_path = _save_file(uid, session_id, "portrait.jpg", image_bytes)

    ctx.user_data["kv2_portrait_file_id"] = file_id
    ctx.user_data["kv2_portrait_path"]    = str(saved_path)

    # Lưu toàn bộ hồ sơ vào DB
    return await _save_to_db_and_finish(update, ctx)


async def portrait_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """User gửi text ở bước PORTRAIT — nhắc gửi ảnh."""
    await update.message.reply_text(
        "🤳 *Bước 3/3 — Ảnh chân dung*\n\n"
        "Vui lòng gửi *ảnh chân dung* (selfie hoặc ảnh thẻ) để hoàn tất hồ sơ KYC.",
        parse_mode="Markdown",
    )
    return KV2_PORTRAIT


# ── Callback: bỏ qua ảnh chân dung ───────────────────────────────────────────

async def cb_skip_portrait(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """User bỏ qua bước ảnh chân dung."""
    query = update.callback_query
    await query.answer()
    ctx.user_data["kv2_portrait_file_id"] = ""
    ctx.user_data["kv2_portrait_path"]    = ""
    return await _save_to_db_and_finish(update, ctx)


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _check_and_proceed(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Kiểm tra đã có đủ cả Live Text lẫn QR chưa. Nếu thiếu → nhắc tiếp."""
    live = ctx.user_data.get("kv2_live_data")
    qr   = ctx.user_data.get("kv2_qr_data")

    if not live:
        await update.message.reply_text(
            "📋 *Bước 1/3 — Vẫn cần Live Text*\n\n"
            "Mở VNeID → Thông tin thẻ Căn cước → dùng Live Text copy toàn bộ nội dung rồi paste vào đây.",
            parse_mode="Markdown",
        )
        return KV2_COLLECTING

    if not qr:
        await update.message.reply_text(
            "📷 *Bước 2/3 — Cần ảnh chụp màn hình VNeID*\n\n"
            "Upload ảnh chụp màn hình *Thông tin thẻ Căn cước* trong VNeID "
            "(màn hình hiện QR Code đen trắng).",
            parse_mode="Markdown",
        )
        return KV2_COLLECTING

    # Đã có đủ — so sánh
    compare_result = compare_livetext_qr(live, qr)
    ctx.user_data["kv2_compare"] = compare_result

    if compare_result.matched:
        ctx.user_data["kv2_status"]        = "VERIFIED"
        ctx.user_data["kv2_verify_method"] = "QR_LIVETEXT_MATCH"
        ctx.user_data["kv2_verified_at"]   = datetime.now(timezone.utc).isoformat()

        await update.message.reply_text(
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "✅ *KYC tự động thành công!*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "3 trường xác thực *khớp hoàn toàn*:\n"
            "  ✓ Số CCCD\n"
            "  ✓ Họ tên\n"
            "  ✓ Ngày sinh\n\n"
            "🤳 *Bước 3/3 — Ảnh chân dung*\n\n"
            "Vui lòng upload ảnh chân dung (selfie hoặc ảnh thẻ) để hoàn tất hồ sơ.\n"
            "_Ảnh chỉ dùng để admin đối chiếu khi cần — không xử lý AI._",
            parse_mode="Markdown",
            reply_markup=_portrait_kb(),
        )
    else:
        mm = compare_result.mismatches
        detail_lines = []
        field_labels = {
            "cccd":          "Số CCCD",
            "full_name":     "Họ tên",
            "date_of_birth": "Ngày sinh",
        }
        for f, vals in mm.items():
            detail_lines.append(
                f"  ❌ *{field_labels.get(f, f)}*\n"
                f"     Live Text: `{vals['live'] or '—'}`\n"
                f"     QR Code:   `{vals['qr']   or '—'}`"
            )

        ctx.user_data["kv2_status"]          = "NEED_MANUAL_REVIEW"
        ctx.user_data["kv2_verify_method"]   = "QR_LIVETEXT_MISMATCH"
        ctx.user_data["kv2_mismatch_detail"] = mm

        await update.message.reply_text(
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ *Cần xét duyệt thủ công*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Một số trường không khớp giữa Live Text và QR:\n\n"
            + "\n".join(detail_lines) + "\n\n"
            "Hồ sơ sẽ được admin xét duyệt trong *1–3 ngày làm việc*.\n\n"
            "🤳 *Bước 3/3 — Ảnh chân dung*\n\n"
            "Vui lòng upload ảnh chân dung để hoàn tất hồ sơ.",
            parse_mode="Markdown",
            reply_markup=_portrait_kb(),
        )

    return KV2_PORTRAIT


async def _save_to_db_and_finish(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    """Lưu toàn bộ hồ sơ vào DB qua API, kết thúc conversation."""
    uid        = ctx.user_data.get("kv2_uid")
    session_id = ctx.user_data.get("kv2_session_id", "")
    token      = get_token(uid)
    live       = ctx.user_data.get("kv2_live_data")
    qr         = ctx.user_data.get("kv2_qr_data")
    compare    = ctx.user_data.get("kv2_compare")
    status     = ctx.user_data.get("kv2_status", "WAITING_LIVE_TEXT")

    # Loại raw_qr khỏi qr_data trước khi lưu
    qr_clean = {k: v for k, v in (qr or {}).items() if k != "raw_qr"}

    payload = {
        "session_id":             session_id,
        "status":                 status,
        "verify_method":          ctx.user_data.get("kv2_verify_method"),
        "live_data":              live,
        "qr_data":                qr_clean if qr_clean else None,
        "mismatch_detail":        ctx.user_data.get("kv2_mismatch_detail"),
        "vneid_image_file_id":    ctx.user_data.get("kv2_vneid_image_file_id", ""),
        "vneid_image_path":       ctx.user_data.get("kv2_vneid_image_path", ""),
        "portrait_image_file_id": ctx.user_data.get("kv2_portrait_file_id", ""),
        "portrait_image_path":    ctx.user_data.get("kv2_portrait_path", ""),
        "portrait_uploaded":      bool(ctx.user_data.get("kv2_portrait_path")),
        "verified_at":            ctx.user_data.get("kv2_verified_at"),
    }

    result = await api.submit_kycvneid2(token, payload)
    _clear(ctx)

    # Lấy message object đúng (từ callback_query hay message)
    msg = (
        update.callback_query.message
        if update.callback_query
        else update.message
    )

    if result.get("error") or result.get("detail"):
        err = result.get("detail") or result.get("error")
        await msg.reply_text(
            f"❌ Lưu hồ sơ thất bại: {err}\n\nVui lòng thử lại hoặc liên hệ hỗ trợ.",
            reply_markup=main_menu(True, get_role(uid)),
        )
        return ConversationHandler.END

    portrait_ok = bool(payload["portrait_image_path"])
    await msg.reply_text(
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "✅ *Hồ sơ KYC VNeID đã hoàn tất!*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📋 Hồ sơ gồm:\n"
        "  • Thông tin CCCD từ Live Text ✅\n"
        "  • Ảnh chụp màn hình VNeID ✅\n"
        + (f"  • Ảnh chân dung ✅\n" if portrait_ok else "  • Ảnh chân dung _(bỏ qua)_\n") +
        "\n"
        + (
            "🎉 *Xác minh tự động thành công!* Tài khoản của bạn đã được xác thực.\n"
            if payload["status"] == "VERIFIED"
            else "⏱ Hồ sơ đang chờ admin xét duyệt trong *1–3 ngày làm việc*.\n"
               "_Bạn sẽ được thông báo khi có kết quả._\n"
        ),
        parse_mode="Markdown",
        reply_markup=main_menu(True, get_role(uid)),
    )
    return ConversationHandler.END


# ── Keyboards ─────────────────────────────────────────────────────────────────

def _portrait_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("⏭ Bỏ qua ảnh chân dung", callback_data="kv2_skip_portrait"),
    ]])


# ── Formatters ────────────────────────────────────────────────────────────────

def _format_live_data(r: dict) -> str:
    g = {"male": "Nam ♂", "female": "Nữ ♀"}.get(r.get("gender") or "", "—")
    return (
        f"🔢 *Số CCCD:* `{_mask(r.get('id_number') or '')}`\n"
        f"👤 *Họ tên:* {r.get('full_name') or '—'}\n"
        f"🎂 *Ngày sinh:* {_fmt_date(r.get('date_of_birth'))}\n"
        f"⚧  *Giới tính:* {g}\n"
        f"🌏 *Quốc tịch:* {r.get('nationality') or '—'}\n"
        f"🏠 *Nơi cư trú:* {r.get('place_of_residence') or '—'}\n"
        f"📍 *Nơi sinh:* {r.get('place_of_birth') or '—'}\n"
        f"📅 *Ngày cấp:* {_fmt_date(r.get('issue_date'))}\n"
        f"⏳ *Hết hạn:* {_fmt_date(r.get('expiry_date'))}"
    )


def _fmt_date(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        y, m, d = iso.split("-")
        return f"{d}/{m}/{y}"
    except Exception:
        return iso


def _mask(cccd: str) -> str:
    """Mask CCCD, giữ 3 số đầu và 4 số cuối."""
    if len(cccd) <= 7:
        return cccd
    return f"{cccd[:3]}{'*' * (len(cccd) - 7)}{cccd[-4:]}"


# ── File storage ──────────────────────────────────────────────────────────────

def _save_file(uid: int, session_id: str, filename: str, data: bytes) -> Path:
    folder = _FILE_BASE / str(uid) / session_id
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / filename
    path.write_bytes(data)
    return path


# ── Session helpers ───────────────────────────────────────────────────────────

def _init_ctx(ctx: ContextTypes.DEFAULT_TYPE, uid: int, session_id: str) -> None:
    for key in _CTX_KEYS:
        ctx.user_data.pop(key, None)
    ctx.user_data["kv2_uid"]        = uid
    ctx.user_data["kv2_session_id"] = session_id


def _clear(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    for key in _CTX_KEYS:
        ctx.user_data.pop(key, None)


_CTX_KEYS = (
    "kv2_uid", "kv2_session_id",
    "kv2_live_data", "kv2_qr_data", "kv2_compare",
    "kv2_status", "kv2_verify_method", "kv2_verified_at", "kv2_mismatch_detail",
    "kv2_vneid_image_file_id", "kv2_vneid_image_path",
    "kv2_portrait_file_id", "kv2_portrait_path",
)
