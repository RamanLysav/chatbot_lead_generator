from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import os

user_data = {}

BOT_TOKEN = os.getenv("BOT_TOKEN") or "YOUR_BOT_TOKEN"
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID") or 123456789)  # ← Замени на свой Telegram user ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Посчитать стоимость", callback_data="calculate")]]
    await update.message.reply_text(
        "⚠️ Добро пожаловать в сервис подсчета руссификации и перепрошивки мультимедийных систем автомобилей FORD. "
        "Пожалуйста, ответьте на пару вопросов, затем вы увидите стоимость услуги и сможете записаться на перепрошивку. "
        "Внимание: ваши ответы будут сохранены для отправки заявки.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if user_id not in user_data:
        user_data[user_id] = {}

    if data == "calculate":
        await query.edit_message_text("Введите год выпуска автомобиля (например, 2018):")

async def handle_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    year = update.message.text.strip()

    if not year.isdigit() or not (1999 <= int(year) <= 2025):
        await update.message.reply_text("Пожалуйста, введите корректный год, например: 2021")
        return

    user_data[user_id] = {"year": year, "choice2": []}

    keyboard = [
        [InlineKeyboardButton("А", callback_data="step2_A")],
        [InlineKeyboardButton("Б", callback_data="step2_B")],
        [InlineKeyboardButton("В", callback_data="step2_V")],
        [InlineKeyboardButton("✅ Готово", callback_data="finish")]
    ]
    await update.message.reply_text(
        f"✅ Год: {year}\nТеперь выберите один или несколько пунктов:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if user_id not in user_data or "year" not in user_data[user_id]:
        await query.edit_message_text("Ошибка: начните сначала с команды /start")
        return

    if data.startswith("step2_"):
        option = data.split("_")[1]
        if option not in user_data[user_id]["choice2"]:
            user_data[user_id]["choice2"].append(option)
            await query.answer(f"Добавлено: {option}", show_alert=True)

    elif data == "finish":
        summary = user_data[user_id]
        price = "100₽"

        msg = (
            f"📝 Новая заявка:\n"
            f"• Год авто: {summary['year']}\n"
            f"• Выбор(ы): {', '.join(summary['choice2']) if summary['choice2'] else '—'}\n"
            f"• Цена: {price}"
        )

        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)
        await query.edit_message_text(f"{msg}\n\nСпасибо за выбор!")
        del user_data[user_id]

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback, pattern="^calculate$"))
    app.add_handler(CallbackQueryHandler(handle_options, pattern="^(step2_|finish)"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_year))
    app.run_polling()