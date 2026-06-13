"""KYC VNeID handler — flow mới không cần chụp CCCD vật lý.

Flow:
  1. /kyc → welcome → cb_kyc_vneid_start
  2. VNEID_SCREENSHOT  — chờ user upload screenshot VNeID
  3. VNEID_LIVETEXT    — chờ user paste Live Text
  4. VNEID_CONFIRM     — hiển thị kết quả, chờ xác nhận

Sau khi parse Live Text:
  - Xoá screenshot tạm
  - Hiển thị thông tin đã đọc để user kiểm tra
  - Chỉ lưu DB khi user bấm Xác nhận

Không lưu ảnh vĩnh viễn.
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.error import BadRequest

from bot import api_client as api
from bot.session import is_logged_in, get_token, get_role
from bot.keyboards import main_menu, cancel_keyboard
from backend.kyc.parsers.live_text_parser import parse_live_text, ParseResult, REQUIRED_FIELDS
from backend.kyc import temp_storage as tmp

logger = logging.getLogger(__name__)

# States
VNEID_SCREENSHOT, VNEID_LIVETEXT, VNEID_CONFIRM = range(3)

_LOGIN_REQ = "🔒 *Cần đăng nhập trước*\n\n👉 Dùng /login để đăng nhập."

_WELCOME = (
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "🪪 *Xác minh KYC qua VNeID*\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "Quy trình *không cần chụp CCCD vật lý*:\n\n"
    "1️⃣ Mở app *VNeID* trên điện thoại\n"
    "2️⃣ Vào *Thông tin thẻ Căn cước*\n"
    "3️⃣ *Chụp màn hình* trang hiển thị cả mặt trước + sau\n"
    "4️⃣ Upload screenshot vào đây\n"
    "5️⃣ Dùng *iPhone Live Text* copy toàn bộ chữ trong screenshot\n"
    "6️⃣ Paste nội dung vào đây\n\n"
    "🔒 _Screenshot chỉ lưu tạm, xoá ngay sau khi đọc xong._"
)

_GUIDE_LIVETEXT = (
    "✅ *Đã nhận screenshot VNeID!*\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "📋 *Bước tiếp theo — Paste Live Text*\n\n"
    "Trên iPhone:\n"
    "• Mở ảnh screenshot vừa chụp\n"
    "• Nhấn giữ vào chữ → *Chọn tất cả* → *Sao chép*\n"
    "• Quay lại bot và *Paste* (dán) vào đây\n\n"
    "💡 _Paste toàn bộ text — bot sẽ tự phân tích._"
)


# ── /kyc entry ────────────────────────────────────────────────────────────────

async def cmd_kyc(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Lệnh /kyc — hiện trạng thái KYC hoặc hướng dẫn nếu chưa làm."""
    uid = update.effective_user.id
    if not is_logged_in(uid):
        await update.message.reply_text(
            _LOGIN_REQ, parse_mode="Markdown",
            reply_markup=main_menu(False),
        )
        return

    token = get_token(uid)

    # Kiểm tra đã có KYC VNeID chưa
    status = await api.get_kyc_vneid_status(token)
    kyc_status = status.get("kyc_status") if status else None

    if kyc_status == "CONFIRMED":
        # Đã xác nhận → hiện thông tin, không cho làm lại
        await update.message.reply_text(
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "✅ *KYC đã được xác nhận*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 *Họ và tên:* {status.get('full_name') or '—'}\n"
            f"🔢 *Số định danh:* `{status.get('id_number') or '—'}`\n"
            f"📅 *Ngày xác nhận:* {_fmt_confirmed_at(status.get('confirmed_at'))}\n\n"
            "ℹ️ _Hồ sơ KYC đã được lưu. Nếu cần cập nhật liên hệ hỗ trợ._",
            parse_mode="Markdown",
            reply_markup=main_menu(True, get_role(uid)),
        )
        return

    # Chưa KYC → hướng dẫn
    await update.message.reply_text(
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🪪 *KYC bằng iPhone Live Text*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "*Cách thực hiện:*\n\n"
        "1️⃣ Mở app *VNeID* → Thông tin thẻ Căn cước\n"
        "2️⃣ Nhấn giữ vào text → *Chọn tất cả* → *Sao chép*\n"
        "3️⃣ Quay lại bot và *Paste* (dán) vào đây\n\n"
        "Bot sẽ tự nhận diện và hướng dẫn các bước tiếp theo.\n\n"
        "💡 _Không cần gõ lệnh gì thêm — paste trực tiếp là bot xử lý._",
        parse_mode="Markdown",
    )


