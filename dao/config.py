from constants import ER_TYPE
from extensions.mongodb import db


async def db_get_config(_id):
    return await db['config'].find_one({'_id': _id})


async def db_set_fee(_id, fee):
    await db['config'].update_one({'_id': _id}, {'$set': {'fee': fee}}, upsert=True)


async def db_set_er(_id, er):
    await db['config'].update_one({'_id': _id}, {'$set': {'er': er, 'er_type': ER_TYPE[0][0]}}, upsert=True)


async def db_set_rter(_id, rter):
    await db['config'].update_one({'_id': _id}, {'$set': {'rter': rter, 'er_type': ER_TYPE[1][0]}}, upsert=True)


async def db_start_accounting(_id):
    config = await db['config'].find_one({'_id': _id})
    er_type = config.get('er_type')
    fee = config.get('fee')
    if (er_type is None) or (fee is None):
        return '必须先设置费率和汇率才能开始记账'
    if config.get('started'):
        return '记账功能工作中'
    await db['config'].update_one({'_id': _id}, {'$set': {'started': True}})
    return '记账功能开始工作'
