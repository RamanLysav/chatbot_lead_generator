import os
import asyncio
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Конфигурация
#BOT_TOKEN = os.getenv("BOT_TOKEN") or "YOUR_BOT_TOKEN"
#ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID") or 123456789)
#WEBHOOK_URL = "https://chatbot-lead-generator.onrender.com"
#WEBHOOK_URL = os.getenv("WEBHOOK_URL")
# Google Sheets
#scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
#creds = ServiceAccountCredentials.from_json_keyfile_name("/etc/secrets/credentials.json", scope)
#client = gspread.authorize(creds)
#sheet = client.open("Заявки FORD").sheet1
from config import BOT_TOKEN, ADMIN_CHAT_ID, WEBHOOK_URL
from config import SHEET

user_data = {}

# /start функция
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚗 Приступить", callback_data="start_calc")],
        [InlineKeyboardButton("ℹ️ Подробнее об услуге", callback_data="show_info")]
    ]
    await update.message.reply_text(
        "⚠️ Здравствуйте! Мы занимаемся перепрошивкой мультимедийных систем Ford, Lincoln.\n\n"
        "📍 Мы работаем только в городе Минск\n\n"
        "📍 Мы работаем официально (УНП: АС2017923) \n\n"
        "Чтобы увидеть стоимость услуги, нажмите 'Приступить' и укажите несколько параметров автомобиля\n\n"
        "Сначала вы видите стоимость, а потом оставляете заявку. Мы не собираем ваши данные и не передаем третьим лицам\n\n",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Под кнопкой Подробнее об услуге

async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("⬅️ Вернуться назад", callback_data="go_back")]]
    await query.edit_message_text(
        "ℹ️ Мы работаем с Мультимедийными системами Ford, Lincoln\n\n"
        "ℹ️ Мы руссифицируем мультимедийный экран, экран приборной панели, а так же голосовой ввод\n\n"        
        "ℹ️ Мы используем только официальные чипы и прошивки Ford\n\n"
        "ℹ️ Мы работаем с выездом по г.Минску, без выходных.\n\n"
        "ℹ️ Процедура занимает 30-180 минут.\n\n"
        "ℹ️ Мы работаем официально, услугу можно оплатить наличным или безналичным расчетом\n\n"
        "📞 Если у вас остались вопросы — просто нажмите «Приступить» и оставьте заявку.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🚗 Приступить", callback_data="start_calc")],
        [InlineKeyboardButton("ℹ️ Подробнее об услуге", callback_data="show_info")]
    ]
    await query.edit_message_text(
        "⚠️ Добро пожаловать обратно!\n\n"
        "Выберите, с чего хотите начать:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Под кнопкой Приступить
async def start_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data[user_id] = {"step": "model"}

    models = [
        ["EcoSport", "Fusion", "Escape"],
        ["Bronco Sport", "Edge", "F-150"],
        ["Mustang", "Другая модель"]
    ]
    markup = ReplyKeyboardMarkup(models, one_time_keyboard=True, resize_keyboard=True)

    await query.edit_message_text("Выберите модель автомобиля:")
    await context.bot.send_message(chat_id=user_id, text="👇 Выберите из списка или нажмите 'Другая модель':", reply_markup=markup)

# Обработка текста
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    session = user_data.get(user_id)

    if not session:
        await update.message.reply_text("Пожалуйста, начните с команды /start.")
        return

    step = session.get("step")

    if step == "model":
        if text == "Другая модель":
            await update.message.reply_text("Введите модель вручную (например, Mondeo):", reply_markup=ReplyKeyboardRemove())
            return
        session["model"] = text
        session["step"] = "year"
        years = [str(y) for y in range(2025, 2014, -1)]
        keyboard = [years[i:i+3] for i in range(0, len(years), 3)]
        keyboard.append(["Другой год"])
        markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("✅ Модель принята.\nТеперь выберите год выпуска автомобиля:", reply_markup=markup)

    elif step == "year":
        if text == "Другой год":
            await update.message.reply_text("Введите год вручную (например, 2012):", reply_markup=ReplyKeyboardRemove())
            return
        if not text.isdigit() or not (2010 <= int(text) <= 2025):
            await update.message.reply_text("⛔ Введите корректный год от 2010 до 2025.")
            return
        session["year"] = text
        session["step"] = "nav"
        await update.message.reply_text("✅ Год принят.", reply_markup=ReplyKeyboardRemove())
        keyboard = [
            [InlineKeyboardButton("✅ Есть", callback_data="nav_yes")],
            [InlineKeyboardButton("❌ Нет", callback_data="nav_no")]
        ]
        await update.message.reply_text("Есть ли встроенная навигация?", reply_markup=InlineKeyboardMarkup(keyboard))

    elif step == "phone":
        if not text.startswith("+375") or len(text) < 13:
            await update.message.reply_text("⛔ Введите номер телефона в формате +375XXXXXXXXX (пример: +375291234567).")
            return
        session["phone"] = text
        session["reached_price"] = False
        keyboard = [[InlineKeyboardButton("📞 Подтвердить заявку и отправить", callback_data="notify_me")]]
        msg = (
            f"📥 Новая заявка:\n"
            f"• Модель: {session['model']}\n"
            f"• Год: {session['year']}\n"
            f"• Навигация: {session['nav']}\n"
            f"• Цена: {session['price']:.2f} BYN\n"
            f"• Телефон: {session['phone']}"
        )
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

# Обработка контакта
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    phone_number = contact.phone_number
    user_id = update.effective_user.id
    session = user_data.get(user_id)
    if session and session.get("step") == "phone":
        session["phone"] = phone_number
        session["reached_price"] = False
        keyboard = [[InlineKeyboardButton("📞 Подтвердить заявку и отправить", callback_data="notify_me")]]
        msg = (
            f"📥 Новая заявка:\n"
            f"• Модель: {session['model']}\n"
            f"• Год: {session['year']}\n"
            f"• Навигация: {session['nav']}\n"
            f"• Цена: {session['price']:.2f} BYN\n"
            f"• Телефон: {session['phone']}"
        )
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))

