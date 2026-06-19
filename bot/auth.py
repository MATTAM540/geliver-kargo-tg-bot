from functools import wraps
from telegram import Update
from telegram.ext import CallbackContext
from bot.config import ALLOWED_USER_IDS


def restricted(func):
    @wraps(func)
    async def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in ALLOWED_USER_IDS:
            if update.callback_query:
                await update.callback_query.answer("Bu işlem için yetkiniz yok.", show_alert=True)
            elif update.message:
                await update.message.reply_text("Bu işlem için yetkiniz yok.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper
