from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from bot.auth import restricted
from bot.api_client import api
from bot.keyboards import main_menu_keyboard


# ── Gönderi Listesi ──

PENDING_STATUSES = {"", None, "CREATED", "PROCESSING", "PRE_TRANSIT"}
TRANSIT_STATUSES = {"TRANSIT", "PICKED_UP", "OUT_FOR_DELIVERY"}

STATUS_LABELS = {
    "PRE_TRANSIT": "Sisteme Kaydedildi",
    "TRANSIT": "Yolda",
    "PICKED_UP": "Teslim Alındı",
    "OUT_FOR_DELIVERY": "Dağıtımda",
    "DELIVERED": "Teslim Edildi",
    "FAILURE": "Hata",
    "RETURNED": "İade Edildi",
    "UNKNOWN": "Bilinmeyen",
}
PAGE_SIZE = 11


@restricted
async def shipment_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🟡 Henüz Gönderilmeyenler", callback_data="ship_list_pending")],
        [InlineKeyboardButton("🟢 Yolda Olanlar", callback_data="ship_list_transit")],
        [InlineKeyboardButton("📦 Tüm Kargolar", callback_data="ship_list_all")],
        [InlineKeyboardButton("🔙 Ana Menü", callback_data="menu_main")],
    ])
    await query.edit_message_text("📋 Kargolarım\n\nListelemek istediğiniz kategoriyi seçin:", reply_markup=keyboard)


@restricted
async def shipment_list(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    raw = query.data.replace("ship_list_", "")
    if "_" in raw:
        parts = raw.rsplit("_", 1)
        if parts[-1].isdigit():
            filter_mode = parts[0]
            page = int(parts[-1])
        else:
            filter_mode = raw
            page = 1
    else:
        filter_mode = raw
        page = 1

    while True:
        try:
            result = await api.get_shipments(page=page, limit=PAGE_SIZE)
        except Exception:
            await query.edit_message_text("API bağlantı hatası.", reply_markup=main_menu_keyboard())
            return

        if not result.get("result"):
            await query.edit_message_text("Gönderiler alınamadı.", reply_markup=main_menu_keyboard())
            return

        shipments = result.get("data", [])
        has_more_pages = len(shipments) == PAGE_SIZE

        if filter_mode == "pending":
            filtered = [
                s for s in shipments
                if (s.get("trackingStatus") or {}).get("trackingStatusCode") in PENDING_STATUSES
            ]
            title = "📋 Henüz Gönderilmeyenler"
        elif filter_mode == "transit":
            filtered = [
                s for s in shipments
                if (s.get("trackingStatus") or {}).get("trackingStatusCode") in TRANSIT_STATUSES
            ]
            title = "📋 Yolda Olanlar"
        else:
            filtered = shipments
            title = "📋 Tüm Kargolar"

        if not filtered and has_more_pages:
            page += 1
            continue
        break

    has_more = len(filtered) == PAGE_SIZE
    buttons = []
    for s in filtered:
        barcode = s.get("barcode", "-")
        ts = s.get("trackingStatus") or {}
        code = ts.get("trackingStatusCode", "")
        status = STATUS_LABELS.get(code, ts.get("statusDetails", "Bilinmiyor"))
        label = f"📦 {barcode} | {status}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"ship_view_{s['id']}")])

    if has_more or page > 1:
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("◀️ Önceki", callback_data=f"ship_list_{filter_mode}_{page - 1}"))
        if has_more:
            nav_buttons.append(InlineKeyboardButton("Sonraki ▶️", callback_data=f"ship_list_{filter_mode}_{page + 1}"))
        buttons.append(nav_buttons)

    buttons.append([InlineKeyboardButton("🔙 Kategoriler", callback_data="menu_shipments")])
    buttons.append([InlineKeyboardButton("🔙 Ana Menü", callback_data="menu_main")])

    if not filtered and page == 1:
        text = f"{title}\n\nBu kategoride gönderi bulunmuyor."
    elif not filtered:
        text = f"{title}\n\nBu sayfada gönderi bulunmuyor."
    elif has_more or page > 1:
        text = f"{title} (Sayfa {page}):"
    else:
        text = f"{title}:"

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# ── Gönderi Detayı ──

