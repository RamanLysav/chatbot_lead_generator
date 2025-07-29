import telegram
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
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start.start),
            CallbackQueryHandler(start.start_calc, pattern="^start_calc$")
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

    # Установка webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
        allowed_updates=[
            "message",
            "edited_message",
            "channel_post",
            "edited_channel_post",
            "inline_query",
            "chosen_inline_result",
            "callback_query",
            "shipping_query",
            "pre_checkout_query",
            "poll",
            "poll_answer",
            "my_chat_member",
            "chat_member",
            "chat_join_request"
        ]
    )

if __name__ == "__main__":
    main()