from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from handlers.states import YEAR
from utils.data import user_data

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    user_data[user_id]["model"] = text
    await update.message.reply_text("Введите год выпуска:", reply_markup=ReplyKeyboardRemove())
    return YEAR