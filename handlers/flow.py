from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from utils.data import user_data
from utils.sheets import append_row_to_sheet

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    if user_id not in user_data or user_data[user_id]["step"] == "model":
        return

    step = user_data[user_id]["step"]

    if step == "year":
        user_data[user_id]["year"] = text
        user_data[user_id]["step"] = "nav"
        markup = ReplyKeyboardMarkup([["С навигацией", "Без навигации"]], one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Есть ли навигация?", reply_markup=markup)

    elif step == "nav":
        user_data[user_id]["nav"] = text
        user_data[user_id]["step"] = "phone"
        await update.message.reply_text("Введите номер телефона:", reply_markup=ReplyKeyboardRemove())

    elif step == "phone":
        user_data[user_id]["phone"] = text
        user_data[user_id]["step"] = "done"

        info = user_data[user_id]
        row = [info.get("brand"), info.get("model"), info.get("year"), info.get("nav"), info.get("phone")]
        append_row_to_sheet(row)  # ✅ сохраняем в таблицу

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