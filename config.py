import os
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN") or "YOUR_BOT_TOKEN"
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID") or 123456789)
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name("/etc/secrets/credentials.json", SCOPE)
CLIENT = gspread.authorize(CREDS)
SHEET = CLIENT.open("Заявки FORD").sheet1