@restricted
async def shipment_view(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    shipment_id = query.data.replace("ship_view_", "")

    try:
        result = await api.get_shipment(shipment_id)
    except Exception:
        await query.edit_message_text("API bağlantı hatası.", reply_markup=main_menu_keyboard())
        return

    if not result.get("result"):
        s = None
    else:
        s = result.get("data")

    if not s:
        await query.edit_message_text(
            "Gönderi bulunamadı.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Gönderiler", callback_data="menu_shipments")]
            ]),
        )
        return

    tracking = s.get("trackingStatus", {})
    sender = s.get("senderAddress", {})
    recipient = s.get("recipientAddress", {})
    label_url = s.get("labelURL", "")
    tracking_url = s.get("trackingUrl", "")

    msg = (
        f"📦 Gönderi Detayı\n\n"
        f"Barkod: {s.get('barcode', '-')}\n"
        f"Takip No: {s.get('trackingNumber', '-')}\n"
        f"Durum: {tracking.get('statusDetails', 'Bilinmiyor')}\n"
        f"Konum: {tracking.get('locationName', '-')}\n"
        f"Tarih: {tracking.get('statusDate', '-')}\n\n"
        f"Gönderen: {sender.get('name', '-')}\n"
        f"Alıcı: {recipient.get('name', '-')}\n\n"
        f"Boyut: {s.get('length', '-')}×{s.get('width', '-')}×{s.get('height', '-')} cm\n"
        f"Ağırlık: {s.get('weight', '-')} kg | Desi: {s.get('desi', '-')}\n"
        f"Tutar: {s.get('totalAmount', '-')} {s.get('currency', 'TL')}\n"
    )

    buttons = []
    if label_url:
        buttons.append([InlineKeyboardButton("🏷 Etiketi Görüntüle", url=label_url)])
    if tracking_url:
        buttons.append([InlineKeyboardButton("🔍 Takip Et", url=tracking_url)])
    buttons.append([InlineKeyboardButton("🗑 Gönderiyi İptal Et", callback_data=f"ship_cancel_{s['id']}")])
    buttons.append([InlineKeyboardButton("🔙 Gönderiler", callback_data="menu_shipments")])
    buttons.append([InlineKeyboardButton("🔙 Ana Menü", callback_data="menu_main")])

    await query.edit_message_text(
        msg,
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# ── Gönderi İptali ──

@restricted
async def shipment_cancel_confirm(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    shipment_id = query.data.replace("ship_cancel_", "")

    await query.edit_message_text(
        "Bu gönderiyi iptal etmek istediğinize emin misiniz?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Evet, İptal Et", callback_data=f"ship_cancel_confirm_{shipment_id}")],
            [InlineKeyboardButton("❌ Vazgeç", callback_data=f"ship_view_{shipment_id}")],
        ]),
    )


