import motor.motor_asyncio

from share.constants.misc import MONGO_URI

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client['inves']
