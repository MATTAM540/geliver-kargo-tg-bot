from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from bot.auth import restricted
from bot.api_client import api
from bot.keyboards import main_menu_keyboard

PAGE_SIZE = 11

# ── Liste ──

@restricted
async def address_list(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("addr_page_"):
        page = int(data.replace("addr_page_", ""))
    else:
        page = 1

    try:
        result = await api.get_addresses(page=page, limit=PAGE_SIZE)
    except Exception:
        await query.edit_message_text("API bağlantı hatası.", reply_markup=main_menu_keyboard())
        return

    if not result.get("result"):
        await query.edit_message_text("Adresler alınamadı.", reply_markup=main_menu_keyboard())
        return

    addresses = result.get("data", [])
    has_more = len(addresses) == PAGE_SIZE

    buttons = []
    for addr in addresses:
        sender = "📤" if addr.get("isDefaultSenderAddress") else ""
        rec = "📥" if addr.get("isRecipientAddress") else ""
        icon = sender or rec or "📍"
        name = addr.get("shortName") or addr.get("name", "-")
        city = addr.get("cityName", "")
        label = f"{icon} {name[:25]} - {city}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"addr_view_{addr['id']}")])

    if has_more or page > 1:
        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("◀️ Önceki", callback_data=f"addr_page_{page - 1}"))
        if has_more:
            nav_buttons.append(InlineKeyboardButton("Sonraki ▶️", callback_data=f"addr_page_{page + 1}"))
        buttons.append(nav_buttons)

    buttons.append([InlineKeyboardButton("➕ Yeni Adres Ekle", callback_data="addr_add_start")])
    buttons.append([InlineKeyboardButton("🔙 Ana Menü", callback_data="menu_main")])

    if not addresses and page == 1:
        text = "Kayıtlı adres bulunmuyor.\n\nYeni adres eklemek için butona tıklayın."
    elif not addresses:
        text = f"📍 Adresleriniz (Sayfa {page}):\n\nBu sayfada adres bulunmuyor."
    elif has_more or page > 1:
        text = f"📍 Adresleriniz (Sayfa {page}):"
    else:
        text = "📍 Adresleriniz:"

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))


# ── Detay ──

@restricted
async def address_view(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    address_id = query.data.replace("addr_view_", "")

    try:
        result = await api.get_address(address_id)
    except Exception:
        await query.edit_message_text("API bağlantı hatası.", reply_markup=main_menu_keyboard())
        return

    if not result.get("result"):
        addr = None
    else:
        addr = result.get("data")

    if not addr:
        await query.edit_message_text(
            "Adres bulunamadı.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Adresler", callback_data="menu_addresses")]
            ]),
        )
        return

    sender = "Gönderici" if addr.get("isDefaultSenderAddress") else ""
    rec = "Alıcı" if addr.get("isRecipientAddress") else ""
    type_label = sender or rec or "Genel"

    msg = (
        f"📍 Adres Detayı\n\n"
        f"İsim: {addr.get('name', '-')}\n"
        f"Kısa Ad: {addr.get('shortName', '-')}\n"
        f"Telefon: {addr.get('phone', '-')}\n"
        f"E-posta: {addr.get('email', '-')}\n"
        f"Adres: {addr.get('address1', '')}\n"
        f"Şehir: {addr.get('cityName', '')} / {addr.get('districtName', '')}\n"
        f"Posta Kodu: {addr.get('zip', '-')}\n"
        f"Tür: {type_label}\n"
        f"ID: {addr.get('id', '')}"
    )

    await query.edit_message_text(
        msg,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🗑 Sil", callback_data=f"addr_del_{address_id}")],
            [InlineKeyboardButton("🔙 Adresler", callback_data="menu_addresses")],
            [InlineKeyboardButton("🔙 Ana Menü", callback_data="menu_main")],
        ]),
    )


# ── Silme ──

@restricted
async def address_delete(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    address_id = query.data.replace("addr_del_", "")

    try:
        result = await api.delete_address(address_id)
    except Exception:
        await query.edit_message_text("API bağlantı hatası.", reply_markup=main_menu_keyboard())
        return

    if result.get("result"):
        await query.edit_message_text(
            "✅ Adres başarıyla silindi.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📍 Adresler", callback_data="menu_addresses")],
                [InlineKeyboardButton("🔙 Ana Menü", callback_data="menu_main")],
            ]),
        )
    else:
        err = result.get("additionalMessage") or result.get("message") or "Bilinmeyen hata"
        await query.edit_message_text(
            f"❌ Silinemedi: {err}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Adresler", callback_data="menu_addresses")]
            ]),
        )


# ── Ekleme (state machine) ──

@restricted
async def address_add_start(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    context.user_data["addr_new"] = {}
    context.user_data["state"] = "addr_type"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 Gönderici", callback_data="addr_type_sender"),
         InlineKeyboardButton("📥 Alıcı", callback_data="addr_type_recipient")],
        [InlineKeyboardButton("🔙 Adresler", callback_data="menu_addresses")],
    ])
    await query.edit_message_text("Yeni adres ekleme\n\nAdres türünü seçin:", reply_markup=keyboard)


