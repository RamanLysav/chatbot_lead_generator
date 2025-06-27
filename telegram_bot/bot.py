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
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID") or 123456789)  # замените на свой ID

# Старт: кнопка для запуска
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Посчитать стоимость", callback_data="start_calc")]]
    await update.message.reply_text(
        "⚠️ Добро пожаловать в сервис руссификации и перепрошивки мультимедийных систем FORD.\n\n"
        "Ответьте на несколько вопросов — и получите стоимость услуги и возможность оставить заявку.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Шаг 1: ввод года
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    user_data[user_id] = {}
    await query.edit_message_text("Введите год выпуска автомобиля (например, 2019):")

# Шаг 2: ввод модели авто
async def handle_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if not text.isdigit() or not (2000 <= int(text) <= 2025):
        await update.message.reply_text("Пожалуйста, введите корректный год от 2000 до 2025.")
        return

    user_data[user_id] = {"year": text}
    await update.message.reply_text("Отлично! Теперь укажите модель автомобиля (например, Focus, Kuga, Explorer, и т.д.):")
0
# Шаг 3: выбор навигации
async def handle_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    model = update.message.text.strip()

    if not model or len(model) < 2:
        await update.message.reply_text("Пожалуйста, введите корректное название модели.")
        return

    user_data[user_id]["model"] = model

    keyboard = [
        [InlineKeyboardButton("✅ Есть", callback_data="nav_yes")],
        [InlineKeyboardButton("❌ Нет", callback_data="nav_no")],
        [InlineKeyboardButton("❓ Не знаю", callback_data="nav_unknown")]
    ]
    await update.message.reply_text(
        "Есть ли в мультимедии автомобиля встроенная навигация?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Шаг 4: стоимость и ввод телефона
async def handle_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    nav = query.data.replace("nav_", "")
    user_data[user_id]["nav"] = nav

    await query.edit_message_text(
        f"✅ Услуга рассчитана.\n💰 Стоимость: 100.00 BYN\n\nПожалуйста, укажите ваш номер телефона для связи:"
    )

# Шаг 5: номер телефона и отправка заявки
async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    phone = update.message.text.strip()

    if not phone or len(phone) < 6:
        await update.message.reply_text("Пожалуйста, введите корректный номер телефона.")
        return

    user_data[user_id]["phone"] = phone
    summary = user_data[user_id]

    msg = (
        f"📥 Новая заявка:\n"
        f"• Год: {summary['year']}\n"
        f"• Модель: {summary['model']}\n"
        f"• Навигация: {summary['nav']}\n"
        f"• Цена: 100₽\n"
        f"• Телефон: {summary['phone']}"
    )

    keyboard = [[InlineKeyboardButton("📞 Связаться со мной", callback_data="notify_me")]]
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

# Подтверждение заявки
async def handle_notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    summary = user_data.get(user_id, {})

    if summary:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"📬 Заявка от пользователя:\n\n{summary}")
        await query.edit_message_text("✅ Спасибо! Мы все перепроверим и свяжемся с вами в ближайшее время.")
        user_data.pop(user_id, None)
    else:
        await query.edit_message_text("⛔ Данных нет. Начните сначала с /start.")    
# Вместо этого:
# app.run_polling()

# Делаем так:
WEBHOOK_URL = os.getenv("WEBHOOK_URL") or "https://your-app-name.onrender.com"

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # хендлеры...
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback, pattern="^start_calc$"))
    app.add_handler(CallbackQueryHandler(handle_navigation, pattern="^nav_"))
    app.add_handler(CallbackQueryHandler(handle_notify, pattern="^notify_me$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_year))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_model))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone))

    # Webhook вместо polling
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        webhook_url=f"{WEBHOOK_URL}/webhook"
    )