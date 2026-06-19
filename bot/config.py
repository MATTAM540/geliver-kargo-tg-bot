import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GELIVER_API_TOKEN = os.getenv("GELIVER_API_TOKEN")
GELIVER_ORGANIZATION_ID = os.getenv("GELIVER_ORGANIZATION_ID", "")
_allowed_ids_raw = os.getenv("ALLOWED_USER_IDS", "")
if _allowed_ids_raw.strip():
    ALLOWED_USER_IDS = set(
        int(uid.strip())
        for uid in _allowed_ids_raw.split(",")
        if uid.strip()
    )
else:
    ALLOWED_USER_IDS = None

GELIVER_BASE_URL = "https://api.geliver.io/api/v1"
