import os
from share.utils.misc import load_secret

secret = load_secret()

MONGO_URI = os.getenv(
    'MONGO_URI',
    f"mongodb://root:{secret['mongodb_pwd']['encoded']}@mongo1:17017,mongo2:17018,mongo3:17019/inves?replicaSet=rs0&authSource=admin"
)

REDIS_URI = os.getenv('REDIS_URI', f"redis://{secret['rds_host']}:16379/0")

BOT_TOKEN = secret['bot_token']

ETHERSCAN_API_KEY = secret['etherscan_api_key']

ETHERSCAN_BASE_URL = "https://api.etherscan.io/api"
