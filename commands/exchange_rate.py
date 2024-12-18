from datetime import datetime as dt

import aiohttp

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from dao.config import db_get_config, db_set_rter
from dao.log import db_log_info, db_log_error
from constants import EXPIRE_TIME
from extensions import redis


async def _get_exchange_rates(update, key):
    cmd, payment_method = key.split('_')
    async with aiohttp.ClientSession() as session:
        timestamp = ''.join(str(dt.now().timestamp()).split('.'))[:-3]
        rows = []
        async with session.get(
                f'https://www.okx.com/v3/c2c/tradingOrders/books?t={timestamp}&quoteCurrency=CNY&baseCurrency=USDT&side=sell&paymentMethod={payment_method}&userType=all&showTrade=false&showFollow=false&showAlreadyTraded=false&isAbleFilter=false&receivingAds=false') as response:
            dic = await response.json()
            for i, record in enumerate(dic['data']['sell'][:10]):
                rows.append(
                    f'{i+1}){" "*2}{record["price"]}{" "*8}{record["nickName"]}')
            rows.append('')
    chat_id = update.effective_chat.id
    # config = await db_get_config(chat_id)
    # rows.append(f'本群费率：{config["fee"]}')
    # rows.append(f'本群汇率：{config["er"]}')

    buttons = []
    for k, v in CALLBACKS.items():
        _cmd, value = k.split('_')
        if _cmd != cmd or (value not in ('all', 'bank', 'aliPay', 'wxPay')):
            continue
        btn_text = v['text'] + '✅' if value == payment_method else v['text']
        buttons.append(InlineKeyboardButton(btn_text, callback_data=k))

    return rows, [buttons], dic['data']['sell'][:10]


async def real_time_exchange_rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows, keyboard, _ = await _get_exchange_rates(update, 'rter_all')
    text = '\n'.join(rows)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)
    await db_log_info({'req': update.message.text, 'res': text, 'chat_id': update.effective_chat.id})


# 设置实时汇率相关
async def _set_fine_tune_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()

    # amount = query.data
    # text, reply_markup = await get_exchange_rates(update, payment_method)
    # await query.edit_message_text(text=text, reply_markup=reply_markup)


async def _set_exchange_rates(update, key):
    _, oper = key.split('_')
    chat_id = update.effective_chat.id
    ranking = f'{chat_id}:ranking'
    payment_method = f'{chat_id}:payment_method'
    fine_tune_price = f'{chat_id}:fine_tune_price'
    k_price = f'{chat_id}:price'

    if oper in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
        redis.kset(ranking, oper, ex=EXPIRE_TIME)
    elif oper in ('all', 'bank', 'aliPay', 'wxPay'):
        redis.kset(payment_method, oper, ex=EXPIRE_TIME)
    elif oper in ('-0.1', '0.1', '-0.01', '0.01'):
        redis.incrbyfloat(fine_tune_price, float(oper))
    elif oper == 'confirm':
        price = redis.get(k_price)
        _ranking = redis.get(ranking) or '0'
        _payment_method = redis.get(payment_method) or 'all'
        _fine_tune_price = redis.get(fine_tune_price or '0')
        _fine_tune_price = float(_fine_tune_price)
        redis.delete(ranking, payment_method, fine_tune_price, k_price)
        if price:
            text = f'汇率设置成功！当前实时汇率：{price}'
            await db_set_rter(
                chat_id, {'ranking': _ranking, 'payment_method': _payment_method, 'fine_tune_price': _fine_tune_price}
            )
            await db_log_info({'req': key, 'res': text, 'chat_id': chat_id})
        else:
            text = '操作超时，请重试！'
            await db_log_error({'req': key, 'res': text, 'chat_id': chat_id})
        return text, None, None
    else:
        raise ValueError(f'Invalid oper: {oper}')

    _ranking = redis.get(ranking) or '0'
    _payment_method = redis.get(payment_method) or 'all'
    _fine_tune_price = redis.get(fine_tune_price or '0')
    _fine_tune_price = float(_fine_tune_price)

    ranking_1_btns = []
    ranking_2_btns = []
    fine_tune_1_btns = []
    fine_tune_2_btns = []
    confirm_btns = []
    for k, v in CALLBACKS.items():
        cmd, value = k.split('_')
        if value in ('0', '1', '2', '3', '4'):
            btn_text = v['text'] + '✅' if value == _ranking else v['text']
            ranking_1_btns.append(InlineKeyboardButton(btn_text, callback_data=k))
        elif value in ('5', '6', '7', '8', '9'):
            btn_text = v['text'] + '✅' if value == _ranking else v['text']
            ranking_2_btns.append(InlineKeyboardButton(btn_text, callback_data=k))
        elif value in ('-0.1', '0.1'):
            fine_tune_1_btns.append(InlineKeyboardButton(v['text'], callback_data=k))
        elif value in ('-0.01', '0.01'):
            fine_tune_2_btns.append(InlineKeyboardButton(v['text'], callback_data=k))
        elif value == 'confirm':
            confirm_btns.append(InlineKeyboardButton(v['text'], callback_data=k))

    rows, keyboard, data = await _get_exchange_rates(update, f'srter_{_payment_method}')
    rows = rows[:-2]
    price = float(data[int(_ranking)]["price"])
    rows.append(f'当前档位价格：{price}')
    rows.append(f'微调价格：{_fine_tune_price}')
    price = round(price + _fine_tune_price, 2)
    redis.kset(k_price, price, ex=EXPIRE_TIME)
    rows.append(f'价格：{price}')

    keyboard = [ranking_1_btns, ranking_2_btns, keyboard[0], fine_tune_1_btns, fine_tune_2_btns, confirm_btns]

    return rows, keyboard, data


