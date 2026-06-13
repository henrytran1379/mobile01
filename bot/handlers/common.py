"""Handlers dùng chung: /start, /help, /cancel, error helpers."""
from telegram import Update, Message
from telegram.ext import ContextTypes, ConversationHandler
from bot.session import is_logged_in, get_role
from bot.keyboards import main_menu, main_menu_reply, session_expired_keyboard

PRIVATE_ONLY_CMDS = {"/register", "/login", "/profile", "/kyc", "/ekyc", "/add_wallet", "/wallets", "/credits"}


# ── Error helpers ─────────────────────────────────────────────────────────────

def parse_api_error(result: dict) -> str:
    """Trích thông báo lỗi từ API response."""
    detail = result.get("detail", {})
    if isinstance(detail, dict):
        return detail.get("message", "Đã xảy ra lỗi không xác định.")
    if isinstance(detail, str):
        return detail
    return "Đã xảy ra lỗi không xác định."


def get_error_code(result: dict) -> str:
    detail = result.get("detail", {})
    if isinstance(detail, dict):
        return detail.get("error_code", "")
    return ""


async def handle_api_error(message: Message, result: dict, next_hint: str = "") -> None:
    """Xử lý lỗi API thống nhất với hướng dẫn tiếp theo."""
    code = get_error_code(result)
    msg = parse_api_error(result)

    # Xử lý các lỗi đặc biệt
    if code in ("UNAUTHORIZED", "INVALID_TOKEN") or result.get("status_code") == 401:
        await message.reply_text(
            "⏰ *Phiên đăng nhập đã hết hạn*\n\n"
            "Lý do: Token xác thực không còn hiệu lực.\n\n"
            "👉 Vui lòng đăng nhập lại để tiếp tục.",
            parse_mode="Markdown",
            reply_markup=session_expired_keyboard(),
        )
        return

    if result.get("status_code") == 429:
        await message.reply_text(
            "⏳ *Quá nhiều yêu cầu*\n\n"
            "Bạn đã thử quá nhiều lần. Vui lòng chờ một lúc rồi thử lại.\n\n"
            f"👉 {next_hint or 'Thử lại sau vài phút.'}",
            parse_mode="Markdown",
        )
        return

    if result.get("status_code", 0) >= 500:
        await message.reply_text(
            "🔧 *Hệ thống đang gặp sự cố*\n\n"
            "Máy chủ tạm thời không phản hồi.\n\n"
            "👉 Vui lòng thử lại sau ít phút. Nếu vấn đề tiếp tục, liên hệ hỗ trợ.",
            parse_mode="Markdown",
        )
        return

    hint_text = f"\n\n👉 {next_hint}" if next_hint else ""
    await message.reply_text(f"❌ {msg}{hint_text}", parse_mode="Markdown")


# ── Commands ──────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    logged = is_logged_in(uid)
    name = update.effective_user.first_name or "bạn"
    role = get_role(uid) if logged else "USER"

    if logged:
        text = (
            f"👋 *Chào mừng trở lại, {name}!*\n\n"
            "🏠 *P2PSuperBot*\nVui lòng chọn chức năng:"
        )
    else:
        text = (
            "🤖 *P2PSuperBot*\n"
            "Mạng xác minh danh tính & ví tài sản số\n\n"
            "Bắt đầu bằng cách:\n"
            "📝 /register — Tạo tài khoản mới\n"
            "🔑 /login — Đăng nhập nếu đã có tài khoản\n"
            "🔄 /resend — Gửi lại thông tin đăng nhập\n"
            "❓ /help — Xem tất cả lệnh"
        )
    kb = main_menu_reply(role) if logged else main_menu(False)
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    logged = is_logged_in(uid)
    role = get_role(uid)

    if not logged:
        text = (
            "📋 *Hướng dẫn sử dụng P2PSuperBot*\n\n"
            "*Chưa có tài khoản?*\n"
            "/register — Đăng ký tài khoản mới\n\n"
            "*Đã có tài khoản?*\n"
            "/login — Đăng nhập\n\n"
            "*Không nhận được email?*\n"
            "/resend — Gửi lại thông tin đăng nhập\n\n"
            "💡 Tất cả lệnh chỉ dùng được trong *chat riêng* với bot."
        )
    elif role in ("ADMIN", "SUPER_ADMIN"):
        text = (
            "📋 *Lệnh Admin*\n\n"
            "/review\\_queue — Xem hàng chờ duyệt hồ sơ\n"
            "/security\\_alerts — Cảnh báo bảo mật\n"
            "/audit\\_logs — Nhật ký hệ thống\n\n"
            "📋 *Lệnh tài khoản*\n"
            "/profile — Hồ sơ cá nhân\n"
            "/credits — Số dư tín dụng\n"
            "/wallets — Danh sách ví\n"
            "/kyc — Xác minh KYC\n"
            "/2fa\\_setup — Bật xác thực 2 lớp\n"
            "/logout — Đăng xuất"
        )
    else:
        text = (
            "📋 *Tất cả lệnh của bạn*\n\n"
            "*Tài khoản*\n"
            "/profile — Xem hồ sơ\n"
            "/profile\\_update — Cập nhật hồ sơ\n"
            "/2fa\\_setup — Bật xác thực 2 lớp\n"
            "/logout — Đăng xuất\n\n"
            "*Xác minh danh tính*\n"
            "/kyc — Nộp KYC (ảnh CCCD)\n"
            "/ekyc — Nộp eKYC (file PDF)\n\n"
            "*Ví & Tín dụng*\n"
            "/wallets — Danh sách ví\n"
            "/add\\_wallet — Thêm ví mới\n"
            "/credits — Số dư và lịch sử tín dụng"
        )
    kb = main_menu_reply(role) if logged else main_menu(False)
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)


async def cmd_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    uid = update.effective_user.id
    logged = is_logged_in(uid)
    role = get_role(uid)
    await update.message.reply_text(
        "❌ Đã huỷ thao tác.\n\n👉 Chọn lệnh từ menu hoặc gõ /help để xem tất cả lệnh.",
        reply_markup=main_menu(logged, role),
    )
    return ConversationHandler.END


async def group_block(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Chặn lệnh nhạy cảm trong group chat."""
    if update.effective_chat.type != "private":
        cmd = update.message.text.split()[0].lower()
        if any(cmd.startswith(c) for c in PRIVATE_ONLY_CMDS):
            await update.message.reply_text(
                "🔒 Lệnh này chỉ dùng được trong *chat riêng* với bot.\n\n"
                "👉 Nhấn vào tên bot để mở chat riêng.",
                parse_mode="Markdown",
            )
