from telegram import Update, BotCommand
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters,
)
from bot.config import TELEGRAM_BOT_TOKEN
from bot.handlers.menu import start, menu_callback, balance_check, error_handler
from bot.handlers.price import price_start
from bot.handlers.addresses import (
    address_list, address_view, address_delete,
    address_add_start, address_type_select, address_city, address_district,
)
from bot.handlers.shipments import (
    shipment_menu, shipment_list, shipment_view,
    shipment_cancel_confirm, shipment_cancel_execute,
    ship_create_start, ship_sender_select, ship_recipient_select,
    ship_offer_select,
)
from bot.handlers.returns import return_start, return_execute
from bot.handlers.webhooks import (
    webhook_list, webhook_view, webhook_delete, webhook_test,
    webhook_add_start, webhook_type_select,
)
from bot.handlers.router import state_message_handler
from bot.api_client import api


async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "Botu başlat"),
    ])


async def shutdown(application):
    await api.close()


def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).post_shutdown(shutdown).build()

    # Komut
    app.add_handler(CommandHandler("start", start))

    # Ana Menü callback
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu_main$"))

    # ── Bakiye Sorgulama ──
    app.add_handler(CallbackQueryHandler(balance_check, pattern="^menu_balance$"))

    # ── Fiyat Sorgulama ──
    app.add_handler(CallbackQueryHandler(price_start, pattern="^menu_price$"))

    # ── Adresler ──
    app.add_handler(CallbackQueryHandler(address_list, pattern="^(menu_addresses$|addr_page_)"))
    app.add_handler(CallbackQueryHandler(address_view, pattern="^addr_view_"))
    app.add_handler(CallbackQueryHandler(address_delete, pattern="^addr_del_"))
    app.add_handler(CallbackQueryHandler(address_add_start, pattern="^addr_add_start$"))
    app.add_handler(CallbackQueryHandler(address_type_select, pattern="^addr_type_"))
    app.add_handler(CallbackQueryHandler(address_city, pattern="^addr_city_"))
    app.add_handler(CallbackQueryHandler(address_district, pattern="^addr_dist_"))

    # ── Gönderiler ──
    app.add_handler(CallbackQueryHandler(shipment_menu, pattern="^menu_shipments$"))
    app.add_handler(CallbackQueryHandler(shipment_list, pattern="^ship_list_"))
    app.add_handler(CallbackQueryHandler(shipment_view, pattern="^ship_view_"))
    app.add_handler(CallbackQueryHandler(shipment_cancel_confirm, pattern="^ship_cancel_(?!confirm_)"))
    app.add_handler(CallbackQueryHandler(shipment_cancel_execute, pattern="^ship_cancel_confirm_"))
    app.add_handler(CallbackQueryHandler(ship_create_start, pattern="^menu_ship$"))
    app.add_handler(CallbackQueryHandler(ship_sender_select, pattern="^ship_sender_"))
    app.add_handler(CallbackQueryHandler(ship_recipient_select, pattern="^ship_recipient_"))
    app.add_handler(CallbackQueryHandler(ship_offer_select, pattern="^ship_offer_"))

    # ── İade ──
    app.add_handler(CallbackQueryHandler(return_start, pattern="^(menu_return$|return_page_)"))
    app.add_handler(CallbackQueryHandler(return_execute, pattern="^return_ship_"))

    # ── Webhook'lar ──
    app.add_handler(CallbackQueryHandler(webhook_list, pattern="^menu_webhooks$"))
    app.add_handler(CallbackQueryHandler(webhook_view, pattern="^wh_view_"))
    app.add_handler(CallbackQueryHandler(webhook_delete, pattern="^wh_del_"))
    app.add_handler(CallbackQueryHandler(webhook_test, pattern="^wh_test$"))
    app.add_handler(CallbackQueryHandler(webhook_add_start, pattern="^wh_add_start$"))
    app.add_handler(CallbackQueryHandler(webhook_type_select, pattern="^wh_type_"))

    # State-based text message handler (for multi-step flows)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, state_message_handler))

    # Hata yakalama
    app.add_error_handler(error_handler)

    print("KargoBot başlatıldı!")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
