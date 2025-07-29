from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from utils.data import user_data

async def choose_brand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    brand = query.data.replace("brand_", "")
    user_data[user_id]["brand"] = brand
    user_data[user_id]["step"] = "model"

    if brand == "ford":
        models = [["EcoSport", "Fusion", "Escape"], ["Bronco Sport", "Edge", "F-150"], ["Mustang", "Другая модель"]]
    else:
        models = [["Corsair", "Navigator"], ["Другая модель"]]

    markup = ReplyKeyboardMarkup(models, one_time_keyboard=True, resize_keyboard=True)
    await query.edit_message_text(f"Вы выбрали: {brand.title()}")
    await context.bot.send_message(chat_id=user_id, text="👇 Теперь выберите модель:", reply_markup=markup)