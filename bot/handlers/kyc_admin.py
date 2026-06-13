"""Admin KYC review commands.

/kyc_queue  — list pending submissions
/kyc_view   — view a specific submission (sends photos + extracted data)
Inline buttons: [✅ Duyệt] [❌ Từ chối] per submission
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from bot import api_client as api
from bot.session import is_logged_in, get_token, get_role
from bot.keyboards import main_menu, cancel_keyboard
from bot.handlers.common import parse_api_error

logger = logging.getLogger(__name__)

KYC_REJECT_REASON = 0   # state for reject reason conversation

_ADMIN_ROLES = ("ADMIN", "SUPER_ADMIN")


def _is_admin(uid: int) -> bool:
    return get_role(uid) in _ADMIN_ROLES


# ── /kyc_queue ────────────────────────────────────────────────────────────────

async def cmd_kyc_queue(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_logged_in(uid) or not _is_admin(uid):
        await update.message.reply_text("🚫 Chỉ admin mới dùng được lệnh này.")
        return

    token = get_token(uid)
    result = await api.get_kyc_queue(token)
    queue = result.get("queue", [])

    if not queue:
        await update.message.reply_text(
            "✅ *Hàng chờ KYC trống*\n\nKhông có hồ sơ nào đang chờ xét duyệt.",
            parse_mode="Markdown",
        )
        return

    text = f"📋 *Hàng chờ KYC — {len(queue)} hồ sơ*\n\n"
    buttons = []
    for i, item in enumerate(queue[:10], 1):
        pid = item.get("kyc_profile_id", "")
        name = item.get("full_name") or "—"
        face = item.get("face_match_score")
        face_str = f"{int(face * 100)}%" if face else "—"
        source = item.get("extraction_source", "—")
        submitted = (item.get("submitted_at") or "")[:10]
        uc = item.get("user_code", "—")

        text += (
            f"*{i}.* `{uc}` — {name}\n"
            f"   🎭 Mặt: {face_str} | 📡 {source} | 📅 {submitted}\n\n"
        )
        buttons.append([InlineKeyboardButton(
            f"👁 Xem #{i}: {uc}",
            callback_data=f"kyc_view_{pid[:24]}",
        )])

    await update.message.reply_text(
        text.strip(),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# ── View submission ───────────────────────────────────────────────────────────

async def cb_kyc_view(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = update.effective_user.id
    if not _is_admin(uid):
        return

    # Extract full profile ID stored in context or callback data
    pid = query.data.replace("kyc_view_", "")
    # Try to get full ID from stored map
    pid = ctx.bot_data.get(f"kyc_pid_{pid}", pid)

    token = get_token(uid)
    result = await api.get_kyc_detail(token, pid)

    if result.get("error_code"):
        await query.message.reply_text(f"❌ {parse_api_error(result)}")
        return

    # Build info text
    face = result.get("face_match_score")
    face_str = f"{int(face * 100)}% ({result.get('face_match_algorithm', '—')})" if face else "—"
    text = (
        f"🪪 *Hồ sơ KYC*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"👤 Họ tên: {result.get('full_name') or '—'}\n"
        f"🎂 Ngày sinh: {result.get('date_of_birth') or '—'}\n"
        f"⚧ Giới tính: {result.get('gender') or '—'}\n"
        f"🪪 CCCD: `{result.get('personal_id_masked') or '—'}`\n"
        f"📍 Địa chỉ: {result.get('address') or '—'}\n"
        f"📅 Ngày cấp: {result.get('issue_date') or '—'}\n"
        f"🎭 Khớp mặt: {face_str}\n"
        f"📡 Nguồn: {result.get('extraction_source') or '—'}\n"
        f"📋 Trạng thái: {result.get('status') or '—'}\n"
        f"━━━━━━━━━━━━━━━━"
    )
    review_kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Duyệt", callback_data=f"kyc_approve_{pid}"),
            InlineKeyboardButton("❌ Từ chối", callback_data=f"kyc_reject_start_{pid}"),
        ]
    ])
    await query.message.reply_text(text, parse_mode="Markdown", reply_markup=review_kb)

    # Send document images
    docs = result.get("documents", [])
    for doc in docs:
        doc_type = doc.get("doc_type", "")
        file_path = doc.get("file_path", "")
        label = {"FRONT": "Mặt trước", "BACK": "Mặt sau", "SELFIE": "Selfie"}.get(doc_type, doc_type)
        try:
            import aiofiles
            async with aiofiles.open(file_path, "rb") as f:
                photo_bytes = await f.read()
            await query.message.reply_photo(photo=photo_bytes, caption=f"📷 {label}")
        except Exception as exc:
            await query.message.reply_text(f"⚠️ Không tải được ảnh {label}: {exc}")


# ── Approve ───────────────────────────────────────────────────────────────────

async def cb_kyc_approve(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = update.effective_user.id
    if not _is_admin(uid):
        return

    pid = query.data.replace("kyc_approve_", "")
    token = get_token(uid)
    result = await api.kyc_approve(token, pid)

    if result.get("success"):
        tg_uid = result.get("telegram_user_id")
        await query.message.reply_text(
            "✅ *KYC đã được duyệt*\n\n"
            f"📌 User: `{result.get('user_id', '')[:8]}...`\n"
            "_Người dùng sẽ nhận thông báo._",
            parse_mode="Markdown",
        )
        # Notify user if possible
        if tg_uid:
            try:
                await ctx.bot.send_message(
                    chat_id=tg_uid,
                    text=(
                        "✅ *KYC của bạn đã được xác minh!*\n\n"
                        "🎉 Tài khoản đã đạt Level 3 — Manual Approved.\n\n"
                        "👉 Dùng /profile để xem trạng thái tài khoản."
                    ),
                    parse_mode="Markdown",
                )
            except Exception:
                pass
    else:
        await query.message.reply_text(f"❌ {parse_api_error(result)}")


# ── Reject ────────────────────────────────────────────────────────────────────

async def cb_kyc_reject_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Start reject conversation — ask for reason."""
    query = update.callback_query
    await query.answer()
    uid = update.effective_user.id
    if not _is_admin(uid):
        return

    pid = query.data.replace("kyc_reject_start_", "")
    ctx.user_data["kyc_reject_pid"] = pid

    await query.message.reply_text(
        "📝 *Từ chối KYC*\n\n"
        "Nhập lý do từ chối (bắt buộc):\n"
        "_Ví dụ: Ảnh mờ, không đọc được thông tin_",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard(),
    )
    return KYC_REJECT_REASON


