import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GELIVER_API_TOKEN = os.getenv("GELIVER_API_TOKEN")
GELIVER_ORGANIZATION_ID = os.getenv("GELIVER_ORGANIZATION_ID", "")
ALLOWED_USER_IDS = set(
    int(uid.strip())
    for uid in os.getenv("ALLOWED_USER_IDS", "").split(",")
    if uid.strip()
)

GELIVER_BASE_URL = "https://api.geliver.io/api/v1"