def _fmt_confirmed_at(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        # "2026-06-12T15:30:00" → "12/06/2026"
        return iso[:10].replace("-", "/")[::-1].replace("/", "-")[::-1]
    except Exception:
        return iso


async def cb_kyc_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # Tạo session mới
    session_id = tmp.new_session_id()
    ctx.user_data["kyc_session"] = session_id
    await query.message.reply_text(
        "📸 *Bước 1/2 — Upload screenshot VNeID*\n\n"
        "Gửi *screenshot* màn hình VNeID hiển thị thông tin thẻ Căn cước.\n\n"
        "⚠️ Đảm bảo cả mặt trước và mặt sau hiển thị rõ trong ảnh.",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard(),
    )
    return VNEID_SCREENSHOT


# ── State 1: Screenshot ───────────────────────────────────────────────────────

async def vneid_screenshot(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Nhận screenshot VNeID từ user."""
    if update.message.text:
        # User paste text trước khi upload ảnh
        await update.message.reply_text(
            "⚠️ *Vui lòng upload screenshot VNeID trước*\n\n"
            "Gửi *ảnh screenshot* — không phải text.\n"
            "Sau khi bot nhận ảnh, bạn mới cần paste Live Text.",
            parse_mode="Markdown",
        )
        return VNEID_SCREENSHOT

    if not update.message.photo:
        await update.message.reply_text(
            "❌ Chưa nhận được ảnh. Hãy gửi *screenshot VNeID*.",
            parse_mode="Markdown",
        )
        return VNEID_SCREENSHOT

    uid = update.effective_user.id
    session_id = ctx.user_data.get("kyc_session") or tmp.new_session_id()
    ctx.user_data["kyc_session"] = session_id

    # Download và lưu tạm
    photo_file = await update.message.photo[-1].get_file()
    data = bytes(await photo_file.download_as_bytearray())
    await _try_delete(update)

    tmp.save_screenshot(uid, session_id, data)
    ctx.user_data["kyc_has_screenshot"] = True

    await update.message.reply_text(
        _GUIDE_LIVETEXT,
        parse_mode="Markdown",
        reply_markup=cancel_keyboard(),
    )
    return VNEID_LIVETEXT


# ── State 2: Live Text ────────────────────────────────────────────────────────

async def vneid_livetext(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Nhận và parse Live Text từ user."""
    if update.message.photo:
        # User gửi ảnh thay vì text
        await update.message.reply_text(
            "ℹ️ Đã nhận screenshot rồi.\n\n"
            "Bây giờ hãy *paste Live Text* — copy toàn bộ chữ từ screenshot và gửi dạng text.",
            parse_mode="Markdown",
        )
        return VNEID_LIVETEXT

    raw_text = (update.message.text or "").strip()
    if not raw_text:
        await update.message.reply_text(
            "❌ Chưa nhận được text. Hãy *paste Live Text* từ screenshot.",
            parse_mode="Markdown",
        )
        return VNEID_LIVETEXT

    # Kiểm tra có screenshot chưa
    if not ctx.user_data.get("kyc_has_screenshot"):
        await update.message.reply_text(
            "⚠️ *Vui lòng upload screenshot VNeID trước*\n\n"
            "Gửi ảnh screenshot trước, sau đó paste Live Text.",
            parse_mode="Markdown",
        )
        return VNEID_SCREENSHOT

    uid       = update.effective_user.id
    session_id = ctx.user_data["kyc_session"]

    # Parse Live Text
    result = parse_live_text(raw_text)

    # Xoá screenshot tạm ngay sau khi parse
    deleted = tmp.delete_session(uid, session_id)
    logger.info("Temp screenshot deleted=%s uid=%s session=%s", deleted, uid, session_id)

    # Lưu kết quả vào session để xác nhận
    ctx.user_data["kyc_result"] = result.to_dict()

    if result.parse_status == "failed":
        await update.message.reply_text(
            "❌ *Không đọc được thông tin nào*\n\n"
            "Text paste vào không chứa dữ liệu CCCD hợp lệ.\n\n"
            "💡 *Mẹo:*\n"
            "• Chọn tất cả text trong screenshot (Live Text → Select All)\n"
            "• Copy và paste toàn bộ vào đây\n"
            "• Đảm bảo screenshot chứa thông tin thẻ Căn cước",
            parse_mode="Markdown",
            reply_markup=_retry_kb(),
        )
        return VNEID_LIVETEXT

    if result.missing_fields:
        missing_text = "\n".join(f"  • {f}" for f in result.missing_fields)
        await update.message.reply_text(
            f"⚠️ *Thiếu thông tin bắt buộc:*\n{missing_text}\n\n"
            "📋 Vui lòng copy lại Live Text đầy đủ hơn hoặc nhập bổ sung.\n\n"
            f"{_format_partial(result)}",
            parse_mode="Markdown",
            reply_markup=_retry_kb(),
        )
        return VNEID_LIVETEXT

    # Đủ thông tin — hiển thị để xác nhận
    await update.message.reply_text(
        _format_summary(result),
        parse_mode="Markdown",
        reply_markup=_confirm_kb(),
    )
    return VNEID_CONFIRM


# ── State 3: Xác nhận ────────────────────────────────────────────────────────

async def cb_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """User xác nhận → lưu vào database."""
    query = update.callback_query
    await query.answer()

    uid   = update.effective_user.id
    token = get_token(uid)
    data  = ctx.user_data.get("kyc_result", {})

    if not data:
        await query.message.reply_text("❌ Phiên đã hết hạn. Dùng /kyc để bắt đầu lại.")
        _clear(ctx)
        return ConversationHandler.END

    # Gọi API lưu DB
    result = await api.submit_kyc_vneid(token, data)

    _clear(ctx)

    if result.get("error") or result.get("detail"):
        await query.message.reply_text(
            f"❌ Lưu thất bại: {result.get('detail') or result.get('error')}\n\n"
            "Dùng /kyc để thử lại.",
            parse_mode="Markdown",
            reply_markup=main_menu(True, get_role(uid)),
        )
        return ConversationHandler.END

    await query.message.reply_text(
        "✅ *KYC đã xác nhận thành công!*\n\n"
        "📌 Hồ sơ đã lưu vào hệ thống.\n"
        "⏱ Xét duyệt trong 1–3 ngày làm việc.\n\n"
        "_Bạn sẽ được thông báo khi có kết quả._",
        parse_mode="Markdown",
        reply_markup=main_menu(True, get_role(uid)),
    )
    return ConversationHandler.END


async def cb_retry_livetext(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """User muốn paste lại Live Text."""
    query = update.callback_query
    await query.answer()
    # Tạo session mới (screenshot cũ đã xoá)
    session_id = tmp.new_session_id()
    ctx.user_data["kyc_session"] = session_id
    ctx.user_data["kyc_has_screenshot"] = False
    ctx.user_data.pop("kyc_result", None)

    await query.message.reply_text(
        "📸 *Chụp lại screenshot và upload lại*\n\n"
        "Gửi screenshot VNeID mới:",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard(),
    )
    return VNEID_SCREENSHOT


async def cb_redo_screenshot(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """User muốn chụp lại screenshot."""
    query = update.callback_query
    await query.answer()
    uid = update.effective_user.id
    session_id = ctx.user_data.get("kyc_session", "")
    if session_id:
        tmp.delete_session(uid, session_id)
    session_id = tmp.new_session_id()
    ctx.user_data["kyc_session"] = session_id
    ctx.user_data["kyc_has_screenshot"] = False
    ctx.user_data.pop("kyc_result", None)

    await query.message.reply_text(
        "📸 Gửi *screenshot VNeID* mới:",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard(),
    )
    return VNEID_SCREENSHOT


# ── Keyboards ─────────────────────────────────────────────────────────────────

def _confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Xác nhận", callback_data="kyc_vneid_confirm")],
        [InlineKeyboardButton("🔄 Nhập lại Live Text", callback_data="kyc_vneid_retry")],
        [InlineKeyboardButton("📸 Chụp lại screenshot",  callback_data="kyc_vneid_redo_screenshot")],
    ])


def _retry_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Paste lại Live Text", callback_data="kyc_vneid_retry")],
        [InlineKeyboardButton("📸 Chụp lại screenshot",  callback_data="kyc_vneid_redo_screenshot")],
    ])


