"""Menu hệ thống P2PSuperBot.

Reply Keyboard (main menu) + Inline Keyboard (sub-menus).
Mọi handler dùng effective_message để tương thích cả message lẫn callback.
"""
from __future__ import annotations

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from bot.session import is_logged_in, get_token, get_role
from bot.keyboards import main_menu_reply, footer_kb

logger = logging.getLogger(__name__)

# ── Reply Keyboard button texts ───────────────────────────────────────────────
BTN_PROFILE  = "👤 My Profile"
BTN_CUSTOMER = "👥 Customer"
BTN_P2P      = "💱 P2P Trading"
BTN_STORES   = "🏪 Stores"
BTN_TOOLS    = "🧮 Tools"
BTN_SETTINGS = "⚙️ Settings"
BTN_HELP     = "❓ Help"

ALL_MENU_TEXTS = frozenset({
    BTN_PROFILE, BTN_CUSTOMER, BTN_P2P,
    BTN_STORES, BTN_TOOLS, BTN_SETTINGS, BTN_HELP,
})

# ── Callback data ─────────────────────────────────────────────────────────────
CB_MENU_PROFILE   = "MENU_PROFILE"
CB_MENU_CUSTOMER  = "MENU_CUSTOMER"
CB_MENU_P2P       = "MENU_P2P"
CB_MENU_STORES    = "MENU_STORES"
CB_MENU_TOOLS     = "MENU_TOOLS"
CB_MENU_SETTINGS  = "MENU_SETTINGS"
CB_MENU_HELP      = "MENU_HELP"
CB_BACK_MAIN      = "BACK_MAIN"
CB_CLEAR_CHAT     = "CLEAR_CHAT"

# Sub-menu command callbacks (shared với ConversationHandler entry points)
CB_START_KYC      = "kyc_vneid_start"   # đã có trong kyc_conv
CB_START_KYCVNEID = "start_kycvneid2"   # thêm vào kycvneid2_conv

_PLACEHOLDER = (
    "🔧 *Chức năng đang được phát triển*\n\n"
    "_Tính năng này sẽ sớm ra mắt._"
)


# ── Sub-menu inline keyboards ─────────────────────────────────────────────────

def _profile_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👤 Profile",    callback_data="CMD_PROFILE"),
            InlineKeyboardButton("📋 View KYC",   callback_data="CMD_VIEWKYC"),
        ],
        [
            InlineKeyboardButton("🪪 KYC",        callback_data=CB_START_KYC),
            InlineKeyboardButton("🆔 KYC VNeID",  callback_data=CB_START_KYCVNEID),
        ],
        [
            InlineKeyboardButton("💼 Wallet",     callback_data="CMD_WALLETS"),
            InlineKeyboardButton("💰 Credit",     callback_data="CMD_CREDITS"),
        ],
        [
            InlineKeyboardButton("🔐 2FA Setup",  callback_data="CMD_2FA"),
            InlineKeyboardButton("🏦 Bank",       callback_data="PH_BANK"),
        ],
        [
            InlineKeyboardButton("🛡 Security",   callback_data="PH_SECURITY"),
        ],
        footer_kb(CB_BACK_MAIN),
    ])


def _customer_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🪪 KYC VNeID",  callback_data="PH_CUST_KYC"),
            InlineKeyboardButton("📝 Update",     callback_data="PH_CUST_UPDATE"),
        ],
        [
            InlineKeyboardButton("🗑 Delete",     callback_data="PH_CUST_DELETE"),
            InlineKeyboardButton("🔍 Search",     callback_data="PH_CUST_SEARCH"),
        ],
        [
            InlineKeyboardButton("📋 History",    callback_data="PH_CUST_HISTORY"),
        ],
        footer_kb(CB_BACK_MAIN),
    ])


def _p2p_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📥 Buy USDT",   callback_data="PH_BUY_USDT"),
            InlineKeyboardButton("📤 Sell USDT",  callback_data="PH_SELL_USDT"),
        ],
        [
            InlineKeyboardButton("📋 Orders",     callback_data="PH_ORDERS"),
            InlineKeyboardButton("📊 Trades",     callback_data="PH_TRADES"),
        ],
        [
            InlineKeyboardButton("⚖️ Dispute",    callback_data="PH_DISPUTE"),
        ],
        footer_kb(CB_BACK_MAIN),
    ])


