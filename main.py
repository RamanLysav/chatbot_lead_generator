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
from config import BOT_TOKEN

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Conversation flow
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start.start),
            CallbackQueryHandler(start.start_calc, pattern="^start_calc$")  # 👈 перенесли сюда!
        ],
        states={
            BRAND: [
                CallbackQueryHandler(brand.choose_brand, pattern="^brand_")
            ],
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

    print("Бот запущен ✅")
    app.run_polling()

if __name__ == "__main__":
    main()