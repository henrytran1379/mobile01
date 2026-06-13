"""Handlers đăng ký, đăng nhập, đổi mật khẩu, 2FA, đăng xuất."""
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot import api_client as api
from bot.session import save_session, delete_session, get_token, is_logged_in, get_role
from bot.keyboards import (
    main_menu, main_menu_reply, cancel_keyboard,
    after_register_keyboard, login_fail_keyboard, twofa_fail_keyboard,
    session_expired_keyboard,
)
from bot.handlers.common import parse_api_error, get_error_code

# States
(
    REG_EMAIL,
    RESEND_EMAIL,
    LOGIN_EMAIL, LOGIN_PASSWORD, LOGIN_2FA,
    CHANGE_PW_OLD, CHANGE_PW_NEW, CHANGE_PW_CONFIRM,
    FA_CODE,
) = range(9)

_PW_RULES = "Tối thiểu 8 ký tự, gồm chữ hoa, chữ thường và số."


# ── REGISTER ──────────────────────────────────────────────────────────────────

async def cmd_register(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.message.reply_text(
            "🔒 Lệnh này chỉ dùng được trong *chat riêng* với bot.",
            parse_mode="Markdown",
        )
        return ConversationHandler.END
    await update.message.reply_text(
        "📝 *Đăng ký tài khoản P2PSuperBot*\n\n"
        "Nhập địa chỉ email của bạn.\n"
        "Hệ thống sẽ gửi *User Code* và *mật khẩu tạm thời* qua email.\n\n"
        "📧 Nhập email:",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard(),
    )
    return REG_EMAIL


async def reg_email(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    await update.message.reply_text("⏳ Đang xử lý...")
    result = await api.register(email)

    if result.get("success"):
        msg = result.get("message", "")
        is_resend = "not verified" in msg or "new verification" in msg

        if is_resend:
            text = (
                "🔄 *Email đã đăng ký nhưng chưa xác minh*\n\n"
                "📌 *Trạng thái:* Tài khoản tồn tại, chưa đăng nhập lần nào.\n"
                "📬 *Hành động:* Chúng tôi vừa gửi lại thông tin đăng nhập.\n\n"
                "👉 *Bước tiếp theo:*\n"
                "1. Kiểm tra hộp thư đến\n"
                "2. Kiểm tra thư mục *Spam / Junk*\n"
                "3. Dùng /login với User Code và mật khẩu tạm thời\n\n"
                "Vẫn không nhận được? Nhấn nút bên dưới để gửi lại."
            )
        else:
            text = (
                "✅ *Đăng ký thành công!*\n\n"
                "📌 *Trạng thái:* Tài khoản đã được tạo.\n"
                "📬 *Hành động:* Email chứa thông tin đăng nhập đã được gửi.\n\n"
                "👉 *Bước tiếp theo:*\n"
                "1. Kiểm tra hộp thư đến (từ P2PSuperBot)\n"
                "2. Kiểm tra thư mục *Spam / Junk* nếu không thấy\n"
                "3. Dùng /login với User Code và mật khẩu tạm thời\n"
                "4. Đổi mật khẩu ngay sau khi đăng nhập lần đầu\n\n"
                "Vẫn không nhận được email? Nhấn *Gửi lại email* bên dưới."
            )
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=after_register_keyboard(),
        )
    else:
        code = get_error_code(result)
        if code == "EMAIL_REGISTERED":
            await update.message.reply_text(
                "⚠️ *Email này đã được đăng ký và đã kích hoạt*\n\n"
                "📌 *Trạng thái:* Tài khoản đã tồn tại.\n\n"
                "👉 *Bạn muốn làm gì?*\n"
                "• Dùng /login để đăng nhập\n"
                "• Dùng /resend nếu quên mật khẩu\n\n"
                "Nếu không phải bạn đăng ký email này, liên hệ hỗ trợ.",
                parse_mode="Markdown",
                reply_markup=login_fail_keyboard(),
            )
        else:
            msg = parse_api_error(result)
            await update.message.reply_text(
                f"❌ *Đăng ký thất bại*\n\n{msg}\n\n"
                "👉 Kiểm tra lại email và thử lại. Nếu lỗi tiếp tục, dùng /help.",
                parse_mode="Markdown",
                reply_markup=main_menu(False),
            )
    return ConversationHandler.END


# ── LOGIN ─────────────────────────────────────────────────────────────────────

async def cmd_login(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.message.reply_text(
            "🔒 Lệnh này chỉ dùng được trong *chat riêng* với bot.",
            parse_mode="Markdown",
        )
        return ConversationHandler.END
    if is_logged_in(update.effective_user.id):
        await update.message.reply_text(
            "✅ *Bạn đã đăng nhập rồi*\n\n"
            "👉 Dùng các lệnh bên dưới để tiếp tục:\n"
            "/profile — Xem hồ sơ\n"
            "/wallets — Quản lý ví\n"
            "/credits — Số dư tín dụng\n"
            "/logout — Đăng xuất",
            parse_mode="Markdown",
            reply_markup=main_menu(True, get_role(update.effective_user.id)),
        )
        return ConversationHandler.END
    await update.message.reply_text(
        "🔑 *Đăng nhập P2PSuperBot*\n\n"
        "Nhập email hoặc User Code của bạn\n"
        "_(ví dụ: user@email.com hoặc USR123456)_",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard(),
    )
    return LOGIN_EMAIL


async def login_email(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["login_email"] = update.message.text.strip()
    await update.message.reply_text(
        "🔒 Nhập mật khẩu của bạn:\n_(Tin nhắn này sẽ bị xoá ngay sau khi gửi)_",
        parse_mode="Markdown",
    )
    return LOGIN_PASSWORD


async def login_password(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    email = ctx.user_data["login_email"]
    password = update.message.text
    await update.message.delete()
    await update.message.reply_text("⏳ Đang xác thực...")
    result = await api.login(email, password)

    if result.get("requires_password_change"):
        ctx.user_data["change_pw_user_id"] = result.get("user_id")
        ctx.user_data["change_pw_temp"] = password
        await update.message.reply_text(
            "🔐 *Đăng nhập lần đầu — Cần đổi mật khẩu*\n\n"
            "📌 *Lý do:* Bạn đang dùng mật khẩu tạm thời từ email.\n"
            "Vì lý do bảo mật, bạn phải đặt mật khẩu mới trước khi tiếp tục.\n\n"
            f"📏 *Yêu cầu mật khẩu:* {_PW_RULES}\n\n"
            "👉 Nhập mật khẩu mới:",
            parse_mode="Markdown",
            reply_markup=cancel_keyboard(),
        )
        return CHANGE_PW_NEW

    if result.get("requires_2fa"):
        ctx.user_data["pending_token"] = result.get("pending_token")
        await update.message.reply_text(
            "🛡 *Xác thực 2 lớp (2FA)*\n\n"
            "📌 Tài khoản của bạn đã bật bảo mật 2 lớp.\n\n"
            "👉 Mở ứng dụng *Google Authenticator* và nhập mã 6 số:\n\n"
            "_(Mã hết hạn sau 30 giây. Nếu mất điện thoại, dùng mã khôi phục.)_",
            parse_mode="Markdown",
            reply_markup=cancel_keyboard(),
        )
        return LOGIN_2FA

    if result.get("access_token"):
        uid = update.effective_user.id
        save_session(uid, result)
        role = result.get("role", "USER")
        await update.message.reply_text(
            f"✅ *Đăng nhập thành công!*\n\n"
            f"👤 User Code: `{result.get('user_code')}`\n"
            f"🎭 Vai trò: {role}\n\n"
            "🏠 *P2PSuperBot*\nVui lòng chọn chức năng:",
            parse_mode="Markdown",
            reply_markup=main_menu_reply(role),
        )
        return ConversationHandler.END

    code = get_error_code(result)
    if code == "ACCOUNT_LOCKED":
        await update.message.reply_text(
            "🔒 *Tài khoản tạm thời bị khóa*\n\n"
            "📌 *Lý do:* Quá nhiều lần đăng nhập sai.\n\n"
            "👉 *Bước tiếp theo:*\n"
            "• Chờ 15 phút rồi thử lại\n"
            "• Hoặc dùng /resend để nhận mật khẩu mới",
            parse_mode="Markdown",
            reply_markup=login_fail_keyboard(),
        )
    elif code == "ACCOUNT_DISABLED":
        await update.message.reply_text(
            "🚫 *Tài khoản đã bị vô hiệu hóa*\n\n"
            "📌 *Lý do:* Tài khoản bị khóa bởi quản trị viên.\n\n"
            "👉 Liên hệ hỗ trợ để biết thêm thông tin.",
            parse_mode="Markdown",
            reply_markup=main_menu(False),
        )
    else:
        await update.message.reply_text(
            "❌ *Đăng nhập thất bại*\n\n"
            "📌 *Lý do:* Email/User Code hoặc mật khẩu không đúng.\n\n"
            "👉 *Bước tiếp theo:*\n"
            "• Kiểm tra lại email và mật khẩu\n"
            "• Dùng /resend nếu quên mật khẩu tạm thời\n"
            "• Dùng /register nếu chưa có tài khoản",
            parse_mode="Markdown",
            reply_markup=login_fail_keyboard(),
        )
    return ConversationHandler.END


async def login_2fa(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    pending_token = ctx.user_data.get("pending_token")
    code = update.message.text.strip()
    ctx.user_data.setdefault("_2fa_attempts", 0)
    ctx.user_data["_2fa_attempts"] += 1
    result = await api.login_2fa(pending_token, code)

    if result.get("access_token"):
        uid = update.effective_user.id
        save_session(uid, result)
        ctx.user_data.pop("_2fa_attempts", None)
        role = result.get("role", "USER")
        await update.message.reply_text(
            "✅ *Đăng nhập thành công!*\n\n"
            "🏠 *P2PSuperBot*\nVui lòng chọn chức năng:",
            parse_mode="Markdown",
            reply_markup=main_menu_reply(role),
        )
        return ConversationHandler.END

    attempts = ctx.user_data["_2fa_attempts"]
    if attempts >= 3:
        ctx.user_data.pop("_2fa_attempts", None)
        await update.message.reply_text(
            "🔒 *Nhập sai quá 3 lần*\n\n"
            "📌 *Lý do:* Mã 2FA không hợp lệ nhiều lần liên tiếp.\n\n"
            "👉 *Bước tiếp theo:*\n"
            "• Nếu có mã khôi phục, nhập một trong các mã đó\n"
            "• Hoặc dùng /login để thử lại từ đầu",
            parse_mode="Markdown",
            reply_markup=main_menu(False),
        )
        return ConversationHandler.END

    await update.message.reply_text(
        f"❌ *Mã 2FA không đúng* (lần {attempts}/3)\n\n"
        "📌 Mã xác thực thay đổi mỗi 30 giây.\n\n"
        "👉 Kiểm tra lại ứng dụng Authenticator và nhập mã mới:\n"
        "_(Nếu mất điện thoại, nhập một trong các mã khôi phục đã lưu)_",
        parse_mode="Markdown",
        reply_markup=twofa_fail_keyboard(),
    )
    return LOGIN_2FA


# ── CHANGE PASSWORD ───────────────────────────────────────────────────────────

async def change_pw_new(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["new_password"] = update.message.text
    await update.message.delete()
    await update.message.reply_text(
        "🔒 Nhập lại mật khẩu mới để xác nhận:\n"
        "_(Tin nhắn sẽ bị xoá ngay)_",
        parse_mode="Markdown",
    )
    return CHANGE_PW_CONFIRM


async def change_pw_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    new_pw = ctx.user_data.get("new_password")
    confirm = update.message.text
    await update.message.delete()

    if new_pw != confirm:
        await update.message.reply_text(
            "❌ *Mật khẩu không khớp*\n\n"
            f"📏 *Nhắc lại yêu cầu:* {_PW_RULES}\n\n"
            "👉 Nhập lại mật khẩu mới:",
            parse_mode="Markdown",
        )
        return CHANGE_PW_CONFIRM

    uid = update.effective_user.id
    old_pw = ctx.user_data.get("change_pw_temp", "")
    first_login_user_id = ctx.user_data.get("change_pw_user_id")

    if first_login_user_id:
        # Đăng nhập lần đầu — chưa có JWT, dùng endpoint không cần token
        result = await api.first_login_change_password(first_login_user_id, old_pw, new_pw)
        # Nếu thành công, result chứa access_token — lưu session luôn
        if result.get("access_token"):
            save_session(uid, result)
    else:
        token = get_token(uid)
        if not token:
            await update.message.reply_text(
                "⏰ *Phiên xác thực đã hết hạn*\n\n"
                "📌 *Lý do:* Quá thời gian cho phép khi đổi mật khẩu.\n\n"
                "👉 Dùng /login để đăng nhập lại từ đầu.",
                parse_mode="Markdown",
                reply_markup=session_expired_keyboard(),
            )
            return ConversationHandler.END
        result = await api.change_password(token, old_pw, new_pw)

    if result.get("success") or result.get("access_token"):
        role = get_role(uid)
        await update.message.reply_text(
            "✅ *Đổi mật khẩu thành công!*\n\n"
            "📌 Tài khoản đã được kích hoạt đầy đủ.\n\n"
            "👉 *Bước tiếp theo được khuyến nghị:*\n"
            "• /2fa\\_setup — Bật xác thực 2 lớp để bảo vệ tài khoản\n"
            "• /profile — Cập nhật thông tin cá nhân\n"
            "• /kyc — Xác minh danh tính để dùng đầy đủ tính năng",
            parse_mode="Markdown",
            reply_markup=main_menu(True, role),
        )
    else:
        msg = parse_api_error(result)
        await update.message.reply_text(
            f"❌ *Đổi mật khẩu thất bại*\n\n{msg}\n\n"
            "👉 Dùng /login để thử lại.",
            parse_mode="Markdown",
        )
    return ConversationHandler.END


# ── 2FA SETUP ─────────────────────────────────────────────────────────────────

async def cmd_2fa_setup(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_logged_in(uid):
        await update.message.reply_text(
            "🔒 *Cần đăng nhập trước*\n\n"
            "👉 Dùng /login để đăng nhập.",
            parse_mode="Markdown",
            reply_markup=main_menu(False),
        )
        return ConversationHandler.END

    await update.message.reply_text("⏳ Đang tạo mã QR...")
    token = get_token(uid)
    result = await api.setup_2fa(token)

    if "qr_code" in result:
        import base64
        qr_bytes = base64.b64decode(result["qr_code"])
        await update.message.reply_photo(
            photo=qr_bytes,
            caption=(
                "📱 *Thiết lập xác thực 2 lớp (2FA)*\n\n"
                "📌 *Bước 1:* Tải app *Google Authenticator* hoặc *Authy*\n"
                "📌 *Bước 2:* Quét mã QR bên trên\n"
                "📌 *Bước 3:* Nhập mã 6 số hiển thị trong app\n\n"
                f"🔑 Secret key thủ công: `{result.get('secret')}`\n"
                "_(Dùng nếu không quét được QR)_\n\n"
                "👉 Nhập mã 6 số để xác nhận:"
            ),
            parse_mode="Markdown",
            reply_markup=cancel_keyboard(),
        )
        return FA_CODE

    await update.message.reply_text(
        "❌ *Không thể tạo mã QR*\n\n"
        "📌 Hệ thống tạm thời gặp sự cố.\n\n"
        "👉 Thử lại sau vài phút bằng lệnh /2fa\\_setup.\n"
        "Nếu lỗi tiếp tục, liên hệ hỗ trợ.",
        parse_mode="Markdown",
    )
    return ConversationHandler.END


async def fa_code_verify(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    token = get_token(uid)
    code = update.message.text.strip()
    result = await api.verify_2fa_setup(token, code)

    if result.get("success"):
        codes = result.get("recovery_codes", [])
        codes_text = "\n".join(f"  `{c}`" for c in codes)
        await update.message.reply_text(
            "✅ *Xác thực 2 lớp đã được kích hoạt!*\n\n"
            "🔑 *Mã khôi phục của bạn:*\n"
            f"{codes_text}\n\n"
            "⚠️ *QUAN TRỌNG:*\n"
            "• Mỗi mã chỉ dùng được *1 lần*\n"
            "• Lưu các mã này ở nơi *an toàn, ngoại tuyến*\n"
            "• Dùng khi mất điện thoại để đăng nhập\n\n"
            "👉 Bước tiếp theo:\n"
            "/profile — Cập nhật hồ sơ\n"
            "/kyc — Xác minh danh tính",
            parse_mode="Markdown",
            reply_markup=main_menu(True, get_role(uid)),
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "❌ *Mã xác thực không đúng*\n\n"
        "📌 *Lý do có thể:*\n"
        "• Mã đã hết hạn (mỗi mã có hiệu lực 30 giây)\n"
        "• Thời gian điện thoại không đồng bộ\n\n"
        "👉 Mở lại Google Authenticator và nhập mã mới nhất:",
        parse_mode="Markdown",
    )
    return FA_CODE


# ── INLINE BUTTON CALLBACKS ───────────────────────────────────────────────────

async def cb_goto_resend(update, ctx):
    """Nút [🔄 Gửi lại email] → vào thẳng flow resend."""
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "🔄 *Gửi lại thông tin đăng nhập*\n\n"
        "📧 Nhập email đã đăng ký:",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard(),
    )
    ctx.user_data["_from_button"] = True
    return RESEND_EMAIL


async def cb_goto_login(update, ctx):
    """Nút [🔑 Đăng nhập] → vào thẳng flow login."""
    query = update.callback_query
    await query.answer()
    if is_logged_in(update.effective_user.id):
        await query.message.reply_text(
            "✅ Bạn đã đăng nhập rồi.\n\n👉 Dùng /profile để xem tài khoản.",
        )
        return ConversationHandler.END
    await query.message.reply_text(
        "🔑 *Đăng nhập P2PSuperBot*\n\n"
        "Nhập email hoặc User Code:",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard(),
    )
    return LOGIN_EMAIL


# ── RESEND VERIFICATION ───────────────────────────────────────────────────────

async def cmd_resend(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        await update.message.reply_text(
            "🔒 Lệnh này chỉ dùng được trong *chat riêng* với bot.",
            parse_mode="Markdown",
        )
        return ConversationHandler.END
    await update.message.reply_text(
        "🔄 *Gửi lại thông tin đăng nhập*\n\n"
        "Nhập email đã đăng ký.\n"
        "Hệ thống sẽ gửi lại User Code và mật khẩu tạm thời nếu tài khoản chưa kích hoạt.\n\n"
        "📧 Nhập email:",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard(),
    )
    return RESEND_EMAIL


async def resend_email(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    await update.message.reply_text("⏳ Đang xử lý...")
    await api.resend_verification(email)
    await update.message.reply_text(
        "📬 *Yêu cầu đã được xử lý*\n\n"
        "📌 Nếu email tồn tại và chưa kích hoạt, chúng tôi đã gửi lại thông tin.\n\n"
        "👉 *Bước tiếp theo:*\n"
        "1. Kiểm tra hộp thư đến\n"
        "2. Kiểm tra thư mục *Spam / Junk*\n"
        "3. Dùng /login với thông tin nhận được\n\n"
        "_Nếu email đã kích hoạt, dùng /login bình thường._",
        parse_mode="Markdown",
        reply_markup=main_menu(False),
    )
    return ConversationHandler.END


# ── LOGOUT ────────────────────────────────────────────────────────────────────

async def cmd_logout(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    chat_id = update.effective_chat.id
    logout_msg_id = update.message.message_id

    delete_session(uid)
    ctx.user_data.clear()

    # Xóa lịch sử chat — thử bulk delete ~200 tin nhắn gần nhất.
    # Bot chỉ xóa được tin của chính mình; tin user sẽ bị bỏ qua silently.
    if logout_msg_id > 1:
        start = max(1, logout_msg_id - 199)
        ids_to_delete = list(range(start, logout_msg_id + 1))
        # deleteMessages nhận tối đa 100 ID mỗi lần
        for i in range(0, len(ids_to_delete), 100):
            chunk = ids_to_delete[i:i + 100]
            try:
                await ctx.bot.delete_messages(chat_id=chat_id, message_ids=chunk)
            except Exception:
                pass

    await ctx.bot.send_message(
        chat_id=chat_id,
        text="👋 *Đã đăng xuất*\n\nLịch sử chat đã được xóa.\n\n👉 Dùng /login để đăng nhập lại.",
        parse_mode="Markdown",
        reply_markup=main_menu(False),
    )
