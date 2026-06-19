from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from bot.auth import restricted
from bot.api_client import api
from bot.keyboards import main_menu_keyboard


@restricted
async def return_start(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    try:
        result = await api.get_shipments(page=1, limit=50)
    except Exception:
        await query.edit_message_text("API bağlantı hatası.", reply_markup=main_menu_keyboard())
        return

    if not result.get("result"):
        await query.edit_message_text("Gönderiler alınamadı.", reply_markup=main_menu_keyboard())
        return

    shipments = result.get("data", [])
    if not shipments:
        await query.edit_message_text(
            "İade edilecek gönderi bulunmuyor.",
            reply_markup=main_menu_keyboard(),
        )
        return

    buttons = []
    for s in shipments:
        barcode = s.get("barcode", "-")
        status = s.get("trackingStatus", {}).get("statusDetails", "-")
        label = f"📦 {barcode} | {status}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"return_ship_{s['id']}")])

    buttons.append([InlineKeyboardButton("🔙 Ana Menü", callback_data="menu_main")])

    await query.edit_message_text(
        "🔄 İade edilecek gönderiyi seçin:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@restricted
async def return_execute(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    shipment_id = query.data.replace("return_ship_", "")

    await query.edit_message_text("⏳ İade talebi oluşturuluyor...")

    try:
        result = await api.return_shipment(shipment_id)
    except Exception:
        await query.edit_message_text("API bağlantı hatası.", reply_markup=main_menu_keyboard())
        return

    if result.get("result"):
        await query.edit_message_text(
            "✅ İade talebi başarıyla oluşturuldu!",
            reply_markup=main_menu_keyboard(),
        )
    else:
        err = result.get("additionalMessage") or result.get("message") or "Bilinmeyen hata"
        await query.edit_message_text(
            f"❌ İade oluşturulamadı: {err}",
            reply_markup=main_menu_keyboard(),
        )
