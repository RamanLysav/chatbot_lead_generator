from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from utils.data import user_data

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    if user_id not in user_data or user_data[user_id]["step"] != "model":
        return

    user_data[user_id]["model"] = text
    user_data[user_id]["step"] = "year"
    await update.message.reply_text("Введите год выпуска:", reply_markup=ReplyKeyboardRemove())