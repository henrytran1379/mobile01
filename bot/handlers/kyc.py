"""KYC wizard handler — CCCD Việt Nam đầy đủ.

States:
  KYC_FRONT    — chờ ảnh mặt trước
  KYC_BACK     — chờ ảnh mặt sau
  KYC_PORTRAIT — chờ ảnh chân dung
  KYC_CONFIRM  — xem tóm tắt, xác nhận / chụp lại

Sau mỗi ảnh, bot báo ngay thông tin đọc được từ ảnh đó.
Ảnh chân dung chỉ lưu hồ sơ — KHÔNG dùng để so khớp khuôn mặt.
"""
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import BadRequest

from bot import api_client as api
from bot.session import is_logged_in, get_token, get_role
from bot.keyboards import main_menu, cancel_keyboard

logger = logging.getLogger(__name__)

KYC_FRONT, KYC_BACK, KYC_PORTRAIT, KYC_CONFIRM = range(4)
EKYC_PDF = 0

_LOGIN_REQ = "🔒 *Cần đăng nhập trước*\n\n👉 Dùng /login để đăng nhập."

_PHOTO_RULES = (
    "📸 *Yêu cầu ảnh:*\n"
    "• Ảnh rõ nét, đủ sáng\n"
    "• Hiển thị đầy đủ thông tin\n"
    "• Không bị mờ, lóa sáng\n"
    "• Không chụp màn hình"
)

_WELCOME = (
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "🪪 *Xác minh danh tính KYC*\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "Để hoàn tất xác minh, bạn cần upload *đủ 3 ảnh*:\n\n"
    "1️⃣ Ảnh *mặt trước* CCCD/CMND\n"
    "2️⃣ Ảnh *mặt sau* CCCD/CMND _(mã QR phải rõ)_\n"
    "3️⃣ Ảnh *chân dung* của bạn\n\n"
    "⏱ *Thời gian ước tính:* 1–2 phút\n\n"
    "🔒 _Thông tin cá nhân được mã hóa và bảo mật._\n"
    "📷 _Ảnh sẽ bị xóa khỏi Telegram ngay sau khi nhận._"
)

_REUPLOAD_KB = InlineKeyboardMarkup([
    [InlineKeyboardButton("✅ Xác nhận thông tin", callback_data="kyc_confirm")],
    [InlineKeyboardButton("🔄 Chụp lại mặt trước", callback_data="kyc_redo_front")],
    [InlineKeyboardButton("🔄 Chụp lại mặt sau",  callback_data="kyc_redo_back")],
    [InlineKeyboardButton("🔄 Chụp lại ảnh chân dung", callback_data="kyc_redo_portrait")],
])


# ── /kyc entry ────────────────────────────────────────────────────────────────

async def cmd_kyc(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_logged_in(uid):
        await update.message.reply_text(_LOGIN_REQ, parse_mode="Markdown", reply_markup=main_menu(False))
        return ConversationHandler.END

    token = get_token(uid)
    status_result = await api.get_kyc_status(token)
    current = status_result.get("status", "NOT_SUBMITTED")

    if current == "VERIFIED":
        ownership = status_result.get("ownership_status", "unknown")
        own_text = _ownership_note(ownership)
        await update.message.reply_text(
            f"✅ *KYC đã được xác minh*\n\n"
            f"👤 Tên: {status_result.get('full_name', '—')}\n"
            f"🪪 CCCD: {status_result.get('personal_id_masked', '—')}\n\n"
            f"{own_text}",
            parse_mode="Markdown",
            reply_markup=main_menu(True, get_role(uid)),
        )
        return ConversationHandler.END

    if current == "UNDER_REVIEW":
        await update.message.reply_text(
            "⏳ *Hồ sơ KYC đang chờ xét duyệt*\n\n"
            "📌 Chúng tôi đang xem xét hồ sơ của bạn.\n"
            "⏱ Thường mất 1–3 ngày làm việc.\n\n"
            "_Bạn sẽ được thông báo khi có kết quả._",
            parse_mode="Markdown",
            reply_markup=main_menu(True, get_role(uid)),
        )
        return ConversationHandler.END

    reject_reason = status_result.get("reject_reason")
    if current in ("REJECTED", "NEED_REUPLOAD") and reject_reason:
        await update.message.reply_text(
            f"❌ *Hồ sơ KYC cần bổ sung*\n\n"
            f"📌 *Lý do:* {reject_reason}\n\n"
            "👉 Vui lòng nộp lại hồ sơ mới bên dưới.",
            parse_mode="Markdown",
        )

    _clear_kyc_data(ctx)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("▶️ Bắt đầu KYC", callback_data="kyc_start")]])
    await update.message.reply_text(_WELCOME, parse_mode="Markdown", reply_markup=keyboard)
    return ConversationHandler.END


