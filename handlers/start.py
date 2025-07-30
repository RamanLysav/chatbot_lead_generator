from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚗 Приступить", callback_data="start_calc")],
        [InlineKeyboardButton("ℹ️ Подробнее об услуге", callback_data="show_info")]
    ]
    await update.message.reply_text("⚠️ Здравствуйте! Мы занимаемся...", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("⬅️ Вернуться назад", callback_data="go_back")]]
    await query.edit_message_text("ℹ️ Подробнее об услуге...", reply_markup=InlineKeyboardMarkup(keyboard))

async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🚗 Приступить", callback_data="start_calc")],
        [InlineKeyboardButton("ℹ️ Подробнее об услуге", callback_data="show_info")]
    ]
    await query.edit_message_text("⚠️ Добро пожаловать обратно!", reply_markup=InlineKeyboardMarkup(keyboard))