async def address_type_select(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    addr_type = query.data.replace("addr_type_", "")
    context.user_data["addr_new"]["type"] = addr_type
    context.user_data["state"] = "addr_name"

    await query.edit_message_text(
        f"Ad Soyad / Şirket Adı girin:\n(Tür: {'Gönderici' if addr_type == 'sender' else 'Alıcı'})",
    )


async def address_name(update: Update, context: CallbackContext):
    context.user_data["addr_new"]["name"] = update.message.text.strip()
    context.user_data["state"] = "addr_phone"
    await update.message.reply_text("Telefon numarası girin (örn: +905xxxxxxxxx):")


async def address_phone(update: Update, context: CallbackContext):
    context.user_data["addr_new"]["phone"] = update.message.text.strip()
    context.user_data["state"] = "addr_shortname"
    await update.message.reply_text("Kısa ad girin (listede görünecek isim):")


async def address_shortname(update: Update, context: CallbackContext):
    context.user_data["addr_new"]["shortName"] = update.message.text.strip()
    context.user_data["state"] = "addr_email"
    await update.message.reply_text("E-posta adresi girin (opsiyonel, boş bırakmak için - yazın):")


async def address_email(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    context.user_data["addr_new"]["email"] = "" if text == "-" else text
    context.user_data["state"] = "addr_line1"
    await update.message.reply_text("Açık adres girin (mahalle, cadde, sokak, no):")


async def address_line1(update: Update, context: CallbackContext):
    context.user_data["addr_new"]["address1"] = update.message.text.strip()
    context.user_data["state"] = "addr_city"

    try:
        result = await api.get_cities()
    except Exception:
        context.user_data.pop("state", None)
        await update.message.reply_text("Şehir listesi alınamadı. İptal edildi.", reply_markup=main_menu_keyboard())
        return

    cities = result.get("data", [])
    context.user_data["_cities"] = cities

    tr_cities = [c for c in cities if c.get("countryCode") == "TR"]
    buttons = []
    for c in tr_cities[:90]:
        buttons.append([InlineKeyboardButton(f"{c['name']}", callback_data=f"addr_city_{c['cityCode']}")])

    await update.message.reply_text(
        "Şehir seçin:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def address_city(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    city_code = query.data.replace("addr_city_", "")
    context.user_data["addr_new"]["cityCode"] = city_code
    context.user_data["state"] = "addr_district"

    try:
        result = await api.get_districts(city_code)
    except Exception:
        context.user_data.pop("state", None)
        await query.edit_message_text("İlçe listesi alınamadı.", reply_markup=main_menu_keyboard())
        return

    districts = result.get("data", [])
    context.user_data["_districts"] = districts

    tr_districts = [d for d in districts if d.get("countryCode") == "TR"]
    if not tr_districts:
        tr_districts = districts

    buttons = []
    for d in tr_districts[:90]:
        buttons.append([InlineKeyboardButton(d["name"], callback_data=f"addr_dist_{d['districtID']}")])

    await query.edit_message_text(
        "İlçe seçin:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def address_district(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    district_id = query.data.replace("addr_dist_", "")
    context.user_data["addr_new"]["districtID"] = int(district_id)
    context.user_data["state"] = "addr_zip"

    await query.edit_message_text("Posta kodu girin:")


async def address_zip(update: Update, context: CallbackContext):
    context.user_data["addr_new"]["zip"] = update.message.text.strip()
    addr = context.user_data["addr_new"]
    context.user_data.pop("state", None)

    is_sender = addr.get("type") == "sender"
    payload = {
        "name": addr["name"],
        "phone": addr["phone"],
        "shortName": addr["shortName"],
        "email": addr.get("email", ""),
        "address1": addr["address1"],
        "cityCode": addr["cityCode"],
        "districtID": addr["districtID"],
        "zip": addr["zip"],
        "countryCode": "TR",
        "isDefaultSenderAddress": is_sender,
        "isDefaultReturnAddress": is_sender,
        "isRecipientAddress": not is_sender,
    }

    try:
        result = await api.create_address(payload)
    except Exception:
        await update.message.reply_text("Adres oluşturulurken API hatası.", reply_markup=main_menu_keyboard())
        return

    if result.get("result"):
        addr_id = result.get("data", {}).get("id", "")
        await update.message.reply_text(
            f"✅ Adres başarıyla oluşturuldu!\nID: {addr_id}",
            reply_markup=main_menu_keyboard(),
        )
    else:
        err = result.get("additionalMessage") or result.get("message") or "Bilinmeyen hata"
        await update.message.reply_text(
            f"❌ Adres oluşturulamadı: {err}",
            reply_markup=main_menu_keyboard(),
        )
