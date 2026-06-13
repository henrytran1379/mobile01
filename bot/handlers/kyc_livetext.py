"""KYC nhanh qua iPhone Live Text.

Flow:
  Bước 1 — Paste Live Text CCCD  → bot parse, hiện thông tin
  Bước 2 — Upload screenshot VNeID (lưu file, không OCR)
  Bước 3 — Upload ảnh chân dung   (lưu file, không OCR)
  Bước 4 — Xác nhận              → lưu DB (data + đường dẫn ảnh)

Ảnh chỉ để admin đối sánh sau — bot không đọc nội dung ảnh.

Auto-detect: khi user gửi text bất kỳ có chứa từ khoá CCCD,
             bot tự nhận diện mà không cần gõ /kyc trước.
"""
import logging
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import ContextTypes, ConversationHandler, filters as tg_filters

from bot.session import is_logged_in, get_token, get_role
from bot.keyboards import main_menu, cancel_keyboard
import bot.api_client as api
from backend.services.kyc_live_text_parser import parse_cccd_live_text, is_cccd_text
from backend.kyc import file_storage as fs

logger = logging.getLogger(__name__)


class _CCCDTextFilter(tg_filters.MessageFilter):
    """Chỉ match khi message text chứa từ khoá CCCD — tránh chặn login/password flow."""
    def filter(self, message: Message) -> bool:
        return bool(message.text and is_cccd_text(message.text))


cccd_text_filter = _CCCDTextFilter()

# States
LT_SCREENSHOT = 0
LT_PORTRAIT   = 1
LT_CONFIRM    = 2


# ── Bước 1: Auto-detect Live Text ────────────────────────────────────────────

