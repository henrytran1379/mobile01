"""Handlers cho Super Admin."""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot import api_client as api
from bot.session import is_logged_in, get_token, get_role
from bot.keyboards import cancel_keyboard, main_menu

CREATE_ADMIN_EMAIL, DISABLE_ADMIN_ID = range(2)


def _require_super(uid: int) -> bool:
    return is_logged_in(uid) and get_role(uid) == "SUPER_ADMIN"


async def cmd_create_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not _require_super(uid):
        await update.message.reply_text("❌ Chỉ Super Admin mới dùng được lệnh này.")
        return ConversationHandler.END

    await update.message.reply_text(
        "📧 Nhập email của tài khoản sẽ được cấp quyền Admin:",
        reply_markup=cancel_keyboard(),
    )
    return CREATE_ADMIN_EMAIL


async def create_admin_email(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    email = update.message.text.strip()
    token = get_token(uid)

    result = await api._post("/admin/create", {"email": email}, token)

    if result.get("success"):
        await update.message.reply_text(
            f"✅ *Đã tạo Admin* cho email `{email}`",
            parse_mode="Markdown",
            reply_markup=main_menu(True, "SUPER_ADMIN"),
        )
    else:
        msg = result.get("detail", {})
        if isinstance(msg, dict):
            msg = msg.get("message", "Lỗi tạo Admin")
        await update.message.reply_text(f"❌ {msg}", reply_markup=main_menu(True, "SUPER_ADMIN"))
    return ConversationHandler.END


async def cmd_audit_logs(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not _require_super(uid):
        await update.message.reply_text("❌ Chỉ Super Admin mới dùng được lệnh này.")
        return

    token = get_token(uid)
    result = await api._get("/admin/audit-logs", token)

    if isinstance(result, dict) and "detail" in result:
        await update.message.reply_text("❌ Không lấy được audit logs.")
        return

    if not result:
        await update.message.reply_text("📋 Chưa có audit log nào.")
        return

    text = "📋 *Audit Logs (10 gần nhất):*\n\n"
    for log in result[:10]:
        text += (
            f"• `{log.get('action', 'N/A')}` — {log.get('actor', 'N/A')}\n"
            f"  {str(log.get('created_at', ''))[:16]}\n\n"
        )
    await update.message.reply_text(text, parse_mode="Markdown")
