from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from bot.api_client import api
from bot.keyboards import main_menu_keyboard, back_to_menu_button


async def price_start(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    context.user_data["state"] = "price_length"
    await query.edit_message_text(
        "📦 Yeni fiyat sorgulama\n\nLütfen paketin boyunu (cm) girin:",
        reply_markup=back_to_menu_button(),
    )


async def price_length(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    try:
        val = float(text)
    except ValueError:
        await update.message.reply_text("Geçersiz değer. Lütfen sayısal bir boy değeri girin (cm):", reply_markup=back_to_menu_button())
        return
    context.user_data["price_length"] = val
    context.user_data["state"] = "price_width"
    await update.message.reply_text("Eni (cm) girin:", reply_markup=back_to_menu_button())


async def price_width(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    try:
        val = float(text)
    except ValueError:
        await update.message.reply_text("Geçersiz değer. En (cm) girin:", reply_markup=back_to_menu_button())
        return
    context.user_data["price_width"] = val
    context.user_data["state"] = "price_height"
    await update.message.reply_text("Yüksekliği (cm) girin:", reply_markup=back_to_menu_button())


async def price_height(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    try:
        val = float(text)
    except ValueError:
        await update.message.reply_text("Geçersiz değer. Yükseklik (cm) girin:", reply_markup=back_to_menu_button())
        return
    context.user_data["price_height"] = val
    context.user_data["state"] = "price_weight"
    await update.message.reply_text("Ağırlığı (kg) girin:", reply_markup=back_to_menu_button())


async def price_weight(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    try:
        val = float(text)
    except ValueError:
        await update.message.reply_text("Geçersiz değer. Ağırlık (kg) girin:", reply_markup=back_to_menu_button())
        return

    length = context.user_data.get("price_length")
    width = context.user_data.get("price_width")
    height = context.user_data.get("price_height")
    context.user_data.pop("state", None)

    await update.message.reply_text("⏳ Fiyatlar hesaplanıyor...")

    try:
        result = await api.get_prices(length, width, height, val)
    except Exception:
        await update.message.reply_text("API bağlantı hatası.", reply_markup=main_menu_keyboard())
        return

    if not result.get("result"):
        err_msg = result.get("additionalMessage") or result.get("message") or "Bilinmeyen hata"
        await update.message.reply_text(f"Fiyat sorgulanamadı: {err_msg}", reply_markup=main_menu_keyboard())
        return

    price_list = result.get("priceList", [])
    if not price_list:
        await update.message.reply_text("Bu ölçülere uygun teklif bulunamadı.", reply_markup=main_menu_keyboard())
        return

    offers = price_list[0].get("offers", [])
    desi = price_list[0].get("desi", "-")

    by_provider = {}
    for offer in offers:
        provider = offer["providerCode"]
        transport = offer.get("transportType", "")
        total = offer.get("totalAmount", "0")
        currency = offer.get("currency", "TL")
        if provider not in by_provider:
            by_provider[provider] = {}
        by_provider[provider][transport] = (total, currency)

    result = []
    for provider, types in by_provider.items():
        unique_prices = set(v[0] for v in types.values())
        if len(unique_prices) == 1:
            total, currency = list(types.values())[0]
            if len(types) > 1:
                transport_label = "Şehir İçi - Dışı"
            else:
                transport_label = list(types.keys())[0]
            result.append((float(total), total, currency, provider, transport_label))
        else:
            for transport, (total, currency) in types.items():
                result.append((float(total), total, currency, provider, transport))

    result.sort(key=lambda x: x[0])

    message = f"📦 Kargo Fiyatları\n\n"
    message += f"Boyut: {length}×{width}×{height} cm | Ağırlık: {val} kg\n"
    message += f"Desi: {desi}\n\n"

    for i, (_, total, currency, provider, transport) in enumerate(result, 1):
        message += f"{i}. {provider}"
        if transport:
            message += f" ({transport})"
        message += f"\n   Toplam: {total} {currency}\n\n"

    await update.message.reply_text(message, reply_markup=main_menu_keyboard())
