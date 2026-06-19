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


def pagination_keyboard(current_page: int, total_pages: int, prefix: str):
    buttons = []
    if current_page > 1:
        buttons.append(InlineKeyboardButton("◀️", callback_data=f"{prefix}_page_{current_page - 1}"))
    if current_page < total_pages:
        buttons.append(InlineKeyboardButton("▶️", callback_data=f"{prefix}_page_{current_page + 1}"))
    row = []
    if buttons:
        row = buttons
    return InlineKeyboardMarkup([row] if row else [])
