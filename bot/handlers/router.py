from telegram import Update
from telegram.ext import CallbackContext

from bot.handlers.price import (
    price_length, price_width, price_height, price_weight,
)
from bot.handlers.addresses import (
    address_name, address_phone, address_shortname, address_email,
    address_line1, address_zip,
)
from bot.handlers.shipments import (
    ship_length, ship_width, ship_height, ship_weight,
)
from bot.handlers.webhooks import (
    webhook_url, webhook_header_name, webhook_header_value,
)

STATE_HANDLERS = {
    "price_length": price_length,
    "price_width": price_width,
    "price_height": price_height,
    "price_weight": price_weight,
    "addr_name": address_name,
    "addr_phone": address_phone,
    "addr_shortname": address_shortname,
    "addr_email": address_email,
    "addr_line1": address_line1,
    "addr_zip": address_zip,
    "ship_length": ship_length,
    "ship_width": ship_width,
    "ship_height": ship_height,
    "ship_weight": ship_weight,
    "wh_url": webhook_url,
    "wh_header_name": webhook_header_name,
    "wh_header_value": webhook_header_value,
}


async def state_message_handler(update: Update, context: CallbackContext):
    state = context.user_data.get("state")
    if state and state in STATE_HANDLERS:
        await STATE_HANDLERS[state](update, context)