async def set_real_time_exchange_rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    ranking = f'{chat_id}:ranking'
    payment_method = f'{chat_id}:payment_method'
    fine_tune_price = f'{chat_id}:fine_tune_price'
    redis.kset(ranking, '0', ex=EXPIRE_TIME)
    redis.kset(payment_method, 'all', ex=EXPIRE_TIME)
    redis.kset(fine_tune_price, '0', ex=EXPIRE_TIME)
    rows, keyboard, _ = await _set_exchange_rates(update, 'srter_all')
    text = '\n'.join(rows)
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)
    await db_log_info({'req': update.message.text, 'res': text, 'chat_id': update.effective_chat.id})


CALLBACKS = {
    'rter_all': {'text': '所有', 'cb': _get_exchange_rates},
    'rter_bank': {'text': '银行卡', 'cb': _get_exchange_rates},
    'rter_aliPay': {'text': '支付宝', 'cb': _get_exchange_rates},
    'rter_wxPay': {'text': '微信', 'cb': _get_exchange_rates},
    'srter_all': {'text': '所有', 'cb': _set_exchange_rates},
    'srter_bank': {'text': '银行卡', 'cb': _set_exchange_rates},
    'srter_aliPay': {'text': '支付宝', 'cb': _set_exchange_rates},
    'srter_wxPay': {'text': '微信', 'cb': _set_exchange_rates},
    'srter_0': {'text': '1', 'cb': _set_exchange_rates},
    'srter_1': {'text': '2', 'cb': _set_exchange_rates},
    'srter_2': {'text': '3', 'cb': _set_exchange_rates},
    'srter_3': {'text': '4', 'cb': _set_exchange_rates},
    'srter_4': {'text': '5', 'cb': _set_exchange_rates},
    'srter_5': {'text': '6', 'cb': _set_exchange_rates},
    'srter_6': {'text': '7', 'cb': _set_exchange_rates},
    'srter_7': {'text': '8', 'cb': _set_exchange_rates},
    'srter_8': {'text': '9', 'cb': _set_exchange_rates},
    'srter_9': {'text': '10', 'cb': _set_exchange_rates},
    'srter_-0.1': {'text': '减0.1', 'cb': _set_exchange_rates},
    'srter_0.1': {'text': '加0.1', 'cb': _set_exchange_rates},
    'srter_-0.01': {'text': '减0.01', 'cb': _set_exchange_rates},
    'srter_0.01': {'text': '加0.01', 'cb': _set_exchange_rates},
    'srter_confirm': {'text': '确认', 'cb': _set_exchange_rates},
}


async def callback_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    key = query.data
    rows, keyboard, _ = await CALLBACKS[key]['cb'](update, key)
    text = '\n'.join(rows) if type(rows) == list else rows
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    await query.edit_message_text(text=text, reply_markup=reply_markup)


