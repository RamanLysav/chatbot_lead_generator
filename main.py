import logging
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters
)

from handlers import start, brand, model, flow
from handlers.states import BRAND, MODEL, YEAR, NAV, PHONE, DONE
from config import BOT_TOKEN, WEBHOOK_URL, PORT

def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    app = Application.builder().token(BOT_TOKEN).build()

    # Обработчик разговоров
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start.start),
            CallbackQueryHandler(start.start_calc, pattern="^start_calc$")
        ],
        states={
            BRAND: [CallbackQueryHandler(brand.choose_brand, pattern="^brand_")],
            MODEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, model.text_handler)],
            YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, flow.year_handler)],
            NAV: [MessageHandler(filters.TEXT & ~filters.COMMAND, flow.nav_handler)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, flow.phone_handler)],
            DONE: []
        },
        fallbacks=[],
        allow_reentry=True
    )

    app.add_handler(conv_handler)

    # Попытка запуска webhook — с fallback на polling
    try:
        logger.info("🔗 Устанавливаю webhook...")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=WEBHOOK_URL,
            allowed_updates=[
                "message",
                "callback_query"
            ]
        )
    except Exception as e:
        logger.warning(f"❗️ Ошибка при запуске webhook: {e}")
        logger.info("🔄 Переключаюсь на polling...")
        app.run_polling()

if __name__ == "__main__":
    main()