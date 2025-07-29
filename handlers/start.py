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


async def start_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    # Здесь можно использовать любую структуру для отслеживания состояния
    keyboard = [
        [InlineKeyboardButton("Ford", callback_data="brand_ford")],
        [InlineKeyboardButton("Lincoln", callback_data="brand_lincoln")]
    ]
    await query.edit_message_text("Выберите марку автомобиля:", reply_markup=InlineKeyboardMarkup(keyboard))