# ── Formatters ────────────────────────────────────────────────────────────────

def _format_summary(r: ParseResult) -> str:
    g = {"male": "Nam", "female": "Nữ"}.get(r.gender or "", r.gender or "—")
    n = "Việt Nam" if r.nationality == "Vietnam" else (r.nationality or "—")
    return (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📋 *Bot đã đọc được thông tin KYC:*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🪪 *Số định danh:* `{r.id_number or '—'}`\n"
        f"👤 *Họ tên:* {r.full_name or '—'}\n"
        f"🎂 *Ngày sinh:* {_fmt_date(r.date_of_birth)}\n"
        f"⚧ *Giới tính:* {g}\n"
        f"🌏 *Quốc tịch:* {n}\n"
        f"🏠 *Nơi cư trú:* {r.place_of_residence or '—'}\n"
        f"📍 *Nơi đăng ký khai sinh:* {r.place_of_birth or '—'}\n"
        f"📅 *Ngày cấp:* {_fmt_date(r.issue_date)}\n"
        f"⏳ *Ngày hết hạn:* {_fmt_date(r.expiry_date)}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "_Vui lòng kiểm tra lại._\n"
        "_Nếu đúng bấm ✅ Xác nhận._\n"
        "_Nếu sai bấm 🔄 Nhập lại Live Text._"
    )


