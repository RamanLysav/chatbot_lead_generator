from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🚗 Приступить", callback_data="start_calc")]]
    markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Добро пожаловать! 🚀", reply_markup=markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("Добро пожаловать! 🚀", reply_markup=markup)
    elif update.effective_chat:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Добро пожаловать! 🚀", reply_markup=markup)
    else:
        print("⛔️ Неизвестный тип update:", update)