async def cb_kyc_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "📷 *Bước 1/3 — Mặt trước CCCD*\n\n"
        "Gửi ảnh *mặt trước* CCCD/CMND của bạn.\n\n"
        f"{_PHOTO_RULES}",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard(),
    )
    return KYC_FRONT


# ── Bước 1: Mặt trước ─────────────────────────────────────────────────────────

async def kyc_front(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text(
            "❌ Bạn cần upload *ảnh mặt trước CCCD*.\n\n"
            f"{_PHOTO_RULES}",
            parse_mode="Markdown",
        )
        return KYC_FRONT

    photo_file = await update.message.photo[-1].get_file()
    data = bytes(await photo_file.download_as_bytearray())
    ctx.user_data["kyc_front"] = data
    await _try_delete(update)

    # Phân tích ngay mặt trước
    analyzing_msg = await update.message.reply_text("🔍 Đang đọc thông tin mặt trước...")
    front_summary = await _analyze_front(data)
    await analyzing_msg.delete()

    await update.message.reply_text(
        f"✅ *Mặt trước đã nhận!*\n\n"
        f"{front_summary}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📷 *Bước 2/3 — Mặt sau CCCD*\n\n"
        "Gửi ảnh *mặt sau* CCCD/CMND.\n"
        "⚠️ Đảm bảo *mã QR* trên mặt sau rõ ràng — đây là nguồn dữ liệu chính.",
        parse_mode="Markdown",
    )
    return KYC_BACK


# ── Bước 2: Mặt sau ───────────────────────────────────────────────────────────

async def kyc_back(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text(
            "❌ Bạn cần upload *ảnh mặt sau CCCD* (mã QR phải rõ ràng).",
            parse_mode="Markdown",
        )
        return KYC_BACK

    photo_file = await update.message.photo[-1].get_file()
    data = bytes(await photo_file.download_as_bytearray())
    ctx.user_data["kyc_back"] = data
    await _try_delete(update)

    # Phân tích ngay mặt sau
    analyzing_msg = await update.message.reply_text("🔍 Đang đọc mã QR và thông tin mặt sau...")
    back_summary = await _analyze_back(data)
    await analyzing_msg.delete()

    await update.message.reply_text(
        f"✅ *Mặt sau đã nhận!*\n\n"
        f"{back_summary}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📷 *Bước 3/3 — Ảnh chân dung*\n\n"
        "Gửi ảnh *chân dung* của bạn.\n\n"
        "📸 *Yêu cầu:*\n"
        "• Khuôn mặt rõ ràng, nhìn thẳng\n"
        "• Đủ ánh sáng, không đeo kính râm\n"
        "• Không dùng ảnh cũ hoặc ảnh chụp màn hình\n\n"
        "ℹ️ _Ảnh chân dung chỉ dùng để lưu hồ sơ nhận diện, không dùng để so khớp khuôn mặt._",
        parse_mode="Markdown",
    )
    return KYC_PORTRAIT


# ── Bước 3: Ảnh chân dung ─────────────────────────────────────────────────────

async def kyc_portrait(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text(
            "❌ Bạn cần upload *ảnh chân dung*.",
            parse_mode="Markdown",
        )
        return KYC_PORTRAIT

    photo_file = await update.message.photo[-1].get_file()
    portrait_data = bytes(await photo_file.download_as_bytearray())
    ctx.user_data["kyc_portrait"] = portrait_data
    await _try_delete(update)

    msg = await update.message.reply_text("⏳ Đang phân tích hồ sơ KYC, vui lòng chờ...")

    token = get_token(update.effective_user.id)
    result = await api.submit_kyc_full(
        token=token,
        telegram_user_id=update.effective_user.id,
        front_bytes=ctx.user_data["kyc_front"],
        back_bytes=ctx.user_data["kyc_back"],
        portrait_bytes=portrait_data,
    )

    await msg.delete()

    if result.get("error_code"):
        code = result.get("error_code", "")
        if code == "INVALID_IMAGE":
            field = result.get("field", "")
            err_msg = result.get("message", "Ảnh không hợp lệ")
            await update.message.reply_text(
                f"❌ *Ảnh {_field_label(field)} không đạt yêu cầu*\n\n"
                f"📌 {err_msg}\n\n"
                "👉 Vui lòng chụp lại và gửi:",
                parse_mode="Markdown",
                reply_markup=cancel_keyboard(),
            )
            if field == "front":
                return KYC_FRONT
            if field == "back":
                return KYC_BACK
            return KYC_PORTRAIT
        else:
            await update.message.reply_text(
                "❌ *Không thể xử lý hồ sơ*\n\n"
                f"{result.get('message') or result.get('detail') or 'Lỗi không xác định'}\n\n"
                "👉 Dùng /kyc để thử lại.",
                parse_mode="Markdown",
                reply_markup=main_menu(True, get_role(update.effective_user.id)),
            )
            return ConversationHandler.END

    missing = result.get("missing_fields", [])
    if missing:
        fields_text = ", ".join(missing)
        await update.message.reply_text(
            f"⚠️ *Ảnh đã nhận nhưng chưa đọc được: {fields_text}*\n\n"
            "📸 Vui lòng chụp lại *mặt sau CCCD* rõ nét, không lóa sáng, không nghiêng.\n\n"
            "💡 *Mẹo:*\n"
            "• Đặt CCCD trên nền tối, đủ sáng\n"
            "• Đảm bảo mã QR không bị mờ hoặc bị che\n"
            "• Chụp thẳng, không nghiêng\n"
            "• Zoom đủ để toàn bộ mặt sau rõ trong khung",
            parse_mode="Markdown",
            reply_markup=cancel_keyboard(),
        )
        ctx.user_data["kyc_missing"] = missing
        return KYC_BACK

    ctx.user_data["kyc_extraction"] = result
    await update.message.reply_text(
        _format_summary(result),
        parse_mode="Markdown",
        reply_markup=_REUPLOAD_KB,
    )
    return KYC_CONFIRM


# ── Bước 4: Xác nhận ─────────────────────────────────────────────────────────

async def cb_kyc_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = update.effective_user.id
    role = get_role(uid)
    result = ctx.user_data.get("kyc_extraction", {})
    status = result.get("status", "UNDER_REVIEW")
    ownership = result.get("ownership_status", "unknown")

    _clear_kyc_data(ctx)

    if status == "NEED_REUPLOAD":
        await query.message.reply_text(
            "⚠️ *Hồ sơ chưa đầy đủ*\n\n"
            "📌 Vui lòng dùng /kyc để nộp lại với ảnh rõ hơn.",
            parse_mode="Markdown",
            reply_markup=main_menu(True, role),
        )
        return ConversationHandler.END

    ownership_msg = _ownership_note(ownership)
    await query.message.reply_text(
        "✅ *Hồ sơ KYC đã được nộp!*\n\n"
        f"{ownership_msg}\n\n"
        "📌 *Trạng thái:* Đang chờ xét duyệt\n"
        "⏱ *Thời gian xử lý:* 1–3 ngày làm việc\n\n"
        "_Bạn sẽ nhận được thông báo khi hồ sơ được duyệt._",
        parse_mode="Markdown",
        reply_markup=main_menu(True, role),
    )
    return ConversationHandler.END


async def cb_kyc_redo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data

    if action == "kyc_redo_front":
        ctx.user_data.pop("kyc_front", None)
        await query.message.reply_text(
            "📷 *Chụp lại mặt trước CCCD*\n\n"
            f"{_PHOTO_RULES}\n\n👉 Gửi ảnh mặt trước:",
            parse_mode="Markdown",
            reply_markup=cancel_keyboard(),
        )
        return KYC_FRONT

    if action == "kyc_redo_back":
        ctx.user_data.pop("kyc_back", None)
        await query.message.reply_text(
            "📷 *Chụp lại mặt sau CCCD*\n\n"
            "⚠️ Đảm bảo mã QR rõ ràng.\n\n👉 Gửi ảnh mặt sau:",
            parse_mode="Markdown",
            reply_markup=cancel_keyboard(),
        )
        return KYC_BACK

    if action == "kyc_redo_portrait":
        ctx.user_data.pop("kyc_portrait", None)
        await query.message.reply_text(
            "📷 *Chụp lại ảnh chân dung*\n\n"
            "👉 Gửi ảnh chân dung của bạn:",
            parse_mode="Markdown",
            reply_markup=cancel_keyboard(),
        )
        return KYC_PORTRAIT

    return KYC_CONFIRM


# ── eKYC ──────────────────────────────────────────────────────────────────────

async def cmd_ekyc(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_logged_in(uid):
        await update.message.reply_text(_LOGIN_REQ, parse_mode="Markdown", reply_markup=main_menu(False))
        return ConversationHandler.END
    await update.message.reply_text(
        "📄 *Xác minh eKYC — Hồ sơ điện tử*\n\n"
        "📌 *Yêu cầu:*\n"
        "• Định dạng: *PDF*\n"
        "• Kích thước: Tối đa 10MB\n\n"
        "👉 Gửi file PDF:",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard(),
    )
    return EKYC_PDF


async def ekyc_pdf(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        await update.message.reply_text("❌ Chưa nhận file. Gửi file *PDF*:", parse_mode="Markdown")
        return EKYC_PDF

    doc = update.message.document
    if not (doc.file_name or "").lower().endswith(".pdf"):
        await update.message.reply_text(
            f"❌ File `{doc.file_name}` không phải PDF. Gửi lại file *.pdf*:",
            parse_mode="Markdown",
        )
        return EKYC_PDF

    file = await doc.get_file()
    pdf_bytes = bytes(await file.download_as_bytearray())
    await update.message.reply_text("⏳ Đang nộp hồ sơ eKYC...")

    token = get_token(update.effective_user.id)
    result = await api.submit_ekyc(token, pdf_bytes)

    if result.get("success") or result.get("submission_id"):
        await update.message.reply_text(
            "✅ *Nộp eKYC thành công!*\n\n"
            "⏱ Xử lý trong 1–3 ngày làm việc.\n"
            "_Bạn sẽ được thông báo khi có kết quả._",
            parse_mode="Markdown",
            reply_markup=main_menu(True, get_role(update.effective_user.id)),
        )
    else:
        await update.message.reply_text(
            f"❌ *Nộp eKYC thất bại*\n\n"
            f"{result.get('message') or 'Lỗi không xác định'}\n\n"
            "👉 Dùng /ekyc để thử lại.",
            parse_mode="Markdown",
        )
    return ConversationHandler.END


# ── Per-photo analysis ────────────────────────────────────────────────────────

async def _analyze_front(image_bytes: bytes) -> str:
    """Chạy OCR mặt trước trong thread, trả về chuỗi báo cáo."""
    try:
        loop = asyncio.get_event_loop()
        from backend.kyc.extractors.ocr_extractor import extract_ocr
        ocr = await loop.run_in_executor(None, lambda: extract_ocr(image_bytes, is_back=False))
        return _format_ocr_report(ocr, side="front")
    except Exception as exc:
        logger.warning("analyze_front error: %s", exc)
        return "ℹ️ _Không thể đọc trước, sẽ phân tích khi nộp toàn bộ hồ sơ._"


async def _analyze_back(image_bytes: bytes) -> str:
    """Chạy QR + OCR mặt sau trong thread, trả về chuỗi báo cáo."""
    try:
        loop = asyncio.get_event_loop()
        from backend.kyc.extractors.qr_extractor import extract_qr
        from backend.kyc.extractors.ocr_extractor import extract_ocr

        def _run():
            qr = extract_qr(image_bytes)
            ocr = extract_ocr(image_bytes, is_back=True)
            return qr, ocr

        qr, ocr = await loop.run_in_executor(None, _run)
        return _format_back_report(qr, ocr)
    except Exception as exc:
        logger.warning("analyze_back error: %s", exc)
        return "ℹ️ _Không thể đọc trước, sẽ phân tích khi nộp toàn bộ hồ sơ._"


def _format_ocr_report(ocr, side: str) -> str:
    """Tạo báo cáo đọc thông tin từ ảnh mặt trước."""
    lines_ok = []
    lines_fail = []

    _check_field(ocr, "personal_id",       "Số CCCD/CMND",           lines_ok, lines_fail)
    _check_field(ocr, "full_name",         "Họ tên",                  lines_ok, lines_fail)
    _check_field(ocr, "date_of_birth",     "Ngày sinh",               lines_ok, lines_fail)
    _check_field(ocr, "gender",            "Giới tính",               lines_ok, lines_fail)
    _check_field(ocr, "nationality",       "Quốc tịch",               lines_ok, lines_fail)
    _check_field(ocr, "place_of_birth",    "Nơi khai sinh",           lines_ok, lines_fail)
    _check_field(ocr, "place_of_residence","Nơi thường trú",          lines_ok, lines_fail)
    _check_field(ocr, "expiry_date",       "Ngày hết hạn",            lines_ok, lines_fail)

    return _build_report(lines_ok, lines_fail)


def _format_back_report(qr, ocr) -> str:
    """Tạo báo cáo đọc thông tin từ ảnh mặt sau."""
    lines_ok = []
    lines_fail = []

    # QR data
    if qr and qr.personal_id:
        lines_ok.append(f"📷 QR: Số CCCD `{qr.personal_id[:6]}...`")
        if qr.full_name:
            lines_ok.append(f"📷 QR: Họ tên `{qr.full_name}`")
        if qr.date_of_birth:
            lines_ok.append(f"📷 QR: Ngày sinh `{qr.date_of_birth}`")
        if qr.place_of_birth:
            lines_ok.append(f"📷 QR: Nơi khai sinh đọc được")
        if qr.issue_date:
            lines_ok.append(f"📷 QR: Ngày cấp `{qr.issue_date}`")
        if qr.expiry_date:
            lines_ok.append(f"📷 QR: Hết hạn `{qr.expiry_date}`")
    else:
        lines_fail.append("Mã QR — không đọc được _(kiểm tra ảnh có rõ không)_")

    # OCR back fields
    _check_field(ocr, "issue_date",        "Ngày cấp (OCR)",          lines_ok, lines_fail)
    _check_field(ocr, "issuing_authority", "Cơ quan cấp (OCR)",       lines_ok, lines_fail)
    _check_field(ocr, "place_of_residence","Nơi thường trú (OCR)",    lines_ok, lines_fail)

    return _build_report(lines_ok, lines_fail)


def _check_field(obj, attr: str, label: str, ok: list, fail: list) -> None:
    val = getattr(obj, attr, None)
    if val:
        # Hiển thị giá trị ngắn gọn
        display = val if len(val) <= 40 else val[:37] + "…"
        ok.append(f"`{display}`  ← {label}")
    else:
        fail.append(label)


def _build_report(ok: list, fail: list) -> str:
    parts = []
    if ok:
        parts.append("✅ *Đọc được:*\n" + "\n".join(f"  • {x}" for x in ok))
    if fail:
        parts.append("❌ *Chưa đọc được:*\n" + "\n".join(f"  • {x}" for x in fail))
    if not ok and not fail:
        return "ℹ️ _Ảnh nhận được, sẽ xử lý khi nộp toàn bộ hồ sơ._"
    return "\n\n".join(parts)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _format_summary(result: dict) -> str:
    ext = result.get("extracted", {})
    source = result.get("extraction_source", "—")
    method = result.get("verification_method", "—")

    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━",
        "📋 *Tóm tắt thông tin KYC*",
        "━━━━━━━━━━━━━━━━━━━━━━",
        "",
        f"👤 *Họ tên:* {ext.get('full_name') or '—'}",
        f"🎂 *Ngày sinh:* {ext.get('date_of_birth') or '—'}",
        f"⚧ *Giới tính:* {ext.get('gender') or '—'}",
        f"🌏 *Quốc tịch:* {ext.get('nationality') or '—'}",
        f"🪪 *Số CCCD:* `{ext.get('personal_id_masked') or '—'}`",
        f"📍 *Nơi khai sinh:* {_truncate(ext.get('place_of_birth'), 60)}",
        f"🏠 *Thường trú:* {_truncate(ext.get('place_of_residence'), 60)}",
        f"📅 *Ngày cấp:* {ext.get('issue_date') or '—'}",
        f"⏳ *Hết hạn:* {ext.get('expiry_date') or '—'}",
        f"🏛 *Cơ quan cấp:* {ext.get('issuing_authority') or '—'}",
        "",
        f"📡 *Nguồn:* {source} | *Phương pháp:* {method}",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━",
        "",
        "_Kiểm tra thông tin. Nếu đúng, nhấn Xác nhận._",
    ]
    return "\n".join(lines)


def _ownership_note(ownership: str) -> str:
    if ownership == "self":
        return "🟢 *KYC thành công. Hồ sơ này trùng khớp với thông tin profile của bạn.*"
    if ownership == "not_self":
        return ("🟡 *KYC thành công. Tuy nhiên thông tin giấy tờ không trùng với profile, "
                "hệ thống ghi nhận đây là KYC không chính chủ.*")
    return ("🔵 *KYC thành công. Tuy nhiên profile của bạn chưa đủ Họ tên hoặc Ngày sinh "
            "để xác định chính chủ.*")


def _field_label(field: str) -> str:
    return {"front": "mặt trước", "back": "mặt sau", "portrait": "chân dung"}.get(field, field)


def _truncate(text: str, max_len: int) -> str:
    if not text:
        return "—"
    return text if len(text) <= max_len else text[:max_len] + "…"


async def _try_delete(update: Update) -> None:
    try:
        await update.message.delete()
    except (BadRequest, Exception):
        pass


def _clear_kyc_data(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    for key in ("kyc_front", "kyc_back", "kyc_portrait", "kyc_extraction", "kyc_missing"):
        ctx.user_data.pop(key, None)
