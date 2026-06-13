"""Handlers hồ sơ người dùng."""
import re
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot import api_client as api
from bot.session import is_logged_in, get_token, get_role
from bot.keyboards import main_menu, cancel_keyboard
from bot.handlers.common import parse_api_error

PROFILE_UPDATE_FIELD, PROFILE_UPDATE_VALUE = range(2)

_KYC_STATUS_TEXT = {
    "PENDING":   "⏳ Chưa nộp — Dùng /kyc để xác minh",
    "SUBMITTED": "📋 Đang chờ duyệt — Vui lòng chờ",
    "APPROVED":  "✅ Đã xác minh",
    "REJECTED":  "❌ Bị từ chối — Dùng /kyc để nộp lại",
}

_EXAMPLE = (
    "Nguyễn Văn A\n"
    "01/01/1990\n"
    "0909123456\n"
    "123 Nguyễn Trãi, Quận 1, TP.HCM"
)

_GUIDE = (
    "📝 *Cập nhật hồ sơ*\n\n"
    "Vui lòng nhập thông tin theo đúng *4 dòng*:\n"
    "• Dòng 1: Họ tên\n"
    "• Dòng 2: Ngày sinh _(DD/MM/YYYY)_\n"
    "• Dòng 3: Số điện thoại\n"
    "• Dòng 4: Địa chỉ\n\n"
    "*Ví dụ:*\n"
    "```\n"
    f"{_EXAMPLE}\n"
    "```\n\n"
    "👉 Nhập thông tin của bạn:"
)

_ERROR_GUIDE = (
    "❌ *Thông tin chưa đúng định dạng*\n\n"
    "Bạn cần nhập đúng *4 dòng*:\n"
    "1\\. Họ tên\n"
    "2\\. Ngày sinh _(DD/MM/YYYY)_\n"
    "3\\. Số điện thoại\n"
    "4\\. Địa chỉ\n\n"
    "*Ví dụ:*\n"
    "```\n"
    f"{_EXAMPLE}\n"
    "```\n\n"
    "👉 Nhập lại:"
)


def _validate_profile_input(text: str):
    """
    Parse và validate 4 dòng input.
    Trả về (data_dict, error_message).
    Nếu hợp lệ: error_message = None.
    """
    lines = [l.strip() for l in text.strip().splitlines()]
    lines = [l for l in lines if l]  # bỏ dòng trống

    if len(lines) != 4:
        return None, f"Cần đúng 4 dòng, bạn nhập {len(lines)} dòng."

    full_name, dob_raw, phone, address = lines

    # Validate họ tên
    if len(full_name) < 2:
        return None, "Họ tên quá ngắn (tối thiểu 2 ký tự)."

    # Validate ngày sinh DD/MM/YYYY
    if not re.fullmatch(r"\d{2}/\d{2}/\d{4}", dob_raw):
        return None, f"Ngày sinh `{dob_raw}` không đúng định dạng DD/MM/YYYY."
    try:
        dob = datetime.strptime(dob_raw, "%d/%m/%Y")
    except ValueError:
        return None, f"Ngày sinh `{dob_raw}` không hợp lệ."
    if dob.year < 1900 or dob > datetime.now():
        return None, "Ngày sinh không hợp lệ."
    dob_iso = dob.strftime("%Y-%m-%d")

    # Validate số điện thoại: chỉ số, 8–15 ký tự
    if not re.fullmatch(r"\d{8,15}", phone):
        return None, f"Số điện thoại `{phone}` không hợp lệ (chỉ gồm số, 8–15 chữ số)."

    # Validate địa chỉ
    if len(address) < 5:
        return None, "Địa chỉ quá ngắn (tối thiểu 5 ký tự)."

    return {
        "full_name": full_name,
        "date_of_birth": dob_iso,
        "phone": phone,
        "address": address,
    }, None


