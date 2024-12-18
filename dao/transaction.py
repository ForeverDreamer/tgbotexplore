from datetime import timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from extensions.mongodb import db
from share.utils.date import strftime, utc2local, utc_now


async def _query_transaction(chat_id):
    time_from, time_to = calc_ago_time_range()
    in_rows = []
    out_rows = []
    query = {
        'chat_id': chat_id,
        'op_type': 'in',
        '$and': [{'create_time': {'$gte': time_from}}, {'create_time': {'$lt': time_to}}]
    }
    in_num = await db['transaction'].count_documents(query)
    query['op_type'] = 'out'
    out_num = await db['transaction'].count_documents(query)
    del query['op_type']
    in_total = 0
    out_total = 0
    should_total = 0

    count = 3
    async for doc in db['transaction'].find(query).sort('create_time', -1):
        # print(doc)
        doc.pop('_id')
        doc['create_time'] = strftime(utc2local(doc['create_time']))
        # after_fee = doc['amount'] * (1 - doc['fee'])
        # cacl_out = round(after_fee/doc['er'], 2)
        if doc['op_type'] == 'in':
            should_out = doc['should_out']
            should_total += should_out
            row = f"{doc['create_time']}  {doc['after_fee']}/{doc['er']}={should_out}"
            in_total += doc['amount']
            if len(in_rows) >= count:
                continue
            in_rows.append(row)
        else:
            out_total += doc['amount']
            if len(out_rows) >= count:
                continue
            row = f"{doc['create_time']}  {doc['amount']}"
            out_rows.append(row)

    in_rows.insert(0, f"已入款({in_num}笔)：")
    if len(in_rows) == 1:
        in_rows.append('暂无入款')
    in_rows.append('\n')
    in_text = '\n'.join(in_rows)

    out_rows.insert(0, f"已下发({out_num}笔)：")
    if len(in_rows) == 1:
        out_rows.append('暂无下发')
    out_rows.append('\n')
    out_text = '\n'.join(out_rows)

    sum_rows = []
    sum_rows.append(f"总入款金额：{in_total}")
    config = await db['config'].find_one({'_id': chat_id})
    sum_rows.append(f"费率：{config.get('fee')}")
    sum_rows.append(f"汇率：{config.get('er')}")
    sum_rows.append(f"应下发：{round(should_total, 2)}(USDT)")
    sum_rows.append(f"已下发：{out_total}(USDT)")
    sum_rows.append(f"未下发：{round(should_total-out_total, 2)}(USDT)")
    sum_text = '\n'.join(sum_rows)

    buttons = []
    for row in [
        [('供求信息', 'https://t.me/gongqiu_tab'), ('使用说明', 'https://t.me/shuoming_tab')],
        [('公群导航', 'https://t.me/daohang_tab'), ('完整账单', 'https://t.me/AutoAccountingBot')]
    ]:
        _btns = []
        for col in row:
            _btns.append(InlineKeyboardButton(col[0], url=col[1]))
        buttons.append(_btns)
    reply_markup = InlineKeyboardMarkup(buttons)

    return in_text + out_text + sum_text, reply_markup


async def db_money_in(chat_id, operater, op_type, c_type, er_type, er, fee, amount, after_fee, should_out):
    await db['transaction'].insert_one(
        {
            'chat_id': chat_id, 'operater': operater, 'op_type': op_type, 'c_type': c_type, 'er_type': er_type,
            'er': er, 'fee': fee,  'amount': amount, 'after_fee': after_fee, 'should_out': should_out, 'create_time': utc_now()
        }
    )
    return await _query_transaction(chat_id)


async def db_money_out(chat_id, operater, op_type, c_type, er_type, er, fee, amount):
    await db['transaction'].insert_one(
        {
            'chat_id': chat_id, 'operater': operater, 'op_type': op_type, 'c_type': c_type, 'er_type': er_type,
            'er': er, 'fee': fee,  'amount': amount, 'create_time': utc_now()
        }
    )
    return await _query_transaction(chat_id)


async def db_show_transaction(chat_id):
    return await _query_transaction(chat_id)


async def db_delete_transaction(chat_id):
    time_from = utc_now().replace(hour=4, minute=0, second=0, microsecond=0)
    time_to = time_from + timedelta(days=1)
    await db['transaction'].delete_many(
        {
            'chat_id': chat_id,
            '$and': [{'create_time': {'$gte': time_from}}, {'create_time': {'$lt': time_to}}]
        }
    )
