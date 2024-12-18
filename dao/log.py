from extensions.mongodb import db


async def db_log_info(doc):
    await db['log_info'].insert_one(doc)


async def db_log_warning(doc):
    await db['log_warning'].insert_one(doc)


async def db_log_error(doc):
    await db['log_error'].insert_one(doc)
