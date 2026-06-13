"""Handlers ví tài sản số."""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot import api_client as api
from bot.session import is_logged_in, get_token, get_role
from bot.keyboards import main_menu, network_keyboard, cancel_keyboard, wallet_help_keyboard
from bot.handlers.common import parse_api_error

WALLET_ADDRESS = 0

_LOGIN_REQUIRED = "🔒 *Cần đăng nhập trước*\n\n👉 Dùng /login để đăng nhập."


async def cmd_wallets(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    em = update.effective_message
    if not is_logged_in(uid):
        await em.reply_text(_LOGIN_REQUIRED, parse_mode="Markdown", reply_markup=main_menu(False))
        return

    token = get_token(uid)
    result = await api.list_wallets(token)

    if isinstance(result, dict) and "detail" in result:
        await em.reply_text(
            "❌ *Không thể tải danh sách ví*\n\n"
            "📌 Hệ thống tạm thời gặp sự cố.\n\n"
            "👉 Thử lại sau vài giây hoặc dùng /logout rồi /login lại.",
            parse_mode="Markdown",
        )
        return

    if not result:
        await em.reply_text(
            "💼 *Danh sách ví*\n\n"
            "📌 Bạn chưa có ví nào được liên kết.\n\n"
            "👉 *Thêm ví để:*\n"
            "• Nhận và gửi tài sản số\n"
            "• Xác minh quyền sở hữu ví\n"
            "• Tham gia các giao dịch P2P\n\n"
            "Dùng /add\\_wallet để thêm ví đầu tiên.",
            parse_mode="Markdown",
            reply_markup=wallet_help_keyboard(),
        )
        return

    pending = [w for w in result if not w.get("is_verified")]

    lines = [f"💼 *Danh sách ví của bạn ({len(result)} ví):*\n"]
    for w in result:
        if w.get("is_verified"):
            lines.append(f"✅ *{w.get('network')}* — Đã xác minh\n  `{w.get('address')}`\n")
        else:
            lines.append(f"⏳ *{w.get('network')}* — Đang chờ xác minh\n  `{w.get('address')}`\n")

    if pending:
        lines.append(f"\n📌 *{len(pending)} ví đang chờ xác minh.*\nThời gian xác minh thường 1–3 ngày làm việc.")

    lines.append("\n👉 Dùng /add\\_wallet để thêm ví mới.")
    await em.reply_text("\n".join(lines), parse_mode="Markdown")


async def cmd_add_wallet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_logged_in(uid):
        await update.message.reply_text(_LOGIN_REQUIRED, parse_mode="Markdown", reply_markup=main_menu(False))
        return ConversationHandler.END

    await update.message.reply_text(
        "➕ *Thêm ví tài sản số*\n\n"
        "📌 *Mạng được hỗ trợ:*\n"
        "• 🔴 TRON (TRX, USDT-TRC20)\n"
        "• 🟡 BSC (BNB, USDT-BEP20)\n\n"
        "👉 Chọn mạng blockchain:",
        parse_mode="Markdown",
        reply_markup=network_keyboard(),
    )
    return WALLET_ADDRESS


async def network_selected(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    network = query.data.replace("net_", "")
    ctx.user_data["wallet_network"] = network

    await query.edit_message_text(
        f"✅ Đã chọn mạng *{network}*\n\n"
        f"📌 *Lưu ý:* Chỉ nhập địa chỉ ví trên mạng *{network}*.\n"
        f"Nhập sai mạng có thể mất tài sản vĩnh viễn.\n\n"
        "👉 Nhập địa chỉ ví:",
        parse_mode="Markdown",
    )
    await query.message.reply_text("📝 Nhập địa chỉ ví:", reply_markup=cancel_keyboard())
    return WALLET_ADDRESS


async def wallet_address(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    address = update.message.text.strip()
    network = ctx.user_data.get("wallet_network", "TRON")
    token = get_token(uid)
    result = await api.add_wallet(token, network, address)

    if result.get("success") or result.get("wallet_id"):
        await update.message.reply_text(
            f"✅ *Thêm ví thành công!*\n\n"
            f"🌐 Mạng: *{network}*\n"
            f"📬 Địa chỉ: `{address}`\n\n"
            "📌 *Trạng thái:* Đang chờ xác minh quyền sở hữu.\n\n"
            "⏱ *Quy trình xác minh:*\n"
            "1. Admin sẽ xác minh ví trong vòng 1–3 ngày\n"
            "2. Bạn sẽ nhận thông báo khi ví được duyệt\n"
            "3. Sau khi xác minh, ví sẵn sàng sử dụng\n\n"
            "👉 Dùng /wallets để xem trạng thái ví.",
            parse_mode="Markdown",
            reply_markup=main_menu(True, get_role(uid)),
        )
    else:
        msg = parse_api_error(result)
        await update.message.reply_text(
            f"❌ *Thêm ví thất bại*\n\n"
            f"📌 *Lý do:* {msg}\n\n"
            "👉 *Kiểm tra lại:*\n"
            f"• Địa chỉ ví có đúng định dạng mạng *{network}* không?\n"
            "• Địa chỉ này đã được liên kết chưa?\n\n"
            "Dùng /add\\_wallet để thử lại.",
            parse_mode="Markdown",
            reply_markup=main_menu(True, get_role(uid)),
        )
    return ConversationHandler.END