def _stores_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💳 Buy Credit",  callback_data="PH_BUY_CREDIT"),
            InlineKeyboardButton("⚡ Buy Energy",  callback_data="PH_BUY_ENERGY"),
        ],
        [
            InlineKeyboardButton("🔷 Buy TRX",    callback_data="PH_BUY_TRX"),
            InlineKeyboardButton("🟡 Buy BNB",    callback_data="PH_BUY_BNB"),
        ],
        footer_kb(CB_BACK_MAIN),
    ])


def _tools_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🧮 Máy tính P2P",   callback_data="PH_MONEY"),
            InlineKeyboardButton("🏦 Check Bank",      callback_data="PH_CHECK_BANK"),
        ],
        [
            InlineKeyboardButton("🔍 Check Address",   callback_data="PH_CHECK_ADDR"),
            InlineKeyboardButton("💹 Tỷ giá",          callback_data="PH_RATE"),
        ],
        footer_kb(CB_BACK_MAIN),
    ])


def _settings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🌐 Language",        callback_data="PH_LANGUAGE"),
            InlineKeyboardButton("🔔 Notifications",   callback_data="PH_NOTIF"),
        ],
        [
            InlineKeyboardButton("🗑 Clear Chat",      callback_data=CB_CLEAR_CHAT),
            InlineKeyboardButton("🚪 Logout",          callback_data="CMD_LOGOUT"),
        ],
        footer_kb(CB_BACK_MAIN),
    ])


def _help_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📖 Help",     callback_data="CMD_HELP"),
            InlineKeyboardButton("ℹ️ About",    callback_data="CMD_ABOUT"),
        ],
        [
            InlineKeyboardButton("🆘 Support",  callback_data="PH_SUPPORT"),
        ],
        footer_kb(CB_BACK_MAIN),
    ])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _require_login(uid: int) -> bool:
    return not is_logged_in(uid)


async def _send_main_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE, text: str | None = None):
    uid = update.effective_user.id
    role = get_role(uid)
    msg = text or (
        "🏠 *P2PSuperBot*\n\n"
        "Vui lòng chọn chức năng:"
    )
    em = update.effective_message
    await em.reply_text(msg, parse_mode="Markdown", reply_markup=main_menu_reply(role))


# ── Reply Keyboard handler (text buttons) ─────────────────────────────────────

