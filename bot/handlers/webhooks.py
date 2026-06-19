from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from bot.auth import restricted
from bot.api_client import api
from bot.keyboards import main_menu_keyboard


# ── Liste ──

@restricted
async def webhook_list(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    try:
        result = await api.get_webhooks()
    except Exception:
        await query.edit_message_text("API bağlantı hatası.", reply_markup=main_menu_keyboard())
        return

    if not result.get("result"):
        await query.edit_message_text("Webhook'lar alınamadı.", reply_markup=main_menu_keyboard())
        return

    webhooks = result.get("data", [])

    buttons = []
    for wh in webhooks:
        active = "✅" if wh.get("isActive") else "❌"
        label = f"{active} {wh.get('type', '-')} | {wh.get('url', '-')[:40]}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"wh_view_{wh['id']}")])

    buttons.append([InlineKeyboardButton("➕ Webhook Ekle", callback_data="wh_add_start")])
    buttons.append([InlineKeyboardButton("🧪 Test Webhook", callback_data="wh_test")])
    buttons.append([InlineKeyboardButton("🔙 Ana Menü", callback_data="menu_main")])

    if not webhooks:
        text = "Kayıtlı webhook bulunmuyor."
    else:
        text = "🔗 Webhook'larınız:"

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# ── Detay ──

@restricted
async def webhook_view(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    webhook_id = query.data.replace("wh_view_", "")

    try:
        result = await api.get_webhooks()
    except Exception:
        await query.edit_message_text("API bağlantı hatası.", reply_markup=main_menu_keyboard())
        return

    wh = next((w for w in result.get("data", []) if w["id"] == webhook_id), None)

    if not wh:
        await query.edit_message_text(
            "Webhook bulunamadı.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Webhook'lar", callback_data="menu_webhooks")]
            ]),
        )
        return

    active = "✅ Aktif" if wh.get("isActive") else "❌ Pasif"
    msg = (
        f"🔗 Webhook Detayı\n\n"
        f"ID: {wh['id']}\n"
        f"Tür: {wh.get('type', '-')}\n"
        f"URL: {wh.get('url', '-')}\n"
        f"Header: {wh.get('headerName', '-')}: {wh.get('headerValue', '-')}\n"
        f"Durum: {active}\n"
        f"Oluşturma: {wh.get('createdAt', '-')}"
    )

    await query.edit_message_text(
        msg,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🗑 Sil", callback_data=f"wh_del_{wh['id']}")],
            [InlineKeyboardButton("🔙 Webhook'lar", callback_data="menu_webhooks")],
            [InlineKeyboardButton("🔙 Ana Menü", callback_data="menu_main")],
        ]),
    )


# ── Silme ──

@restricted
async def webhook_delete(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    webhook_id = query.data.replace("wh_del_", "")

    try:
        result = await api.delete_webhook(webhook_id)
    except Exception:
        await query.edit_message_text("API bağlantı hatası.", reply_markup=main_menu_keyboard())
        return

    if result.get("result"):
        await query.edit_message_text(
            "✅ Webhook başarıyla silindi.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Webhook'lar", callback_data="menu_webhooks")],
                [InlineKeyboardButton("🔙 Ana Menü", callback_data="menu_main")],
            ]),
        )
    else:
        err = result.get("additionalMessage") or result.get("message") or "Bilinmeyen hata"
        await query.edit_message_text(
            f"❌ Silinemedi: {err}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Webhook'lar", callback_data="menu_webhooks")]
            ]),
        )


# ── Test ──

@restricted
async def webhook_test(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    try:
        result = await api.test_webhook()
    except Exception:
        await query.edit_message_text("API bağlantı hatası.", reply_markup=main_menu_keyboard())
        return

    if result.get("result"):
        await query.edit_message_text(
            "✅ Test webhook'u başarıyla oluşturuldu!",
            reply_markup=main_menu_keyboard(),
        )
    else:
        err = result.get("additionalMessage") or result.get("message") or "Bilinmeyen hata"
        await query.edit_message_text(
            f"❌ Test başarısız: {err}",
            reply_markup=main_menu_keyboard(),
        )


# ── Ekleme (state machine) ──

@restricted
async def webhook_add_start(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    context.user_data["new_wh"] = {}
    context.user_data["state"] = "wh_type"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("TRACK_UPDATED", callback_data="wh_type_TRACK_UPDATED")],
        [InlineKeyboardButton("🔙 Webhook'lar", callback_data="menu_webhooks")],
    ])
    await query.edit_message_text("Webhook türünü seçin:", reply_markup=keyboard)


async def webhook_type_select(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    wh_type = query.data.replace("wh_type_", "")
    context.user_data["new_wh"]["type"] = wh_type
    context.user_data["state"] = "wh_url"
    await query.edit_message_text("Webhook URL'sini girin (örn: https://hook.example.com/path):")


async def webhook_url(update: Update, context: CallbackContext):
    context.user_data["new_wh"]["url"] = update.message.text.strip()
    context.user_data["state"] = "wh_header_name"
    await update.message.reply_text("Header adı girin (opsiyonel, boş bırakmak için - yazın):")


async def webhook_header_name(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    context.user_data["new_wh"]["headerName"] = "" if text == "-" else text
    context.user_data["state"] = "wh_header_value"
    await update.message.reply_text("Header değeri girin (opsiyonel, boş bırakmak için - yazın):")


async def webhook_header_value(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    context.user_data["new_wh"]["headerValue"] = "" if text == "-" else text
    wh = context.user_data["new_wh"]
    context.user_data.pop("state", None)

    try:
        result = await api.create_webhook(wh)
    except Exception:
        await update.message.reply_text("Webhook oluşturulurken API hatası.", reply_markup=main_menu_keyboard())
        return

    if result.get("result"):
        wh_id = result.get("data", {}).get("id", "")
        await update.message.reply_text(
            f"✅ Webhook başarıyla oluşturuldu!\nID: {wh_id}",
            reply_markup=main_menu_keyboard(),
        )
    else:
        err = result.get("additionalMessage") or result.get("message") or "Bilinmeyen hata"
        await update.message.reply_text(
            f"❌ Webhook oluşturulamadı: {err}",
            reply_markup=main_menu_keyboard(),
        )