async def auto_detect_cccd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """MessageHandler — tự nhận diện text CCCD từ Live Text.

    Trả về LT_SCREENSHOT nếu parse thành công, None nếu không phải CCCD.
    """
    text = (update.message.text or "").strip()
    if not text or not is_cccd_text(text):
        return None

    uid = update.effective_user.id
    if not is_logged_in(uid):
        await update.message.reply_text(
            "🔒 Cần đăng nhập để thực hiện KYC.\n👉 Dùng /login",
        )
        return ConversationHandler.END

    # Kiểm tra đã KYC chưa — nếu rồi thì không cho làm lại
    token = get_token(uid)
    status = await api.get_kyc_vneid_status(token)
    if status and status.get("kyc_status") == "CONFIRMED":
        await update.message.reply_text(
            "✅ *KYC của bạn đã được xác nhận*\n\n"
            f"👤 {status.get('full_name') or '—'}\n"
            f"🔢 `{status.get('id_number') or '—'}`\n\n"
            "ℹ️ _Dùng /kyc để xem chi tiết._",
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    # Parse trước khi xóa tin nhắn
    result = parse_cccd_live_text(text)

    # Xóa ngay tin nhắn gốc chứa Live Text — bảo vệ dữ liệu cá nhân
    try:
        await update.message.delete()
    except Exception:
        pass  # Không có quyền xóa hoặc tin nhắn đã cũ — bỏ qua

    if result["parse_status"] == "failed":
        await update.message.reply_text(
            "❌ *Không đọc được thông tin CCCD*\n\n"
            "Hãy copy toàn bộ text từ ảnh CCCD bằng iPhone Live Text rồi paste vào đây.",
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    # Loại raw_text khỏi session — không lưu lâu dài trong bộ nhớ bot
    result.pop("raw_text", None)

    # Khởi tạo session
    session_id = uuid.uuid4().hex[:12]
    ctx.user_data["lt_session"]  = session_id
    ctx.user_data["lt_result"]   = result
    ctx.user_data["lt_uid"]      = uid

    if result["parse_status"] == "partial":
        missing = ", ".join(result["missing_fields"])
        header = (
            f"⚠️ *Thiếu một số trường bắt buộc:* `{missing}`\n\n"
            "Bạn vẫn có thể tiếp tục — ảnh sẽ giúp admin xác minh thủ công.\n\n"
        )
    else:
        header = "✅ *Đã đọc được thông tin CCCD từ Live Text*\n\n"

    # Hiện thông tin đã parse + nút xác nhận — không cần upload ảnh thêm
    await update.message.reply_text(
        header + _format_final_summary(result),
        parse_mode="Markdown",
        reply_markup=_confirm_kb(),
    )
    return LT_CONFIRM


# ── Bước 2: Nhận screenshot VNeID ────────────────────────────────────────────

async def cb_skip_screenshot(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """User bấm Bỏ qua bước screenshot."""
    query = update.callback_query
    await query.answer()
    ctx.user_data["lt_screenshot_path"] = ""
    await query.message.reply_text(
        "⏭ Bỏ qua screenshot.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🤳 *Bước 3/3 — Upload ảnh chân dung* _(tuỳ chọn)_\n\n"
        "Gửi ảnh selfie hoặc ảnh thẻ để admin đối chiếu.\n"
        "Nếu không có, bấm *Bỏ qua*.",
        parse_mode="Markdown",
        reply_markup=_skip_portrait_kb(),
    )
    return LT_PORTRAIT


async def cb_skip_portrait(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """User bấm Bỏ qua bước chân dung."""
    query = update.callback_query
    await query.answer()
    ctx.user_data["lt_portrait_path"] = ""
    result = ctx.user_data.get("lt_result", {})
    await query.message.reply_text(
        "⏭ Bỏ qua ảnh chân dung.\n\n"
        + _format_final_summary(result),
        parse_mode="Markdown",
        reply_markup=_confirm_kb(),
    )
    return LT_CONFIRM


async def receive_screenshot(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Nhận screenshot VNeID, lưu file, chuyển sang bước chân dung."""
    if update.message.text:
        await update.message.reply_text(
            "⚠️ Hãy gửi *ảnh* screenshot VNeID, hoặc bấm *Bỏ qua*.",
            parse_mode="Markdown",
            reply_markup=_skip_screenshot_kb(),
        )
        return LT_SCREENSHOT

    if not update.message.photo:
        await update.message.reply_text(
            "❌ Chưa nhận được ảnh. Gửi ảnh chụp màn hình VNeID.",
        )
        return LT_SCREENSHOT

    uid        = ctx.user_data.get("lt_uid") or update.effective_user.id
    session_id = ctx.user_data.get("lt_session", "unknown")

    # Download ảnh chất lượng cao nhất
    photo_file = await update.message.photo[-1].get_file()
    data = bytes(await photo_file.download_as_bytearray())

    # Lưu vĩnh viễn — không OCR
    saved_path = fs.save_screenshot(uid, session_id, data)
    ctx.user_data["lt_screenshot_path"] = str(saved_path)
    logger.info("Screenshot saved uid=%s session=%s path=%s", uid, session_id, saved_path)

    await update.message.reply_text(
        "✅ *Đã nhận screenshot VNeID*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🤳 *Bước 3/3 — Upload ảnh chân dung* _(tuỳ chọn)_\n\n"
        "Gửi ảnh selfie hoặc ảnh thẻ để admin đối chiếu.\n"
        "Nếu không có, bấm *Bỏ qua*.",
        parse_mode="Markdown",
        reply_markup=_skip_portrait_kb(),
    )
    return LT_PORTRAIT


# ── Bước 3: Nhận ảnh chân dung ────────────────────────────────────────────────

async def receive_portrait(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Nhận ảnh chân dung, lưu file, hiển thị xác nhận cuối."""
    if update.message.text:
        await update.message.reply_text(
            "⚠️ Hãy gửi *ảnh chân dung*, hoặc bấm *Bỏ qua*.",
            parse_mode="Markdown",
            reply_markup=_skip_portrait_kb(),
        )
        return LT_PORTRAIT

    if not update.message.photo:
        await update.message.reply_text(
            "❌ Chưa nhận được ảnh. Gửi ảnh chân dung hoặc bấm *Bỏ qua*.",
            parse_mode="Markdown",
            reply_markup=_skip_portrait_kb(),
        )
        return LT_PORTRAIT

    uid        = ctx.user_data.get("lt_uid") or update.effective_user.id
    session_id = ctx.user_data.get("lt_session", "unknown")

    photo_file = await update.message.photo[-1].get_file()
    data = bytes(await photo_file.download_as_bytearray())

    saved_path = fs.save_portrait(uid, session_id, data)
    ctx.user_data["lt_portrait_path"] = str(saved_path)
    logger.info("Portrait saved uid=%s session=%s path=%s", uid, session_id, saved_path)

    result = ctx.user_data.get("lt_result", {})

    await update.message.reply_text(
        "✅ *Đã nhận đủ 2 ảnh*\n\n"
        + _format_final_summary(result),
        parse_mode="Markdown",
        reply_markup=_confirm_kb(),
    )
    return LT_CONFIRM


# ── Bước 4: Xác nhận → lưu DB ────────────────────────────────────────────────

async def cb_lt_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """User bấm Xác nhận — lưu toàn bộ vào DB."""
    query = update.callback_query
    await query.answer()

    uid             = ctx.user_data.get("lt_uid") or update.effective_user.id
    token           = get_token(uid)
    result          = ctx.user_data.get("lt_result")
    session_id      = ctx.user_data.get("lt_session", "")
    screenshot_path = ctx.user_data.get("lt_screenshot_path", "")
    portrait_path   = ctx.user_data.get("lt_portrait_path", "")

    if not result:
        await query.message.reply_text(
            "❌ Phiên đã hết hạn. Vui lòng paste lại CCCD để bắt đầu.",
        )
        _clear(ctx)
        return ConversationHandler.END

    # Gọi API backend lưu DB — không gửi raw_text
    payload = {k: v for k, v in result.items() if k != "raw_text"}
    payload.update({
        "kyc_session_id":  session_id,
        "screenshot_path": screenshot_path,
        "portrait_path":   portrait_path,
    })
    api_result = await api.submit_kyc_vneid(token, payload)
    _clear(ctx)

    if api_result.get("error") or api_result.get("detail"):
        err = api_result.get("detail") or api_result.get("error")
        await query.message.reply_text(
            f"❌ Lưu thất bại: {err}\n\nThử lại hoặc liên hệ hỗ trợ.",
            reply_markup=main_menu(True, get_role(uid)),
        )
        return ConversationHandler.END

    await query.message.reply_text(
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "✅ *KYC đã gửi thành công!*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📋 Hồ sơ của bạn gồm:\n"
        "  • Thông tin CCCD từ Live Text ✅\n"
        "  • Ảnh màn hình VNeID ✅\n"
        "  • Ảnh chân dung ✅\n\n"
        "⏱ Admin sẽ đối sánh và xét duyệt trong *1–3 ngày làm việc*.\n"
        "_Bạn sẽ được thông báo khi có kết quả._",
        parse_mode="Markdown",
        reply_markup=main_menu(True, get_role(uid)),
    )
    return ConversationHandler.END


async def cb_lt_retry(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """User muốn nhập lại từ đầu."""
    query = update.callback_query
    await query.answer()

    # Xoá ảnh đã lưu nếu có
    uid        = ctx.user_data.get("lt_uid") or update.effective_user.id
    session_id = ctx.user_data.get("lt_session", "")
    if session_id:
        fs.delete_kyc_files(uid, session_id)

    _clear(ctx)
    await query.message.reply_text(
        "🔄 OK, paste lại nội dung CCCD từ iPhone Live Text để bắt đầu lại.",
    )
    return ConversationHandler.END


# ── Keyboards ─────────────────────────────────────────────────────────────────

def _skip_screenshot_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏭ Bỏ qua (không có ảnh)", callback_data="lt_skip_screenshot")],
    ])


def _skip_portrait_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏭ Bỏ qua (không có ảnh)", callback_data="lt_skip_portrait")],
    ])


def _confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Xác nhận — Gửi KYC", callback_data="lt_kyc_confirm")],
        [InlineKeyboardButton("🔄 Nhập lại từ đầu",    callback_data="lt_kyc_retry")],
    ])