# Обработка навигации
async def handle_nav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    nav = query.data.replace("nav_", "")
    session = user_data.get(user_id, {})
    session["nav"] = nav
    session["step"] = "phone"
    base_price = 100
    if nav == "yes":
        base_price += 40
    session["price"] = base_price
    session["reached_price"] = True
    session["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    session["first_name"] = update.effective_user.first_name or "—"
    session["username"] = f"@{update.effective_user.username}" if update.effective_user.username else "—"

    async def check_abandoned(user_id, context):
        await asyncio.sleep(300)
        session = user_data.get(user_id)
        if session and session.get("reached_price") and session.get("step") == "phone":
            msg = (
                f"⚠️ Пользователь не завершил заявку:\n"
                f"• Имя: {session.get('first_name', '—')}\n"
                f"• Username: {session.get('username', '—')}\n"
                f"• Telegram ID: {user_id}\n"
                f"• Модель: {session['model']}\n"
                f"• Год: {session['year']}\n"
                f"• Навигация: {session['nav']}\n"
                f"• Цена: {session['price']:.2f} BYN\n"
                f"• Время: {session['timestamp']}"
            )

            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)

    context.application.create_task(check_abandoned(user_id, context))

    keyboard = [[KeyboardButton("📱 Отправить номер", request_contact=True)]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await query.edit_message_text(
        f"✅ Стоимость услуги рассчитана.\n💰 Стоимость: {base_price:.2f} BYN\n\n"
        "Пожалуйста, отправьте номер телефона кнопкой ниже или введите вручную в формате +375XXXXXXXXX чтобы завершить отправку заявки"
    )
    await context.bot.send_message(chat_id=user_id, text="👇 Отправьте номер телефона:", reply_markup=markup)

# Отправка заявки и экспорт в таблицу
async def handle_notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = query.from_user
    session = user_data.get(user_id)

    if session:
        session["reached_price"] = False
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        first_name = user.first_name or "—"
        username = f"@{user.username}" if user.username else "—"

        # Сообщение админу
        msg = (
            f"📬 Заявка от пользователя:\n"
            f"• Имя: {first_name}\n"
            f"• Username: {username}\n"
            f"• Telegram ID: {user_id}\n"
            f"• Время заявки: {timestamp}\n\n"
            f"• Модель: {session['model']}\n"
            f"• Год: {session['year']}\n"
            f"• Навигация: {session['nav']}\n"
            f"• Телефон: {session['phone']}\n"
            f"• Цена: {session['price']:.2f} BYN"
        )
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)

        # Экспорт в Google Таблицу
        SHEET.append_row([
            timestamp,
            first_name,
            username,
            str(user_id),
            session["model"],
            session["year"],
            session["nav"],
            session["phone"],
            f"{session['price']:.2f}"
        ])

        # Ответ пользователю
        restart_keyboard = [[InlineKeyboardButton("🔁 Начать заново", callback_data="start_calc")]]
        await query.edit_message_text(
            "✅ Спасибо! Ваша заявка принята! Мы свяжемся с вами в ближайшее время.",
            reply_markup=InlineKeyboardMarkup(restart_keyboard)
        )
        user_data.pop(user_id, None)
    else:
        await query.edit_message_text("⛔ Данные не найдены. Начните с /start.")


# Версия из Git

from version import get_git_commit_message

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commit_msg = get_git_commit_message()
    await update.message.reply_text(f"🤖 Версия бота: `{commit_msg}`", parse_mode="Markdown")

#import subprocess

#def get_git_commit_message():
#    try:
#        result = subprocess.check_output(["git", "log", "-1", "--pretty=%s"])
#        return result.decode("utf-8").strip()
#    except Exception:
#        return "не удалось получить версию"
    
#async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
#    commit_msg = get_git_commit_message()
#    await update.message.reply_text(f"🤖 Версия бота: `{commit_msg}`", parse_mode="Markdown")

# Основной запуск
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(start_calc, pattern="^start_calc$"))
    app.add_handler(CallbackQueryHandler(handle_nav, pattern="^nav_"))
    app.add_handler(CallbackQueryHandler(handle_notify, pattern="^notify_me$"))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(show_info, pattern="^show_info$"))
    app.add_handler(CallbackQueryHandler(go_back, pattern="^go_back$"))
    app.add_handler(CommandHandler("about", about))

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