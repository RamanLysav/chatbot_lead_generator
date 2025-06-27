import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))
#WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_URL = "https://chatbot-lead-generator.onrender.com"

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Посчитать стоимость", callback_data="start_calc")]]
    await update.message.reply_text(
        "⚠️ Добро пожаловать в сервис руссификации и перепрошивки мультимедийных систем FORD.\n\n"
        "Ответьте на несколько вопросов — и получите стоимость услуги и возможность оставить заявку.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def start_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data[user_id] = {"step": "year"}
    await query.edit_message_text("Введите год выпуска автомобиля (например, 2019):")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    session = user_data.get(user_id)

    if not session or "step" not in session:
        await update.message.reply_text("Пожалуйста, начните сначала с команды /start.")
        return

    step = session["step"]

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
        await update.message.reply_text("Есть ли в мультимедии автомобиля встроенная навигация?", reply_markup=InlineKeyboardMarkup(keyboard))

    elif step == "phone":
        if len(text) < 6:
            await update.message.reply_text("⛔ Введите корректный номер телефона.")
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

async def handle_nav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    nav_choice = query.data.replace("nav_", "")
    session = user_data.get(user_id)

    if not session:
        await query.edit_message_text("⛔ Сессия устарела. Начните с /start.")
        return

    session["nav"] = nav_choice
    session["step"] = "phone"
    await query.edit_message_text("✅ Услуга рассчитана.\n💰 Стоимость: 100.00 BYN\n\nПожалуйста, введите номер телефона:")

async def handle_notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    session = user_data.get(user_id)

    if session:
        msg = (
            f"📬 Заявка от пользователя:\n"
            f"• Год: {session['year']}\n"
            f"• Модель: {session['model']}\n"
            f"• Навигация: {session['nav']}\n"
            f"• Телефон: {session['phone']}"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)
        await query.edit_message_text("✅ Спасибо! Мы свяжемся с вами в ближайшее время.")
        user_data.pop(user_id, None)
    else:
        await query.edit_message_text("⛔ Данных не найдено. Попробуйте снова с /start.")

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
        webhook_url=f"{WEBHOOK_URL}/webhook"  # ← вот это было важно!
    )

    await app.updater.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())