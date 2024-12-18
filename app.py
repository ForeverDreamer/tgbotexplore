import logging

from telegram.ext import ApplicationBuilder, CallbackQueryHandler, MessageHandler, filters, CommandHandler

from commands.exchange_rate import callback_entry
from commands.misc import analyze_message, start
from share.constants.misc import BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(callback_entry))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), analyze_message))

    application.run_polling()