async def handle_menu_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Bắt text từ Reply Keyboard buttons."""
    uid = update.effective_user.id
    if _require_login(uid):
        await update.message.reply_text(
            "🔒 *Cần đăng nhập trước*\n\n👉 Dùng /login.",
            parse_mode="Markdown",
        )
        return

    text = update.message.text.strip()
    em = update.effective_message

    if text == BTN_PROFILE:
        await em.reply_text(
            "👤 *My Profile*\nQuản lý hồ sơ và xác minh tài khoản.",
            parse_mode="Markdown",
            reply_markup=_profile_kb(),
        )
    elif text == BTN_CUSTOMER:
        await em.reply_text(
            "👥 *Customer*\nQuản lý khách hàng P2P của bạn.",
            parse_mode="Markdown",
            reply_markup=_customer_kb(),
        )
    elif text == BTN_P2P:
        await em.reply_text(
            "💱 *P2P Trading*\nQuản lý mua bán USDT.",
            parse_mode="Markdown",
            reply_markup=_p2p_kb(),
        )
    elif text == BTN_STORES:
        await em.reply_text(
            "🏪 *Stores*\nMua Credit, Energy và tài nguyên giao dịch.",
            parse_mode="Markdown",
            reply_markup=_stores_kb(),
        )
    elif text == BTN_TOOLS:
        await em.reply_text(
            "🧮 *Tools*\nCông cụ hỗ trợ giao dịch P2P.",
            parse_mode="Markdown",
            reply_markup=_tools_kb(),
        )
    elif text == BTN_SETTINGS:
        await em.reply_text(
            "⚙️ *Settings*\nCài đặt hệ thống.",
            parse_mode="Markdown",
            reply_markup=_settings_kb(),
        )
    elif text == BTN_HELP:
        await em.reply_text(
            "❓ *Help*\nHướng dẫn sử dụng P2PSuperBot.",
            parse_mode="Markdown",
            reply_markup=_help_kb(),
        )


# ── Callback: Back to Main Menu ───────────────────────────────────────────────

async def cb_back_main(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = update.effective_user.id
    role = get_role(uid)
    await query.message.reply_text(
        "🏠 *P2PSuperBot*\n\nVui lòng chọn chức năng:",
        parse_mode="Markdown",
        reply_markup=main_menu_reply(role),
    )


# ── Callback: Clear Chat ──────────────────────────────────────────────────────

async def cb_clear_chat(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("🗑 Đang xóa lịch sử...")
    chat_id = query.message.chat_id
    msg_id  = query.message.message_id

    ids_to_delete = list(range(max(1, msg_id - 199), msg_id + 1))
    for i in range(0, len(ids_to_delete), 100):
        try:
            await ctx.bot.delete_messages(chat_id=chat_id, message_ids=ids_to_delete[i:i+100])
        except Exception:
            pass

    uid = update.effective_user.id
    role = get_role(uid)
    await ctx.bot.send_message(
        chat_id=chat_id,
        text="🗑 *Lịch sử chat đã được xóa.*\n\nVui lòng chọn chức năng:",
        parse_mode="Markdown",
        reply_markup=main_menu_reply(role),
    )


# ── Callback: Sub-menus (từ inline buttons) ───────────────────────────────────

async def cb_menu_profile(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "👤 *My Profile*\nQuản lý hồ sơ và xác minh tài khoản.",
        parse_mode="Markdown",
        reply_markup=_profile_kb(),
    )


async def cb_menu_customer(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "👥 *Customer*\nQuản lý khách hàng P2P của bạn.",
        parse_mode="Markdown",
        reply_markup=_customer_kb(),
    )


async def cb_menu_p2p(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "💱 *P2P Trading*\nQuản lý mua bán USDT.",
        parse_mode="Markdown",
        reply_markup=_p2p_kb(),
    )


async def cb_menu_stores(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "🏪 *Stores*\nMua Credit, Energy và tài nguyên giao dịch.",
        parse_mode="Markdown",
        reply_markup=_stores_kb(),
    )


async def cb_menu_tools(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "🧮 *Tools*\nCông cụ hỗ trợ giao dịch P2P.",
        parse_mode="Markdown",
        reply_markup=_tools_kb(),
    )


async def cb_menu_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "⚙️ *Settings*\nCài đặt hệ thống.",
        parse_mode="Markdown",
        reply_markup=_settings_kb(),
    )


async def cb_menu_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "❓ *Help*\nHướng dẫn sử dụng P2PSuperBot.",
        parse_mode="Markdown",
        reply_markup=_help_kb(),
    )


# ── Callback: Commands từ sub-menu ────────────────────────────────────────────

async def cb_cmd_profile(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    from bot.handlers.profile import cmd_profile
    query = update.callback_query
    await query.answer()
    await cmd_profile(update, ctx)


async def cb_cmd_viewkyc(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    from bot.handlers.viewkyc import cmd_viewkyc
    query = update.callback_query
    await query.answer()
    await cmd_viewkyc(update, ctx)


async def cb_cmd_wallets(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    from bot.handlers.wallet import cmd_wallets
    query = update.callback_query
    await query.answer()
    await cmd_wallets(update, ctx)


async def cb_cmd_credits(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    from bot.handlers.credits import cmd_credits
    query = update.callback_query
    await query.answer()
    await cmd_credits(update, ctx)


async def cb_cmd_2fa(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    from bot.handlers.auth import cmd_2fa_setup
    query = update.callback_query
    await query.answer()
    await cmd_2fa_setup(update, ctx)


async def cb_cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    from bot.handlers.common import cmd_help
    query = update.callback_query
    await query.answer()
    await cmd_help(update, ctx)


async def cb_cmd_about(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "ℹ️ *P2PSuperBot*\n\n"
        "Hệ thống xác minh danh tính & quản lý ví tài sản số cho Exchanger P2P.\n\n"
        "_Phiên bản: 1.0.0_",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([footer_kb(CB_BACK_MAIN)]),
    )


async def cb_cmd_logout(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    from bot.handlers.auth import cmd_logout
    query = update.callback_query
    await query.answer()
    # Simulate message context for logout handler
    await cmd_logout(update, ctx)


# ── Placeholder callback ──────────────────────────────────────────────────────

async def cb_placeholder(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Chức năng đang phát triển", show_alert=False)
    await query.message.reply_text(
        _PLACEHOLDER,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([footer_kb(CB_BACK_MAIN)]),
    )