# ── Formatters ────────────────────────────────────────────────────────────────

def _fmt_date(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        y, m, d = iso.split("-")
        return f"{d}/{m}/{y}"
    except Exception:
        return iso


def _format_parsed(r: dict) -> str:
    """Hiện thông tin đã parse — dùng sau bước Live Text."""
    g = {"male": "Nam ♂", "female": "Nữ ♀"}.get(r.get("gender") or "", "—")
    n = "Việt Nam" if r.get("nationality") == "Vietnam" else (r.get("nationality") or "—")
    return (
        f"🔢 *Số định danh:* `{r.get('id_number') or '—'}`\n"
        f"👤 *Họ và tên:* {r.get('full_name') or '—'}\n"
        f"🎂 *Ngày sinh:* {_fmt_date(r.get('date_of_birth'))}\n"
        f"⚧  *Giới tính:* {g}\n"
        f"🌏 *Quốc tịch:* {n}\n"
        f"🏠 *Nơi cư trú:* {r.get('place_of_residence') or '—'}\n"
        f"📍 *Nơi khai sinh:* {r.get('place_of_birth') or '—'}\n"
        f"📅 *Ngày cấp:* {_fmt_date(r.get('issue_date'))}\n"
        f"⏳ *Hết hạn:* {_fmt_date(r.get('expiry_date'))}"
    )


def _format_final_summary(r: dict) -> str:
    """Summary đầy đủ trước khi xác nhận cuối."""
    return (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📋 *Kiểm tra lại toàn bộ hồ sơ KYC*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        + _format_parsed(r) + "\n\n"
        "📎 *Tài liệu đính kèm:*\n"
        "  • 🖼 Screenshot VNeID ✅\n"
        "  • 🤳 Ảnh chân dung ✅\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "_Nếu đúng bấm_ ✅ *Xác nhận*\n"
        "_Nếu cần sửa bấm_ 🔄 *Nhập lại từ đầu*"
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _clear(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    for k in ("lt_session", "lt_result", "lt_uid", "lt_screenshot_path", "lt_portrait_path"):
        ctx.user_data.pop(k, None)
