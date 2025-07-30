from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from data.session import user_data

async def start_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data[user_id] = {"step": "model"}

    models = [["EcoSport", "Fusion", "Escape"], ["Bronco Sport", "Edge", "F-150"], ["Mustang", "Другая модель"]]
    markup = ReplyKeyboardMarkup(models, one_time_keyboard=True, resize_keyboard=True)

    await query.edit_message_text("Выберите модель автомобиля:")
    await context.bot.send_message(chat_id=user_id, text="👇 Выберите из списка или нажмите 'Другая модель':", reply_markup=markup)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    session = user_data.get(user_id)

    if not session:
        await update.message.reply_text("Пожалуйста, начните с команды /start.")
        return

    step = session.get("step")

    if step == "model":
        if text == "Другая модель":
            await update.message.reply_text("Введите модель вручную:", reply_markup=ReplyKeyboardRemove())
            return
        session["model"] = text
        session["step"] = "year"
        years = [str(y) for y in range(2025, 2014, -1)]
        keyboard = [years[i:i+3] for i in range(0, len(years), 3)] + [["Другой год"]]
        markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("✅ Модель принята.\nТеперь выберите год:", reply_markup=markup)

    elif step == "year":
        if text == "Другой год":
            await update.message.reply_text("Введите год вручную:", reply_markup=ReplyKeyboardRemove())
            return
        if not text.isdigit() or not (2010 <= int(text) <= 2025):
            await update.message.reply_text("⛔ Введите