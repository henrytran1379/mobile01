"""Inline và Reply keyboards dùng chung."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove

REMOVE = ReplyKeyboardRemove()


def main_menu_reply(role: str = "USER") -> ReplyKeyboardMarkup:
    """Reply Keyboard chính sau khi đăng nhập — nhóm theo nghiệp vụ."""
    if role in ("ADMIN", "SUPER_ADMIN"):
        keys = [
            ["👤 My Profile",  "👥 Customer"],
            ["💱 P2P Trading", "🏪 Stores"],
            ["🧮 Tools",       "⚙️ Settings"],
            ["📊 Admin Queue", "❓ Help"],
        ]
    else:
        keys = [
            ["👤 My Profile",  "👥 Customer"],
            ["💱 P2P Trading", "🏪 Stores"],
            ["🧮 Tools",       "⚙️ Settings"],
            ["❓ Help"],
        ]
    return ReplyKeyboardMarkup(keys, resize_keyboard=True)


def main_menu(is_logged_in: bool = False, role: str = "USER") -> ReplyKeyboardMarkup:
    """Legacy keyboard — giữ backward compat, chuyển dần sang main_menu_reply."""
    if not is_logged_in:
        keys = [["/register", "/login"], ["/resend", "/help"]]
        return ReplyKeyboardMarkup(keys, resize_keyboard=True)
    return main_menu_reply(role)


def footer_kb(back_cb: str = "BACK_MAIN") -> list:
    """Hàng nút footer: Back | Main Menu | Clear Chat."""
    return [
        InlineKeyboardButton("🔙 Back",       callback_data=back_cb),
        InlineKeyboardButton("🏠 Main Menu",  callback_data="BACK_MAIN"),
        InlineKeyboardButton("🗑 Clear Chat", callback_data="CLEAR_CHAT"),
    ]


def network_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔴 TRON (TRX)", callback_data="net_TRON")],
        [InlineKeyboardButton("🟡 BSC (BNB)", callback_data="net_BSC")],
    ])


def review_keyboard(review_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Duyệt", callback_data=f"approve_{review_id}"),
            InlineKeyboardButton("❌ Từ chối", callback_data=f"reject_{review_id}"),
        ]
    ])


def cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([["/cancel"]], resize_keyboard=True)


# ── Action keyboards ──────────────────────────────────────────────────────────

def after_register_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔑 Đăng nhập", callback_data="goto_login")],
        [InlineKeyboardButton("🔄 Gửi lại email", callback_data="goto_resend")],
    ])


def login_fail_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Thử lại", callback_data="goto_login")],
        [InlineKeyboardButton("📧 Gửi lại mật khẩu", callback_data="goto_resend")],
    ])


def twofa_fail_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Nhập lại mã", callback_data="retry_2fa")],
        [InlineKeyboardButton("🆘 Dùng mã khôi phục", callback_data="use_recovery")],
    ])


def kyc_retry_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Nộp lại KYC", callback_data="goto_kyc")],
        [InlineKeyboardButton("❓ Hướng dẫn", callback_data="kyc_guide")],
    ])


def wallet_help_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Thêm ví", callback_data="goto_add_wallet")],
    ])


def session_expired_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔑 Đăng nhập lại", callback_data="goto_login")],
    ])
