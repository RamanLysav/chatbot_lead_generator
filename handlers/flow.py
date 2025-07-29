from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from handlers.states import NAV, PHONE, DONE
from utils.data import user_data
from utils.sheets import append_row_to_sheet

async def year_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    try:
        year = int(text)
        user_data[user_id]["year"] = year
        markup = ReplyKeyboardMarkup([["С навигацией", "Без навигации"]],
                                     one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Есть ли навигация?", reply_markup=markup)
        return NAV
    except ValueError:
        await update.message.reply_text("Введите год цифрами, например: 2017")
        return YEAR

async def nav_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id]["nav"] = update.message.text.strip()
    await update.message.reply_text("Введите номер телефона:", reply_markup=ReplyKeyboardRemove())
    return PHONE

async def phone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id]["phone"] = update.message.text.strip()

    info = user_data[user_id]
    row = [info.get("brand"), info.get("model"), info.get("year"), info.get("nav"), info.get("phone")]
    append_row_to_sheet(row)

    summary = (
        f"📋 Ваша заявка:\n"
        f"Марка: {info.get('brand')}\n"
        f"Модель: {info.get('model')}\n"
        f"Год: {info.get('year')}\n"
        f"Навигация: {info.get('nav')}\n"
        f"Телефон: {info.get('phone')}"
    )

    await update.message.reply_text(summary)
    await update.message.reply_text("✅ Спасибо! Ваша заявка отправлена.")
    return DONE