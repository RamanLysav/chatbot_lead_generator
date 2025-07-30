from datetime import datetime
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from config import ADMIN_CHAT_ID, sheet
from data.session import user_data

async def handle_nav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    nav = query.data.replace("nav_", "")
    session = user_data.get(user_id, {})
    session.update({
        "nav": nav,
        "step": "phone",
        "reached_price": True,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "first_name": update.effective_user.first_name or "—",
        "username": f"@{update.effective_user.username}" if update.effective_user.username else "—",
    })

    session["price"] = 130 if nav == "yes" else 100

    async def check_abandoned(user_id, context):
        await asyncio.sleep(300)
        s = user_data.get(user_id)
        if s and s.get("reached_price") and s.get("step") == "phone":
            msg = (
                f"⚠️ Пользователь не завершил заявку:\n"
                f"• Имя: {s['first_name']}\n"
                f"• Username: {s['username']}\n"
                f"• Telegram ID: {user_id}\n"
                f"• Модель: {s['model']}\n"
                f"• Год: {s['year']}\n"
                f"• Навигация: {s['nav']}\n"
                f"• Цена: {s['price']:.2f} BYN\n"
                f"• Время: {s['timestamp']}"
            )
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)

    context.application.create_task(check_abandoned(user_id, context))

    markup = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Отправить номер", request_contact=True)]],
        one_time_keyboard=True, resize_keyboard=True
    )
    await query.edit_message_text(
        f"✅ Стоимость услуги рассчитана.\n💰 {session['price']:.2f} BYN\n\n"
        "Пожалуйста, отправьте номер телефона кнопкой ниже или введите вручную:",
    )
    await context.bot.send_message(chat_id=user_id, text="👇 Отправьте номер телефона:", reply_markup=markup)

async def handle_notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    session = user_data.get(user_id)
    if not session:
        await query.edit_message_text("⛔ Данные не найдены. Начните с /start.")
        return

    session["reached_price"] = False
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Отправка админу
    msg = (
        f"📬 Заявка:\n"
        f"• Имя: {session['first_name']}\n"
        f"• Username: {session['username']}\n"
        f"• Telegram ID: {user_id}\n"
        f"• Модель: {session['model']}\n"
        f"• Год: {session['year']}\n"
        f"• Навигация: {session['nav']}\n"
        f"• Телефон: {session['phone']}\n"
        f"• Цена: {session['price']:.2f} BYN\n"
        f"• Время: {timestamp}"
    )
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)

    # В таблицу
    sheet.append_row([
        timestamp, session['first_name'], session['username'], str(user_id),
        session["model"], session["year"], session["nav"], session["phone"], f"{session['price']:.2f}"
    ])

    await query.edit_message_text(
        "✅ Спасибо! Ваша заявка принята.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Начать заново", callback_data="start_calc")]])
    )
    user_data.pop(user_id, None)