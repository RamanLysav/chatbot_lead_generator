import asyncio
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
)
from config import BOT_TOKEN, WEBHOOK_URL, PORT
from handlers import start, flow, callbacks, system

async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Стартовые команды и кнопки
    app.add_handler(CommandHandler("start", start.start))
    app.add_handler(CallbackQueryHandler(start.show_info, pattern="^show_info$"))
    app.add_handler(CallbackQueryHandler(start.go_back, pattern="^go_back$"))

    # Поток логики
    app.add_handler(CallbackQueryHandler(flow.start_calc, pattern="^start_calc$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, flow.handle_text))
    app.add_handler(MessageHandler(filters.CONTACT, flow.handle_contact))

    # Кнопки завершения
    app.add_handler(CallbackQueryHandler(callbacks.handle_nav, pattern="^nav_"))
    app.add_handler(CallbackQueryHandler(callbacks.handle_notify, pattern="^notify_me$"))

    # Системная команда
    app.add_handler(CommandHandler("about", system.about))

    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"{WEBHOOK_URL}/webhook",
        allowed_updates=["message", "callback_query"]
    )

if __name__ == "__main__":
    asyncio.run(main())