async def cmd_profile(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
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
    result = await api.get_profile(token)

    if "detail" in result:
        await em.reply_text(
            "❌ *Không thể tải hồ sơ*\n\n"
            "📌 Hệ thống tạm thời gặp sự cố.\n\n"
            "👉 Thử lại sau vài giây. Nếu lỗi tiếp tục, dùng /logout rồi /login lại.",
            parse_mode="Markdown",
        )
        return

    kyc = result.get("kyc_status", "PENDING")
    ekyc = result.get("ekyc_status", "PENDING")
    kyc_text = _KYC_STATUS_TEXT.get(kyc, kyc)
    ekyc_text = _KYC_STATUS_TEXT.get(ekyc, ekyc)

    missing = []
    if not result.get("full_name"):
        missing.append("Họ tên")
    if not result.get("phone"):
        missing.append("Số điện thoại")

    text = (
        f"👤 *Hồ sơ của bạn*\n\n"
        f"• Họ tên: {result.get('full_name') or '_(chưa cập nhật)_'}\n"
        f"• Điện thoại: {result.get('phone') or '_(chưa cập nhật)_'}\n"
        f"• Ngày sinh: {result.get('date_of_birth') or '_(chưa cập nhật)_'}\n"
        f"• Địa chỉ: {result.get('address') or '_(chưa cập nhật)_'}\n\n"
        f"📋 *Trạng thái xác minh*\n"
        f"• KYC: {kyc_text}\n"
        f"• eKYC: {ekyc_text}\n"
    )

    if missing:
        text += f"\n⚠️ *Thiếu thông tin:* {', '.join(missing)}\n👉 Dùng /profile\\_update để bổ sung."
    elif kyc == "PENDING":
        text += "\n👉 Dùng /kyc để bắt đầu xác minh danh tính."
    elif kyc == "APPROVED":
        text += "\n👉 Dùng /wallets để quản lý ví của bạn."

    await em.reply_text(text, parse_mode="Markdown")


async def cmd_profile_update(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_logged_in(uid):
        await update.message.reply_text(
            "🔒 *Cần đăng nhập trước*\n\n👉 Dùng /login để đăng nhập.",
            parse_mode="Markdown",
            reply_markup=main_menu(False),
        )
        return ConversationHandler.END

    await update.message.reply_text(
        _GUIDE,
        parse_mode="Markdown",
        reply_markup=cancel_keyboard(),
    )
    return PROFILE_UPDATE_VALUE


async def profile_field(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Không dùng nữa — giữ lại để tránh lỗi ConversationHandler nếu state cũ còn."""
    return await profile_value(update, ctx)


async def profile_value(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    token = get_token(uid)

    data, error = _validate_profile_input(update.message.text)

    if error:
        await update.message.reply_text(
            f"{_ERROR_GUIDE}\n\n⚠️ _{error}_",
            parse_mode="Markdown",
            reply_markup=cancel_keyboard(),
        )
        return PROFILE_UPDATE_VALUE  # cho nhập lại

    result = await api.update_profile(token, data)

    if result.get("success") or result.get("full_name") or result.get("id"):
        await update.message.reply_text(
            "✅ *Cập nhật hồ sơ thành công\\!*\n\n"
            f"• Họ tên: {data['full_name']}\n"
            f"• Ngày sinh: {update.message.text.strip().splitlines()[1].strip()}\n"
            f"• Điện thoại: {data['phone']}\n"
            f"• Địa chỉ: {data['address']}\n\n"
            "👉 *Bước tiếp theo:*\n"
            "• /profile — Xem lại hồ sơ\n"
            "• /kyc — Xác minh danh tính nếu chưa làm",
            parse_mode="MarkdownV2",
            reply_markup=main_menu(True, get_role(uid)),
        )
    else:
        msg = parse_api_error(result)
        await update.message.reply_text(
            f"❌ *Cập nhật thất bại*\n\n{msg}\n\n"
            "👉 Kiểm tra lại và thử lại.",
            parse_mode="Markdown",
        )
    return ConversationHandler.END
