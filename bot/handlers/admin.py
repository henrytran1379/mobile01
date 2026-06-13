"""Handlers cho Admin: review queue, security alerts, approve/reject."""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot import api_client as api
from bot.session import is_logged_in, get_token, get_role
from bot.keyboards import review_keyboard, cancel_keyboard, main_menu
from bot.handlers.common import parse_api_error

REJECT_REASON = 0


def _require_admin(uid: int) -> bool:
    return is_logged_in(uid) and get_role(uid) in ("ADMIN", "SUPER_ADMIN")


async def cmd_review_queue(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_logged_in(uid):
        await update.message.reply_text(
            "🔒 *Cần đăng nhập trước*\n\n👉 Dùng /login để đăng nhập.",
            parse_mode="Markdown",
        )
        return
    if not _require_admin(uid):
        await update.message.reply_text(
            "🚫 *Không có quyền truy cập*\n\n"
            "📌 Lệnh này chỉ dành cho Admin.\n\n"
            "👉 Nếu bạn cho rằng đây là nhầm lẫn, liên hệ Super Admin.",
            parse_mode="Markdown",
        )
        return

    token = get_token(uid)
    reviews = await api.get_reviews(token)

    if isinstance(reviews, dict) and "detail" in reviews:
        await update.message.reply_text(
            "❌ *Không thể tải hàng chờ duyệt*\n\n"
            "📌 Hệ thống tạm thời gặp sự cố.\n\n"
            "👉 Thử lại sau vài giây.",
            parse_mode="Markdown",
        )
        return

    if not reviews:
        await update.message.reply_text(
            "✅ *Hàng chờ duyệt trống*\n\n"
            "📌 Không có hồ sơ nào đang chờ xét duyệt.\n\n"
            "👉 Dùng /security\\_alerts để kiểm tra cảnh báo bảo mật.",
            parse_mode="Markdown",
        )
        return

    await update.message.reply_text(
        f"📋 *Hàng chờ duyệt — {len(reviews)} hồ sơ*\n\n"
        "👉 Nhấn *Duyệt* hoặc *Từ chối* cho từng hồ sơ:",
        parse_mode="Markdown",
    )

    for review in reviews[:10]:
        rid = review.get("id", "")
        rtype = review.get("review_type", "N/A")
        date = str(review.get("created_at", ""))[:10]
        text = (
            f"🆔 ID: `{rid}`\n"
            f"👤 User: `{review.get('user_code', 'N/A')}`\n"
            f"📂 Loại: *{rtype}*\n"
            f"📅 Ngày nộp: {date}"
        )
        await update.message.reply_text(
            text, parse_mode="Markdown", reply_markup=review_keyboard(str(rid))
        )

    if len(reviews) > 10:
        await update.message.reply_text(
            f"📌 _Hiển thị 10/{len(reviews)} hồ sơ. Duyệt xong để xem thêm._",
            parse_mode="Markdown",
        )


async def handle_approve(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id

    if not _require_admin(uid):
        await query.answer("🚫 Bạn không có quyền thực hiện thao tác này.", show_alert=True)
        return

    review_id = query.data.replace("approve_", "")
    token = get_token(uid)
    result = await api.approve_review(token, review_id)

    if result.get("success"):
        await query.edit_message_text(
            f"✅ *Đã duyệt hồ sơ*\n\n"
            f"🆔 ID: `{review_id}`\n\n"
            "📌 User sẽ nhận được thông báo xác nhận.\n"
            "👉 Dùng /review\\_queue để xem hồ sơ tiếp theo.",
            parse_mode="Markdown",
        )
    else:
        msg = parse_api_error(result)
        await query.edit_message_text(
            f"❌ *Duyệt thất bại*\n\n"
            f"📌 *Lý do:* {msg}\n\n"
            "👉 Thử lại hoặc kiểm tra lại trạng thái hồ sơ.",
            parse_mode="Markdown",
        )


async def handle_reject_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id

    if not _require_admin(uid):
        await query.answer("🚫 Bạn không có quyền thực hiện thao tác này.", show_alert=True)
        return ConversationHandler.END

    review_id = query.data.replace("reject_", "")
    ctx.user_data["reject_review_id"] = review_id
    await query.message.reply_text(
        f"✏️ *Từ chối hồ sơ* `{review_id}`\n\n"
        "📌 Lý do từ chối sẽ được gửi đến người dùng.\n"
        "Vui lòng mô tả rõ ràng để user biết cách khắc phục.\n\n"
        "👉 Nhập lý do từ chối:",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard(),
    )
    return REJECT_REASON


async def handle_reject_reason(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    review_id = ctx.user_data.get("reject_review_id")
    reason = update.message.text.strip()
    token = get_token(uid)
    result = await api.reject_review(token, review_id, reason)

    if result.get("success"):
        await update.message.reply_text(
            f"✅ *Đã từ chối hồ sơ*\n\n"
            f"🆔 ID: `{review_id}`\n"
            f"📝 Lý do: _{reason}_\n\n"
            "📌 User sẽ nhận được thông báo và lý do từ chối.\n"
            "👉 Dùng /review\\_queue để xem hồ sơ tiếp theo.",
            parse_mode="Markdown",
            reply_markup=main_menu(True, get_role(uid)),
        )
    else:
        msg = parse_api_error(result)
        await update.message.reply_text(
            f"❌ *Từ chối thất bại*\n\n"
            f"📌 *Lý do:* {msg}\n\n"
            "👉 Thử lại bằng /review\\_queue.",
            parse_mode="Markdown",
        )
    return ConversationHandler.END


async def cmd_security_alerts(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not _require_admin(uid):
        await update.message.reply_text(
            "🚫 *Không có quyền truy cập*\n\n"
            "📌 Lệnh này chỉ dành cho Admin.",
            parse_mode="Markdown",
        )
        return

    token = get_token(uid)
    result = await api.get_reviews(token, review_type="security_alert")

    if isinstance(result, dict) and "detail" in result:
        await update.message.reply_text(
            "❌ *Không thể tải cảnh báo bảo mật*\n\n"
            "📌 Hệ thống tạm thời gặp sự cố.\n\n"
            "👉 Thử lại sau vài giây.",
            parse_mode="Markdown",
        )
        return

    if not result:
        await update.message.reply_text(
            "✅ *Không có cảnh báo bảo mật*\n\n"
            "📌 Hệ thống đang hoạt động bình thường.\n\n"
            "👉 Dùng /review\\_queue để xem hồ sơ chờ duyệt.",
            parse_mode="Markdown",
        )
        return

    text = f"🚨 *Cảnh báo bảo mật — {len(result)} cảnh báo*\n\n"
    for alert in result[:10]:
        severity = alert.get("severity", "INFO")
        emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(severity, "⚪")
        date = str(alert.get("created_at", ""))[:16]
        text += (
            f"{emoji} *[{severity}]* {alert.get('description', 'N/A')}\n"
            f"  👤 User: `{alert.get('user_code', 'N/A')}` — {date}\n\n"
        )

    text += "👉 Kiểm tra từng cảnh báo và xử lý kịp thời."
    await update.message.reply_text(text, parse_mode="Markdown")
