"""Handlers hệ thống tín dụng."""
from telegram import Update
from telegram.ext import ContextTypes
from bot import api_client as api
from bot.session import is_logged_in, get_token
from bot.keyboards import main_menu


async def cmd_credits(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    em = update.effective_message
    if not is_logged_in(uid):
        await em.reply_text(
            "🔒 *Cần đăng nhập trước*\n\n👉 Dùng /login để đăng nhập.",
            parse_mode="Markdown",
            reply_markup=main_menu(False),
        )
        return

    token = get_token(uid)
    balance = await api.get_credits(token)
    ledger = await api.get_ledger(token)

    if "detail" in balance:
        await em.reply_text(
            "❌ *Không thể tải thông tin tín dụng*\n\n"
            "📌 Hệ thống tạm thời gặp sự cố.\n\n"
            "👉 Thử lại sau vài giây hoặc dùng /logout rồi /login lại.",
            parse_mode="Markdown",
        )
        return

    bal = balance.get("balance", 0)
    used = balance.get("used", 0)

    text = (
        f"💰 *Tín dụng của bạn*\n\n"
        f"• Số dư hiện tại: *{bal:,.0f}* credits\n"
        f"• Đã sử dụng: {used:,.0f} credits\n"
    )

    if bal == 0:
        text += (
            "\n⚠️ *Số dư bằng 0*\n"
            "📌 Bạn cần có tín dụng để sử dụng các dịch vụ xác minh.\n\n"
            "👉 Liên hệ Admin để được cấp tín dụng."
        )

    if ledger and isinstance(ledger, list) and len(ledger) > 0:
        text += "\n\n📋 *5 giao dịch gần nhất:*\n"
        for entry in ledger[:5]:
            amount = entry.get("amount", 0)
            sign = "+" if amount > 0 else ""
            desc = entry.get("description", "")
            date = str(entry.get("created_at", ""))[:10]
            text += f"• {sign}{amount:,.0f} — {desc} _{date}_\n"

        if len(ledger) > 5:
            text += f"\n_...và {len(ledger) - 5} giao dịch khác_"
    else:
        text += "\n\n📋 *Chưa có giao dịch nào.*"

    text += "\n\n👉 Dùng /wallets hoặc /kyc để sử dụng tín dụng."

    await em.reply_text(text, parse_mode="Markdown")
