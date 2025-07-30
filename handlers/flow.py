# handlers/flow.py

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import ContextTypes
from data.session import user_data

async def start_calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # Инициализируем новую сессию
    user_data[user_id] = {"step": "model"}

    # Варианты моделей
    models = [
        ["EcoSport", "Fusion", "Escape"],
        ["Bronco Sport", "Edge", "F-150"],
        ["Mustang", "Другая модель"],
    ]
    markup = ReplyKeyboardMarkup(models, one_time_keyboard=True, resize_keyboard=True)

    await query.edit_message_text("Выберите модель автомобиля:")
    await context.bot.send_message(
        chat_id=user_id,
        text="👇 Выберите из списка или нажмите «Другая модель»:",
        reply_markup=markup,
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = user_data.get(user_id)

    # Если сессии нет — просим начать сначала
    if not session:
        await update.message.reply_text("Пожалуйста, начните с команды /start.")
        return

    text = update.message.text.strip()
    step = session.get("step")

    # 1) Выбор (или ручной ввод) модели
    if step == "model":
        if text == "Другая модель":
            await update.message.reply_text(
                "Введите модель вручную:", reply_markup=ReplyKeyboardRemove()
            )
            return

        session["model"] = text
        session["step"] = "year"

        # Генерируем кнопки с годами
        years = [str(y) for y in range(2025, 2014, -1)]
        keyboard = [years[i : i + 3] for i in range(0, len(years), 3)] + [["Другой год"]]
        markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(
            "✅ Модель принята.\nТеперь выберите год:", reply_markup=markup
        )
        return

    # 2) Выбор (или ручной ввод) года
    if step == "year":
        if text == "Другой год":
            await update.message.reply_text(
                "Введите год вручную:", reply_markup=ReplyKeyboardRemove()
            )
            return

        if not text.isdigit() or not (2010 <= int(text) <= 2025):
            await update.message.reply_text("⛔ Введите корректный год от 2010 до 2025.")
            return

        session["year"] = text
        session["step"] = "phone"

        # Предлагаем выбрать наличие навигации
        nav_buttons = [
            InlineKeyboardButton("Есть навигация", callback_data="nav_yes"),
            InlineKeyboardButton("Нет навигации", callback_data="nav_no"),
        ]
        markup = InlineKeyboardMarkup([nav_buttons])

        await update.message.reply_text(
            f"✅ Год принят: {text}\n"
            "Выберите, есть ли штатная навигация:",
            reply_markup=markup,
        )
        return

    # 3) Ввод телефона (кнопка «Отправить номер» или ручной ввод)
    if step == "phone":
        # Если пришёл контакт через кнопку
        if update.message.contact:
            phone = update.message.contact.phone_number
        else:
            phone = text

        session["phone"] = phone
        session["step"] = "confirm"

        # Подтверждаем отправку заявки
        confirm_buttons = [
            [InlineKeyboardButton("✅ Отправить заявку", callback_data="notify")],
            [InlineKeyboardButton("🔄 Начать заново", callback_data="start_calc")],
        ]
        markup = InlineKeyboardMarkup(confirm_buttons)

        await update.message.reply_text(
            f"📞 Ваш телефон: {phone}\n\n"
            "Нажмите «Отправить заявку», чтобы подтвердить.",
            reply_markup=markup,
        )
        return

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    phone = update.message.contact.phone_number
    session = user_data.get(user_id)

    if not session or session.get("step") != "phone":
        await update.message.reply_text("⛔ Неожиданный контакт. Начните с /start.")
        return

    session["phone"] = phone
    session["step"] = "confirm"

    confirm_buttons = [
        [InlineKeyboardButton("✅ Отправить заявку", callback_data="notify_me")],
        [InlineKeyboardButton("🔄 Начать заново", callback_data="start_calc")],
    ]
    markup = InlineKeyboardMarkup(confirm_buttons)

    await update.message.reply_text(
        f"📞 Ваш номер: {phone}\n\nНажмите «Отправить заявку», чтобы подтвердить.",
        reply_markup=markup,
    )