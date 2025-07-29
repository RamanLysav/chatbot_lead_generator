from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from handlers import start, brand, model, flow

from utils.data import user_data
from config import BOT_TOKEN

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start.start))
    app.add_handler(CallbackQueryHandler(start.start_calc, pattern="^start_calc$"))
    app.add_handler(CallbackQueryHandler(brand.choose_brand, pattern="^brand_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, model.text_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, flow.text_handler))

    print("Бот запущен ✅")
    app.run_polling()

if __name__ == "__main__":
    main()