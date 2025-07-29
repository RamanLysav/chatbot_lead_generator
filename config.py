import os
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "123456789"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = 8443
# Google Sheets
SHEET_NAME = os.getenv("SHEET_NAME", "Заявки FORD")
CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_JSON", "/etc/secrets/credentials.json")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1