def _format_partial(r: ParseResult) -> str:
    """Hiển thị những gì đã đọc được (partial)."""
    lines = ["*Thông tin đọc được:*"]
    if r.id_number:    lines.append(f"  🪪 Số định danh: `{r.id_number}`")
    if r.full_name:    lines.append(f"  👤 Họ tên: {r.full_name}")
    if r.date_of_birth: lines.append(f"  🎂 Ngày sinh: {_fmt_date(r.date_of_birth)}")
    if r.gender:       lines.append(f"  ⚧ Giới tính: {'Nam' if r.gender == 'male' else 'Nữ'}")
    if r.nationality:  lines.append(f"  🌏 Quốc tịch: {'Việt Nam' if r.nationality == 'Vietnam' else r.nationality}")
    if r.place_of_residence: lines.append(f"  🏠 Nơi cư trú: {r.place_of_residence[:60]}")
    return "\n".join(lines)


def _fmt_date(d: str | None) -> str:
    if not d:
        return "—"
    try:
        y, m, day = d.split("-")
        return f"{day}/{m}/{y}"
    except Exception:
        return d


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _try_delete(update: Update) -> None:
    try:
        await update.message.delete()
    except (BadRequest, Exception):
        pass


def _clear(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    for k in ("kyc_session", "kyc_has_screenshot", "kyc_result"):
        ctx.user_data.pop(k, None)
