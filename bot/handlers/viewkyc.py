"""Handler lệnh /viewkyc — xem toàn bộ thông tin KYC đã nộp."""
from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.session import is_logged_in, get_token, get_role
from bot.keyboards import main_menu, main_menu_reply
import bot.api_client as api


async def cmd_viewkyc(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    em = update.effective_message
    if not is_logged_in(uid):
        await em.reply_text(
            "🔒 *Cần đăng nhập trước*\n\n👉 Dùng /login để đăng nhập.",
            parse_mode="Markdown",
        )
        return

    token = get_token(uid)
    lines: list[str] = ["━━━━━━━━━━━━━━━━━━━━━━",
                        "📋 *Thông tin KYC của bạn*",
                        "━━━━━━━━━━━━━━━━━━━━━━\n"]

    # ── KYC VNeID v2 (Live Text + QR) ─────────────────────────────────────────
    v2 = await api.get_kycvneid2_status(token)
    if v2 and v2.get("status") not in (None, "NOT_SUBMITTED"):
        lines.append("🪪 *KYC VNeID (Live Text + QR)*")
        lines.append(_badge(v2["status"]))
        ld = v2.get("live_data") or {}
        qd = v2.get("qr_data")  or {}
        # Ưu tiên live_data, fallback qr_data
        name      = ld.get("full_name")      or qd.get("full_name")      or v2.get("full_name")
        cccd      = ld.get("id_number")      or qd.get("cccd")           or v2.get("cccd")
        dob       = ld.get("date_of_birth")  or qd.get("date_of_birth")  or v2.get("date_of_birth")
        gender    = ld.get("gender")         or qd.get("gender")
        nation    = ld.get("nationality")
        residence = ld.get("place_of_residence")
        birthplace= ld.get("place_of_birth")
        issue     = ld.get("issue_date")
        expiry    = ld.get("expiry_date")    or qd.get("expiry_date")

        if cccd:
            lines.append(f"🔢 Số CCCD: `{_mask(cccd)}`")
        if name:
            lines.append(f"👤 Họ tên: {name}")
        if dob:
            lines.append(f"🎂 Ngày sinh: {_fmt(dob)}")
        if gender:
            lines.append(f"⚧ Giới tính: {'Nam ♂' if gender=='male' else 'Nữ ♀' if gender=='female' else gender}")
        if nation:
            lines.append(f"🌏 Quốc tịch: {nation}")
        if residence:
            lines.append(f"🏠 Nơi cư trú: {residence}")
        if birthplace:
            lines.append(f"📍 Nơi sinh: {birthplace}")
        if issue:
            lines.append(f"📅 Ngày cấp: {_fmt(issue)}")
        if expiry:
            lines.append(f"⏳ Hết hạn: {_fmt(expiry)}")
        vm = v2.get("verify_method")
        if vm:
            labels = {
                "QR_LIVETEXT_MATCH":    "✅ Tự động (QR + Live Text khớp)",
                "QR_LIVETEXT_MISMATCH": "⚠️ Cần xét duyệt (có sai lệch)",
            }
            lines.append(f"🔍 Phương thức: {labels.get(vm, vm)}")
        portrait = v2.get("portrait_uploaded") or v2.get("portrait_image_path")
        lines.append(f"🤳 Ảnh chân dung: {'✅ Đã nộp' if portrait else '_(chưa nộp)_'}")
        lines.append("")
    else:
        lines.append("🪪 *KYC VNeID (Live Text + QR)*: _(chưa nộp)_\n")

    # ── KYC VNeID cũ (Live Text thủ công) ────────────────────────────────────
    vn = await api.get_kyc_vneid_status(token)
    vn_status = (vn or {}).get("kyc_status") or (vn or {}).get("status")
    if vn and vn_status not in (None, "NOT_SUBMITTED"):
        lines.append("📱 *KYC VNeID (Live Text)*")
        lines.append(_badge(vn_status))
        if vn.get("full_name"):
            lines.append(f"👤 Họ tên: {vn['full_name']}")
        if vn.get("id_number"):
            lines.append(f"🔢 Số CCCD: `{_mask(vn['id_number'])}`")
        if vn.get("confirmed_at"):
            lines.append(f"📅 Xác nhận lúc: {vn['confirmed_at'][:10]}")
        portrait = vn.get("has_portrait") or vn.get("portrait_path")
        lines.append(f"🤳 Ảnh chân dung: {'✅ Đã nộp' if portrait else '_(chưa nộp)_'}")
        lines.append("")

    # ── eKYC (PDF) ────────────────────────────────────────────────────────────
    ek = await api.get_ekyc_status(token)
    if ek and ek.get("status") not in (None, "NOT_SUBMITTED"):
        lines.append("📄 *eKYC (PDF)*")
        lines.append(_badge(ek["status"]))
        lines.append("")

    # ── KYC ảnh (front/back/portrait) ─────────────────────────────────────────
    ks = await api.get_kyc_status(token)
    if ks and ks.get("status") not in (None, "NOT_SUBMITTED", "not_found"):
        lines.append("🖼 *KYC ảnh (CCCD + chân dung)*")
        lines.append(_badge(ks.get("status", "")))
        if ks.get("full_name"):
            lines.append(f"👤 Họ tên: {ks['full_name']}")
        if ks.get("id_number"):
            lines.append(f"🔢 Số CCCD: `{_mask(ks['id_number'])}`")
        if ks.get("rejection_reason"):
            lines.append(f"❌ Lý do từ chối: _{ks['rejection_reason']}_")
        lines.append("")

    if len(lines) <= 4:
        lines.append("_(Bạn chưa nộp hồ sơ KYC nào)_\n")
        lines.append("👉 Dùng /kycvneid để bắt đầu xác minh danh tính.")
    else:
        lines.append("━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("💡 Dùng /kycvneid để nộp hoặc cập nhật hồ sơ.")

    await em.reply_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=main_menu_reply(get_role(uid)),
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _badge(status: str) -> str:
    m = {
        "VERIFIED":           "  ✅ Đã xác minh tự động",
        "CONFIRMED":          "  ✅ Đã xác nhận",
        "NEED_MANUAL_REVIEW": "  ⏳ Chờ xét duyệt thủ công",
        "PENDING":            "  ⏳ Đang xử lý",
        "APPROVED":           "  ✅ Đã duyệt",
        "REJECTED":           "  ❌ Bị từ chối",
        "SUBMITTED":          "  📥 Đã nộp",
    }
    return m.get(status, f"  📋 {status}")


def _mask(cccd: str) -> str:
    if len(cccd) <= 7:
        return cccd
    return f"{cccd[:3]}{'*' * (len(cccd) - 7)}{cccd[-4:]}"


def _fmt(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        parts = iso[:10].split("-")
        if len(parts) == 3:
            return f"{parts[2]}/{parts[1]}/{parts[0]}"
    except Exception:
        pass
    return iso
