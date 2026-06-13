"""Entry point cho Telegram Bot P2PSuperBot."""
import asyncio
import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)
from backend.core.config import settings
from bot.handlers.common import cmd_start, cmd_help, cmd_cancel
from bot.handlers import auth, profile, kyc, wallet, credits, admin, superadmin
from bot.handlers import kyc_admin
from bot.handlers import kyc_vneid as kyc_vn
from bot.handlers import kyc_livetext as kyc_lt
from bot.handlers import kycvneid as kycvn2
from bot.handlers import viewkyc
from bot.handlers import menu as menu_h
from bot.handlers.menu import (
    ALL_MENU_TEXTS,
    CB_BACK_MAIN, CB_CLEAR_CHAT,
    CB_MENU_PROFILE, CB_MENU_CUSTOMER, CB_MENU_P2P,
    CB_MENU_STORES, CB_MENU_TOOLS, CB_MENU_SETTINGS, CB_MENU_HELP,
    CB_START_KYCVNEID,
)

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def build_app() -> Application:
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    cancel_handler = CommandHandler("cancel", cmd_cancel)

    # ── Register ─────────────────────────────────────────────────────────────
    register_conv = ConversationHandler(
        entry_points=[CommandHandler("register", auth.cmd_register)],
        states={
            auth.REG_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth.reg_email)],
        },
        fallbacks=[cancel_handler],
        allow_reentry=True,
    )

    # ── Login ─────────────────────────────────────────────────────────────────
    login_conv = ConversationHandler(
        entry_points=[
            CommandHandler("login", auth.cmd_login),
            CallbackQueryHandler(auth.cb_goto_login, pattern="^goto_login$"),
        ],
        states={
            auth.LOGIN_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth.login_email)],
            auth.LOGIN_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth.login_password)],
            auth.LOGIN_2FA: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth.login_2fa)],
            auth.CHANGE_PW_NEW: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth.change_pw_new)],
            auth.CHANGE_PW_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth.change_pw_confirm)],
        },
        fallbacks=[cancel_handler],
        allow_reentry=True,
        per_message=False,
    )

    # ── Resend Verification ───────────────────────────────────────────────────
    resend_conv = ConversationHandler(
        entry_points=[
            CommandHandler("resend", auth.cmd_resend),
            CallbackQueryHandler(auth.cb_goto_resend, pattern="^goto_resend$"),
        ],
        states={
            auth.RESEND_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth.resend_email)],
        },
        fallbacks=[cancel_handler],
        allow_reentry=True,
        per_message=False,
    )

    # ── 2FA Setup ─────────────────────────────────────────────────────────────
    twofa_conv = ConversationHandler(
        entry_points=[CommandHandler("2fa_setup", auth.cmd_2fa_setup)],
        states={
            auth.FA_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth.fa_code_verify)],
        },
        fallbacks=[cancel_handler],
        allow_reentry=True,
    )

    # ── Profile Update ────────────────────────────────────────────────────────
    profile_update_conv = ConversationHandler(
        entry_points=[CommandHandler("profile_update", profile.cmd_profile_update)],
        states={
            profile.PROFILE_UPDATE_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile.profile_value)],
        },
        fallbacks=[cancel_handler],
        allow_reentry=True,
    )

    # ── KYC VNeID (flow mới — screenshot + Live Text) ─────────────────────────
    kyc_conv = ConversationHandler(
        entry_points=[
            CommandHandler("kyc", kyc_vn.cmd_kyc),
            CallbackQueryHandler(kyc_vn.cb_kyc_start, pattern="^kyc_vneid_start$"),
        ],
        states={
            kyc_vn.VNEID_SCREENSHOT: [
                MessageHandler(filters.PHOTO, kyc_vn.vneid_screenshot),
                MessageHandler(filters.TEXT & ~filters.COMMAND, kyc_vn.vneid_screenshot),
            ],
            kyc_vn.VNEID_LIVETEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, kyc_vn.vneid_livetext),
                MessageHandler(filters.PHOTO, kyc_vn.vneid_livetext),
            ],
            kyc_vn.VNEID_CONFIRM: [
                CallbackQueryHandler(kyc_vn.cb_confirm,          pattern="^kyc_vneid_confirm$"),
                CallbackQueryHandler(kyc_vn.cb_retry_livetext,   pattern="^kyc_vneid_retry$"),
                CallbackQueryHandler(kyc_vn.cb_redo_screenshot,  pattern="^kyc_vneid_redo_screenshot$"),
            ],
        },
        fallbacks=[cancel_handler],
        allow_reentry=True,
        per_message=False,
    )

    # ── eKYC ─────────────────────────────────────────────────────────────────
    ekyc_conv = ConversationHandler(
        entry_points=[CommandHandler("ekyc", kyc.cmd_ekyc)],
        states={
            kyc.EKYC_PDF: [MessageHandler(filters.Document.PDF, kyc.ekyc_pdf)],
        },
        fallbacks=[cancel_handler],
        allow_reentry=True,
    )

    # ── Admin KYC reject conversation ─────────────────────────────────────────
    kyc_reject_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(kyc_admin.cb_kyc_reject_start, pattern="^kyc_reject_start_")],
        states={
            kyc_admin.KYC_REJECT_REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, kyc_admin.kyc_reject_reason)],
        },
        fallbacks=[cancel_handler],
        allow_reentry=True,
        per_message=False,
    )

    # ── Add Wallet ────────────────────────────────────────────────────────────
    wallet_conv = ConversationHandler(
        entry_points=[CommandHandler("add_wallet", wallet.cmd_add_wallet)],
        states={
            wallet.WALLET_ADDRESS: [
                CallbackQueryHandler(wallet.network_selected, pattern="^net_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, wallet.wallet_address),
            ],
        },
        fallbacks=[cancel_handler],
        allow_reentry=True,
        per_message=False,
    )

    # ── Admin: Reject Review ──────────────────────────────────────────────────
    reject_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin.handle_reject_start, pattern="^reject_")],
        states={
            admin.REJECT_REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin.handle_reject_reason)],
        },
        fallbacks=[cancel_handler],
        allow_reentry=True,
        per_message=False,
    )

    # ── Super Admin: Create Admin ─────────────────────────────────────────────
    create_admin_conv = ConversationHandler(
        entry_points=[CommandHandler("create_admin", superadmin.cmd_create_admin)],
        states={
            superadmin.CREATE_ADMIN_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, superadmin.create_admin_email)],
        },
        fallbacks=[cancel_handler],
        allow_reentry=True,
    )

    # ── KYC Live Text — auto-detect paste + upload ảnh ───────────────────────
    # Phải đứng TRƯỚC kyc_conv để bắt text CCCD ở mọi trạng thái
    kyc_lt_conv = ConversationHandler(
        entry_points=[
            MessageHandler(kyc_lt.cccd_text_filter, kyc_lt.auto_detect_cccd),
        ],
        states={
            kyc_lt.LT_SCREENSHOT: [
                MessageHandler(filters.PHOTO,                   kyc_lt.receive_screenshot),
                CallbackQueryHandler(kyc_lt.cb_skip_screenshot, pattern="^lt_skip_screenshot$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, kyc_lt.receive_screenshot),
            ],
            kyc_lt.LT_PORTRAIT: [
                MessageHandler(filters.PHOTO,                   kyc_lt.receive_portrait),
                CallbackQueryHandler(kyc_lt.cb_skip_portrait,   pattern="^lt_skip_portrait$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, kyc_lt.receive_portrait),
            ],
            kyc_lt.LT_CONFIRM: [
                CallbackQueryHandler(kyc_lt.cb_lt_confirm, pattern="^lt_kyc_confirm$"),
                CallbackQueryHandler(kyc_lt.cb_lt_retry,   pattern="^lt_kyc_retry$"),
            ],
        },
        fallbacks=[cancel_handler],
        allow_reentry=False,
        per_message=False,
    )

    # ── KYC VNeID v2 — /kycvneid: Live Text + QR verify + portrait ──────────────
    kycvneid2_conv = ConversationHandler(
        entry_points=[
            CommandHandler("kycvneid", kycvn2.cmd_kycvneid),
            CallbackQueryHandler(kycvn2.cmd_kycvneid, pattern=f"^{CB_START_KYCVNEID}$"),
        ],
        states={
            kycvn2.KV2_COLLECTING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, kycvn2.collecting_text),
                MessageHandler(filters.PHOTO,                   kycvn2.collecting_photo),
            ],
            kycvn2.KV2_PORTRAIT: [
                MessageHandler(filters.PHOTO,                   kycvn2.portrait_photo),
                MessageHandler(filters.TEXT & ~filters.COMMAND, kycvn2.portrait_text),
                CallbackQueryHandler(kycvn2.cb_skip_portrait,   pattern="^kv2_skip_portrait$"),
            ],
        },
        fallbacks=[cancel_handler],
        allow_reentry=False,
        per_message=False,
    )

    # Register all handlers
    for conv in [
        kycvneid2_conv,   # /kycvneid — phải đứng trước kyc_lt_conv
        kyc_lt_conv,      # auto-detect CCCD text
        register_conv, login_conv, resend_conv, twofa_conv,
        profile_update_conv, ekyc_conv,
        wallet_conv, reject_conv, create_admin_conv,
        kyc_reject_conv,
    ]:
        app.add_handler(conv)

    # ── Menu: Reply Keyboard text buttons ─────────────────────────────────────
    menu_text_filter = filters.TEXT & filters.Regex(
        "^(" + "|".join(map(lambda s: s.replace("(", r"\(").replace(")", r"\)"), ALL_MENU_TEXTS)) + ")$"
    ) & ~filters.COMMAND
    app.add_handler(MessageHandler(menu_text_filter, menu_h.handle_menu_text))

    # ── Menu: Inline callbacks — navigation ───────────────────────────────────
    app.add_handler(CallbackQueryHandler(menu_h.cb_back_main,      pattern=f"^{CB_BACK_MAIN}$"))
    app.add_handler(CallbackQueryHandler(menu_h.cb_clear_chat,     pattern=f"^{CB_CLEAR_CHAT}$"))
    app.add_handler(CallbackQueryHandler(menu_h.cb_menu_profile,   pattern=f"^{CB_MENU_PROFILE}$"))
    app.add_handler(CallbackQueryHandler(menu_h.cb_menu_customer,  pattern=f"^{CB_MENU_CUSTOMER}$"))
    app.add_handler(CallbackQueryHandler(menu_h.cb_menu_p2p,       pattern=f"^{CB_MENU_P2P}$"))
    app.add_handler(CallbackQueryHandler(menu_h.cb_menu_stores,    pattern=f"^{CB_MENU_STORES}$"))
    app.add_handler(CallbackQueryHandler(menu_h.cb_menu_tools,     pattern=f"^{CB_MENU_TOOLS}$"))
    app.add_handler(CallbackQueryHandler(menu_h.cb_menu_settings,  pattern=f"^{CB_MENU_SETTINGS}$"))
    app.add_handler(CallbackQueryHandler(menu_h.cb_menu_help,      pattern=f"^{CB_MENU_HELP}$"))

    # ── Menu: Inline callbacks — command dispatch ──────────────────────────────
    app.add_handler(CallbackQueryHandler(menu_h.cb_cmd_profile,    pattern="^CMD_PROFILE$"))
    app.add_handler(CallbackQueryHandler(menu_h.cb_cmd_viewkyc,    pattern="^CMD_VIEWKYC$"))
    app.add_handler(CallbackQueryHandler(menu_h.cb_cmd_wallets,    pattern="^CMD_WALLETS$"))
    app.add_handler(CallbackQueryHandler(menu_h.cb_cmd_credits,    pattern="^CMD_CREDITS$"))
    app.add_handler(CallbackQueryHandler(menu_h.cb_cmd_2fa,        pattern="^CMD_2FA$"))
    app.add_handler(CallbackQueryHandler(menu_h.cb_cmd_help,       pattern="^CMD_HELP$"))
    app.add_handler(CallbackQueryHandler(menu_h.cb_cmd_about,      pattern="^CMD_ABOUT$"))
    app.add_handler(CallbackQueryHandler(menu_h.cb_cmd_logout,     pattern="^CMD_LOGOUT$"))

    # ── Menu: Placeholder callbacks ────────────────────────────────────────────
    app.add_handler(CallbackQueryHandler(menu_h.cb_placeholder, pattern="^PH_"))

    # Simple commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("cancel", cmd_cancel))
    app.add_handler(CommandHandler("kyc", kyc_vn.cmd_kyc))
    app.add_handler(CommandHandler("logout", auth.cmd_logout))
    app.add_handler(CommandHandler("profile", profile.cmd_profile))
    app.add_handler(CommandHandler("wallets", wallet.cmd_wallets))
    app.add_handler(CommandHandler("credits", credits.cmd_credits))
    app.add_handler(CommandHandler("viewkyc", viewkyc.cmd_viewkyc))
    app.add_handler(CommandHandler("review_queue", admin.cmd_review_queue))
    app.add_handler(CommandHandler("security_alerts", admin.cmd_security_alerts))
    app.add_handler(CommandHandler("audit_logs", superadmin.cmd_audit_logs))
    app.add_handler(CommandHandler("kyc_queue", kyc_admin.cmd_kyc_queue))

    # Callback queries — admin
    app.add_handler(CallbackQueryHandler(admin.handle_approve, pattern="^approve_"))
    app.add_handler(CallbackQueryHandler(kyc_admin.cb_kyc_view, pattern="^kyc_view_"))
    app.add_handler(CallbackQueryHandler(kyc_admin.cb_kyc_approve, pattern="^kyc_approve_"))

    return app


async def main():
    logger.info("Starting P2PSuperBot...")
    app = build_app()
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        logger.info("Bot is running. Press Ctrl+C to stop.")
        await asyncio.Event().wait()  # chờ vô tận


if __name__ == "__main__":
    asyncio.run(main())