@restricted
async def shipment_cancel_execute(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    shipment_id = query.data.replace("ship_cancel_confirm_", "")

    try:
        result = await api.cancel_shipment(shipment_id)
    except Exception:
        await query.edit_message_text("API bağlantı hatası.", reply_markup=main_menu_keyboard())
        return

    if result.get("result"):
        await query.edit_message_text("✅ Gönderi başarıyla iptal edildi.", reply_markup=main_menu_keyboard())
    else:
        err = result.get("additionalMessage") or result.get("message") or "Bilinmeyen hata"
        await query.edit_message_text(f"❌ İptal edilemedi: {err}", reply_markup=main_menu_keyboard())


# ── Kargo Gönder (state machine) ──

@restricted
async def ship_create_start(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    try:
        result = await api.get_addresses(page=1, limit=50)
    except Exception:
        await query.edit_message_text("Adres listesi alınamadı.", reply_markup=main_menu_keyboard())
        return

    if not result.get("result"):
        err = result.get("additionalMessage") or result.get("message") or "Bilinmeyen hata"
        await query.edit_message_text(f"Adres listesi alınamadı: {err}", reply_markup=main_menu_keyboard())
        return

    addresses = result.get("data", [])
    if not addresses:
        await query.edit_message_text(
            "Önce adres eklemelisiniz. 📍 Adreslerim menüsünden ekleyin.",
            reply_markup=main_menu_keyboard(),
        )
        return

    context.user_data["_addresses"] = addresses
    context.user_data["new_ship"] = {}
    context.user_data["state"] = "ship_sender"

    buttons = []
    for addr in addresses:
        name = addr.get("shortName") or addr.get("name", "-")
        city = addr.get("cityName", "")
        label = f"{name[:30]} - {city}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"ship_sender_{addr['id']}")])

    buttons.append([InlineKeyboardButton("🔙 Ana Menü", callback_data="menu_main")])

    await query.edit_message_text(
        "🚚 Kargo Gönderimi\n\nGönderici adresini seçin:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def ship_sender_select(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    sender_id = query.data.replace("ship_sender_", "")
    context.user_data["new_ship"]["senderAddressId"] = sender_id
    context.user_data["state"] = "ship_recipient"

    addresses = context.user_data.get("_addresses", [])
    buttons = []
    for addr in addresses:
        if addr["id"] != sender_id:
            name = addr.get("shortName") or addr.get("name", "-")
            city = addr.get("cityName", "")
            label = f"{name[:30]} - {city}"
            buttons.append([InlineKeyboardButton(label, callback_data=f"ship_recipient_{addr['id']}")])

    if not buttons:
        await query.edit_message_text(
            "Alıcı adresi bulunmuyor. Önce bir alıcı adresi ekleyin.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Ana Menü", callback_data="menu_main")]
            ]),
        )
        context.user_data.pop("state", None)
        return

    await query.edit_message_text(
        "Alıcı adresini seçin:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def ship_recipient_select(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    recipient_id = query.data.replace("ship_recipient_", "")
    context.user_data["new_ship"]["recipientAddressId"] = recipient_id
    context.user_data["state"] = "ship_length"

    await query.edit_message_text("Paket boyunu (cm) girin:")


async def ship_length(update: Update, context: CallbackContext):
    try:
        val = float(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Geçersiz değer. Boy (cm) girin:")
        return
    context.user_data["new_ship"]["length"] = val
    context.user_data["state"] = "ship_width"
    await update.message.reply_text("Paket enini (cm) girin:")


async def ship_width(update: Update, context: CallbackContext):
    try:
        val = float(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Geçersiz değer. En (cm) girin:")
        return
    context.user_data["new_ship"]["width"] = val
    context.user_data["state"] = "ship_height"
    await update.message.reply_text("Paket yüksekliğini (cm) girin:")


async def ship_height(update: Update, context: CallbackContext):
    try:
        val = float(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Geçersiz değer. Yükseklik (cm) girin:")
        return
    context.user_data["new_ship"]["height"] = val
    context.user_data["state"] = "ship_weight"
    await update.message.reply_text("Paket ağırlığını (kg) girin:")


async def ship_weight(update: Update, context: CallbackContext):
    try:
        val = float(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Geçersiz değer. Ağırlık (kg) girin:")
        return

    ship = context.user_data["new_ship"]
    ship["weight"] = val
    context.user_data["state"] = "ship_offer"

    await update.message.reply_text("⏳ Fiyat teklifleri alınıyor...")

    try:
        price_result = await api.get_prices(ship["length"], ship["width"], ship["height"], val)
    except Exception as e:
        context.user_data.pop("state", None)
        await update.message.reply_text(f"Fiyat sorgulama hatası: {e}", reply_markup=main_menu_keyboard())
        return

    if not price_result.get("result"):
        context.user_data.pop("state", None)
        await update.message.reply_text("Fiyat teklifi alınamadı.", reply_markup=main_menu_keyboard())
        return

    price_list = price_result.get("priceList", [])
    if not price_list or not price_list[0].get("offers"):
        context.user_data.pop("state", None)
        await update.message.reply_text("Bu ölçülere uygun teklif bulunamadı.", reply_markup=main_menu_keyboard())
        return

    offers = price_list[0]["offers"]
    desi = price_list[0].get("desi", "-")

    by_provider = {}
    for offer in offers:
        provider = offer["providerCode"]
        transport = offer.get("transportType", "")
        total = offer.get("totalAmount", "0")
        currency = offer.get("currency", "TL")
        service_code = offer.get("providerServiceCode", "")
        if provider not in by_provider:
            by_provider[provider] = {}
        if transport not in by_provider[provider]:
            by_provider[provider][transport] = (total, currency, service_code)

    result = []
    for provider, types in by_provider.items():
        unique_prices = set(v[0] for v in types.values())
        if len(unique_prices) == 1:
            total, currency, service_code = list(types.values())[0]
            transport_label = "Şehir İçi - Dışı" if len(types) > 1 else list(types.keys())[0]
            result.append((float(total), total, currency, provider, transport_label, service_code))
        else:
            for transport, (total, currency, service_code) in types.items():
                result.append((float(total), total, currency, provider, transport, service_code))

    result.sort(key=lambda x: x[0])
    context.user_data["_ship_offers"] = result

    buttons = []
    for i, (_, total, currency, provider, transport, _) in enumerate(result):
        label = f"{provider} - {total} {currency} ({transport})"
        buttons.append([InlineKeyboardButton(label, callback_data=f"ship_offer_{i}")])

    buttons.append([InlineKeyboardButton("🔙 Ana Menü", callback_data="menu_main")])

    await update.message.reply_text(
        f"📦 Teklifler (Desi: {desi}):",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def ship_offer_select(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    idx = int(query.data.replace("ship_offer_", ""))
    offers = context.user_data.get("_ship_offers", [])
    context.user_data.pop("state", None)

    if idx >= len(offers):
        await query.edit_message_text("Geçersiz teklif.", reply_markup=main_menu_keyboard())
        return

    offer_data = offers[idx]
    service_code = offer_data[5]
    ship = context.user_data.get("new_ship", {})

    await query.edit_message_text("⏳ Gönderi satın alınıyor...")

    payload = {
        "senderAddressID": ship["senderAddressId"],
        "recipientAddressID": ship["recipientAddressId"],
        "length": str(int(ship["length"])),
        "width": str(int(ship["width"])),
        "height": str(int(ship["height"])),
        "distanceUnit": "cm",
        "weight": str(int(ship["weight"])),
        "massUnit": "kg",
        "items": [{"title": "Urun", "quantity": 1}],
        "productPaymentOnDelivery": False,
        "order": {
            "sourceCode": "API",
            "sourceIdentifier": "telegram",
            "orderNumber": f"TG-{update.effective_user.id}",
            "totalAmount": int(float(offer_data[1])),
            "totalAmountCurrency": offer_data[2],
        },
    }

    try:
        result = await api.purchase_shipment(service_code, payload)
    except Exception as e:
        print(f"purchase_shipment ERROR: {e}")
        await query.edit_message_text(f"Satın alma hatası: {e}", reply_markup=main_menu_keyboard())
        return

    if not result.get("result"):
        err = result.get("additionalMessage") or result.get("message") or str(result)
        await query.edit_message_text(
            f"❌ Satın alma başarısız: {err}", reply_markup=main_menu_keyboard(),
        )
        return

    txn_data = result.get("data", {})
    shipment = txn_data.get("shipment", {})
    barcode = shipment.get("barcode") or "-"
    label_url = shipment.get("labelURL", "")
    tracking_url = shipment.get("trackingUrl", "")
    tracking_no = shipment.get("trackingNumber") or "-"

    msg = (
        f"✅ Gönderi Başarıyla Oluşturuldu!\n\n"
        f"Barkod: {barcode}\n"
        f"Takip No: {tracking_no}\n"
        f"Firma: {offer_data[3]}\n"
        f"Tutar: {offer_data[1]} {offer_data[2]}\n"
    )
    buttons = [[InlineKeyboardButton("🔙 Ana Menü", callback_data="menu_main")]]
    if label_url:
        buttons.insert(0, [InlineKeyboardButton("🏷 Etiketi Görüntüle", url=label_url)])
    if tracking_url:
        buttons.insert(0, [InlineKeyboardButton("🔍 Takip Et", url=tracking_url)])

    await query.edit_message_text(
        msg, reply_markup=InlineKeyboardMarkup(buttons),
    )
