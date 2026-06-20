from telegram import Update
from telegram.ext import CallbackContext
from bot.keyboards import main_menu_keyboard, back_to_menu_button


async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "🚀 KargoBot'a hoş geldin!\n\n"
        "Aşağıdaki menüden yapmak istediğin işlemi seç:",
        reply_markup=main_menu_keyboard(),
    )


async def menu_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_main":
        await query.edit_message_text(
            "🚀 KargoBot Ana Menü\n\nYapmak istediğin işlemi seç:",
            reply_markup=main_menu_keyboard(),
        )


async def balance_check(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    try:
        from bot.api_client import api
        result = await api.get_balance()
        data = result.get("data", "0")
        debt = result.get("debt", "0")
        text = (
            f"💰 Bakiye Bilgisi\n\n"
            f"Bakiye: {data} TL\n"
            f"Borç: {debt} TL"
        )
    except Exception:
        text = "Bakiye sorgulanırken bir hata oluştu."

    await query.edit_message_text(
        text,
        reply_markup=back_to_menu_button(),
    )


async def error_handler(update: object, context: CallbackContext):
    error_text = f"Hata oluştu: {context.error}"
    print(error_text)
    if update and hasattr(update, "effective_chat") and update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Bir hata oluştu. Lütfen daha sonra tekrar deneyin.",
        )
