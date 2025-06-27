from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

user_data = {}

BOT_TOKEN = os.getenv("BOT_TOKEN") or "YOUR_BOT_TOKEN"
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID") or YOUR_ADMIN_CHAT_ID)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Посчитать", callback_data="calculate")]]
    await update.message.reply_text(
        "⚠️ Внимание: ваши ответы будут сохранены для отправки заявки.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if user_id not in user_data:
        user_data[user_id] = {"choice2": []}

    if data == "calculate":
        keyboard = [[InlineKeyboardButton(str(i), callback_data=f"step1_{i}")] for i in (1, 2, 3)]
        await query.edit_message_text("Выберите вариант:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("step1_"):
        user_data[user_id]['choice1'] = data[-1]
        keyboard = [
            [InlineKeyboardButton("А", callback_data="step2_A")],
            [InlineKeyboardButton("Б", callback_data="step2_B")],
            [InlineKeyboardButton("В", callback_data="step2_V")],
            [InlineKeyboardButton("✅ Готово", callback_data="finish")]
        ]
        await query.edit_message_text("Выберите один или несколько вариантов:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("step2_"):
        option = data.split("_")[1]
        if option not in user_data[user_id]['choice2']:
            user_data[user_id]['choice2'].append(option)
            await query.answer(f"Добавлено: {option}", show_alert=True)

    elif data == "finish":
        summary = user_data[user_id]
        price = "100₽"
        msg = (
            f"📝 Новая заявка:\n"
            f"• Вариант: {summary['choice1']}\n"
            f"• Выбор(ы): {', '.join(summary['choice2'])}\n"
            f"• Цена: {price}"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)
        await query.edit_message_text(f"{msg}\n\nСпасибо за выбор!")
        del user_data[user_id]

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_callback))

if __name__ == "__main__":
    app.run_polling()