async def kyc_reject_reason(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Receive rejection reason and submit."""
    uid = update.effective_user.id
    reason = update.message.text.strip()
    pid = ctx.user_data.pop("kyc_reject_pid", None)

    if not pid:
        await update.message.reply_text("❌ Phiên xét duyệt đã hết hạn. Dùng /kyc_queue lại.")
        return ConversationHandler.END

    if len(reason) < 5:
        await update.message.reply_text(
            "⚠️ Lý do quá ngắn (tối thiểu 5 ký tự). Nhập lại:",
            parse_mode="Markdown",
        )
        ctx.user_data["kyc_reject_pid"] = pid
        return KYC_REJECT_REASON

    token = get_token(uid)
    result = await api.kyc_reject(token, pid, reason)

    if result.get("success"):
        tg_uid = result.get("telegram_user_id")
        await update.message.reply_text(
            f"✅ *KYC đã bị từ chối*\n\n📌 Lý do: {reason}\n\n_Người dùng sẽ nhận thông báo._",
            parse_mode="Markdown",
            reply_markup=main_menu(True, get_role(uid)),
        )
        # Notify user
        if tg_uid:
            try:
                await update.get_bot().send_message(
                    chat_id=tg_uid,
                    text=(
                        "❌ *Hồ sơ KYC của bạn bị từ chối*\n\n"
                        f"📌 *Lý do:* {reason}\n\n"
                        "👉 Bạn có thể nộp lại hồ sơ mới bằng lệnh /kyc."
                    ),
                    parse_mode="Markdown",
                )
            except Exception:
                pass
    else:
        await update.message.reply_text(f"❌ {parse_api_error(result)}")

    return ConversationHandler.END
