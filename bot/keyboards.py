from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard():
    buttons = [
        [InlineKeyboardButton("📦 Fiyat Sorgula", callback_data="menu_price")],
        [InlineKeyboardButton("📍 Adreslerim", callback_data="menu_addresses")],
        [InlineKeyboardButton("🚚 Kargo Gönder", callback_data="menu_ship")],
        [InlineKeyboardButton("📋 Kargolarım", callback_data="menu_shipments")],
        [InlineKeyboardButton("🔄 Kargo İade", callback_data="menu_return")],
        [InlineKeyboardButton("🔗 Webhook'lar", callback_data="menu_webhooks")],
    ]
    return InlineKeyboardMarkup(buttons)


def back_to_menu_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Ana Menü", callback_data="menu_main")]
    ])


def confirm_cancel_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Evet", callback_data="confirm_yes"),
            InlineKeyboardButton("❌ Hayır", callback_data="confirm_no"),
        ]
    ])


