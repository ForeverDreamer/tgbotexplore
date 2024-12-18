import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# from commands.config import set_fee, set_er, start_accounting
from commands.address import query_address
from commands.exchange_rate import real_time_exchange_rates, set_real_time_exchange_rates
# from commands.operator import set_operator, delete_operator
# from commands.transaction import money_in, money_out, show_transaction, delete_transaction
from dao.log import db_log_warning, db_log_error, db_log_info
#
#
COMMANDS = {
    r'^z0$|^显示实时汇率$': real_time_exchange_rates,
    r"^查询地址\s*(0x[a-fA-F0-9]{40})$": query_address,
    # r'^设置操作人$': set_operator,
    # r'^删除操作人$': delete_operator,
    # r'^(设置费率)(\s?)(0\.?\d{0,2})$': set_fee,
    # r'^(设置汇率)(\s?)(\d\.?\d{0,2})$': set_er,
    # r'^设置实时汇率$': set_real_time_exchange_rates,
    # r'^开始$|^开始记账$': start_accounting,
    # r'^(入款|\+|-)(\s?)(\+|-?)(\d+)(u|r?)$': money_in,
    # r'^(下发)(\s?)(\+|-?)(\d+|\d+\.\d{0,2}|0\.\d{0,2})(u|r?)$': money_out,
    # r'^显示账单$': show_transaction,
    # r'^删除账单$': delete_transaction,
}


async def analyze_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('analyze_message, chat_id: ', update.effective_chat.id)
    for cmd in COMMANDS:
        match_obj = re.match(cmd, update.message.text, re.IGNORECASE)
        if match_obj:
            try:
                await COMMANDS[cmd](update, context, *match_obj.groups())
            except Exception as e:
                await db_log_error({'req': update.message.text, 'res': str(e), 'chat_id': update.effective_chat.id})
                raise
            break


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"Sorry, I didn't understand that command."
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")
    await db_log_warning({'req': update.message.text, 'res': text, 'chat_id': update.effective_chat.id})


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = 'I am the official customer service robot of MLMC-VIP. How can I help you?'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    await db_log_info({'req': update.message.text, 'res': text, 'chat_id': chat_id})
