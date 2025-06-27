import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Конфигурация
BOT_TOKEN = os.getenv("BOT_TOKEN") or "YOUR_BOT_TOKEN"
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID") or 123456789)
WEBHOOK_URL = "https://chatbot-lead-generator.onrender.com"

user_data = {}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Посчитать стоимость", callback_data="start_calc")]]
    await update.message.reply_text(
        "⚠️ Добро пожаловать в сервис перепрошивки мультимедийных систем FORD.\n\n" \
        "мы работаем только в городе Минск\n\n"
        "Чтобы увидеть стоимость услуги, ответьте на несколько вопросов, после чего Вы сможете оставить заявку.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Старт опроса
async def start_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data[user_id] = {"step": "year"}
    await query.edit_message_text("Введите год выпуска автомобиля (например, 2019):")

# Обработка навигации
async def handle_nav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    nav = query.data.replace("nav_", "")
    session = user_data.get(user_id, {})
    session["nav"] = nav
    session["step"] = "phone"
    await query.edit_message_text("✅ Услуга рассчитана.\n💰 Стоимость: 100.00 BYN\n Если хотите оставить заявку\nВведите номер телефона с кодом оператора:")

# Финальный шаг
from datetime import datetime

async def handle_notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = query.from_user
    session = user_data.get(user_id)

    if session:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        first_name = user.first_name or "—"
        username = f"@{user.username}" if user.username else "—"

        msg = (
            f"📬 Заявка от пользователя:\n"
            f"• Имя: {first_name}\n"
            f"• Username: {username}\n"
            f"• Telegram ID: {user_id}\n"
            f"• Время заявки: {timestamp}\n\n"
            f"• Год: {session['year']}\n"
            f"• Модель: {session['model']}\n"
            f"• Навигация: {session['nav']}\n"
            f"• Телефон: {session['phone']}"
        )

        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)
        await query.edit_message_text("✅ Спасибо! Ваша заявка принята! Мы свяжемся с вами в ближайшее время.")
        user_data.pop(user_id, None)
    else:
        await query.edit_message_text("⛔ Данные не найдены. Начните с /start.")
# Обработка текста по шагам
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    session = user_data.get(user_id)

    if not session:
        await update.message.reply_text("Пожалуйста, начните с команды /start.")
        return

    step = session.get("step")

    if step == "year":
        if not text.isdigit() or not (2000 <= int(text) <= 2025):
            await update.message.reply_text("⛔ Введите корректный год от 2000 до 2025.")
            return
        session["year"] = text
        session["step"] = "model"
        await update.message.reply_text("✅ Год принят. Укажите модель автомобиля (например, Focus, Kuga):")

    elif step == "model":
        if len(text) < 2:
            await update.message.reply_text("⛔ Введите корректную модель.")
            return
        session["model"] = text
        session["step"] = "nav"
        keyboard = [
            [InlineKeyboardButton("✅ Есть", callback_data="nav_yes")],
            [InlineKeyboardButton("❌ Нет", callback_data="nav_no")],
            [InlineKeyboardButton("❓ Не знаю", callback_data="nav_unknown")]
        ]
        await update.message.reply_text("Есть ли встроенная навигация?", reply_markup=InlineKeyboardMarkup(keyboard))

    elif step == "phone":
        if len(text) < 6:
            await update.message.reply_text("⛔ Введите корректный номер телефона.")
            return
        session["phone"] = text
        keyboard = [[InlineKeyboardButton("📞Отправить заявку", callback_data="notify_me")]]
        msg = (
            f"📥 Новая заявка:\n"
            f"• Год: {session['year']}\n"
            f"• Модель: {session['model']}\n"
            f"• Навигация: {session['nav']}\n"
            f"• Цена: 100.00 BYN\n"
            f"• Телефон: {session['phone']}"
        )
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

# Основной запуск
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(start_calc, pattern="^start_calc$"))
    app.add_handler(CallbackQueryHandler(handle_nav, pattern="^nav_"))
    app.add_handler(CallbackQueryHandler(handle_notify, pattern="^notify_me$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    await app.initialize()
    await app.start()
    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", "8080")),
        url_path="/webhook",
        webhook_url=f"{WEBHOOK_URL}/webhook"
    )
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())