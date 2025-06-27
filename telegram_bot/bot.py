from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import os

user_data = {}

BOT_TOKEN = os.getenv("BOT_TOKEN") or "YOUR_BOT_TOKEN"
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID") or 123456789)
WEBHOOK_URL = os.getenv("WEBHOOK_URL") or "https://your-app.onrender.com"

# Стартовая команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Посчитать стоимость", callback_data="start_calc")]]
    await update.message.reply_text(
        "⚠️ Добро пожаловать в сервис руссификации и перепрошивки мультимедийных систем FORD.\n\n"
        "Ответьте на несколько вопросов — и получите стоимость услуги и возможность оставить заявку.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Обработка нажатия кнопки "Посчитать стоимость"
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data[user_id] = {"step": "year"}
    await query.edit_message_text("Введите год выпуска автомобиля (например, 2019):")

# Обработка всех текстовых сообщений по шагам
async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    session = user_data.get(user_id)

    if not session or "step" not in session:
        await update.message.reply_text("Пожалуйста, начните с команды /start.")
        return

    step = session["step"]

    if step == "year":
        if not text.isdigit() or not (2000 <= int(text) <= 2025):
            await update.message.reply_text("⛔ Пожалуйста, введите корректный год от 2000 до 2025.")
            return
        session["year"] = text
        session["step"] = "model"
        await update.message.reply_text("✅ Год принят!\nТеперь введите модель автомобиля (например, Focus, Kuga):")

    elif step == "model":
        if len(text) < 2:
            await update.message.reply_text("⛔ Пожалуйста, введите корректную модель.")
            return
        session["model"] = text
        session["step"] = "nav"
        keyboard = [
            [InlineKeyboardButton("✅ Есть", callback_data="nav_yes")],
            [InlineKeyboardButton("❌ Нет", callback_data="nav_no")],
            [InlineKeyboardButton("❓ Не знаю", callback_data="nav_unknown")]
        ]
        await update.message.reply_text(
            "Есть ли в мультимедии автомобиля встроенная навигация?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif step == "phone":
        if len(text) < 6:
            await update.message.reply_text("Пожалуйста, введите корректный номер телефона.")
            return
        session["phone"] = text

        msg = (
            f"📥 Новая заявка:\n"
            f"• Год: {session['year']}\n"
            f"• Модель: {session['model']}\n"
            f"• Навигация: {session['nav']}\n"
            f"• Цена: 100.00 BYN\n"
            f"• Телефон: {session['phone']}"
        )

        keyboard = [[InlineKeyboardButton("📞 Связаться со мной", callback_data="notify_me")]]
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

# Обработка выбора навигации
async def handle_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    nav = query.data.replace("nav_", "")
    session = user_data.get(user_id)

    if not session:
        await query.edit_message_text("Сессия устарела. Пожалуйста, начните с /start.")
        return

    session["nav"] = nav
    session["step"] = "phone"

    await query.edit_message_text(
        "✅ Услуга рассчитана.\n💰 Стоимость: 100.00 BYN\n\nПожалуйста, введите номер телефона для связи:"
    )

# Обработка заявки
async def handle_notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    summary = user_data.get(user_id, {})

    if summary:
        text = (
            f"📬 Заявка от пользователя:\n"
            f"• Год: {summary['year']}\n"
            f"• Модель: {summary['model']}\n"
            f"• Навигация: {summary['nav']}\n"
            f"• Телефон: {summary['phone']}"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)
        await query.edit_message_text("✅ Спасибо! Мы свяжемся с вами в ближайшее время.")
        user_data.pop(user_id, None)
    else:
        await query.edit_message_text("⛔ Данных нет. Пожалуйста, начните с /start.")

# Запуск бота через Webhook
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback, pattern="^start_calc$"))
    app.add_handler(CallbackQueryHandler(handle_navigation, pattern="^nav_"))
    app.add_handler(CallbackQueryHandler(handle_notify, pattern="^notify_me$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        webhook_url=f"{WEBHOOK_URL}/webhook"
    )