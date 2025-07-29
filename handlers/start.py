from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from utils.data import user_data

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🚗 Приступить", callback_data="start_calc")]]
    await update.message.reply_text("Добро пожаловать! 🚀", reply_markup=InlineKeyboardMarkup(keyboard))

async def start_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data[user_id] = {"step": "brand"}
    keyboard = [
        [InlineKeyboardButton("Ford", callback_data="brand_ford")],
        [InlineKeyboardButton("Lincoln", callback_data="brand_lincoln")]
    ]
    await query.edit_message_text("Выберите марку автомобиля:", reply_markup=InlineKeyboardMarkup(keyboard))