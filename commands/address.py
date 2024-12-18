from collections import defaultdict

import aiohttp
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, ContextTypes

from share.constants.misc import ETHERSCAN_API_KEY, ETHERSCAN_BASE_URL


# 地址监听器
watched_addresses = {}


# 查询 USDT 地址信息（ERC-20）
async def _query_address(address: str):
    url = f"{ETHERSCAN_BASE_URL}?module=account&action=tokentx&address={address}&apikey={ETHERSCAN_API_KEY}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            if data["status"] == "1":
                transactions = data["result"]
                # 使用 defaultdict 初始化统计数据
                tokens = defaultdict(lambda: {"balance": 0, "transaction_count": 0, "symbol": None, "decimals": 0})

                for tx in transactions:
                    contract_address = tx["contractAddress"].lower()
                    symbol = tx.get("tokenSymbol", "Unknown")
                    decimals = int(tx.get("tokenDecimal", 18))  # 默认精度为 18

                    value = int(tx["value"]) / (10 ** decimals)

                    # 收到代币
                    if tx["to"].lower() == address.lower():
                        tokens[contract_address]["balance"] += value
                    # 发出代币
                    if tx["from"].lower() == address.lower():
                        tokens[contract_address]["balance"] -= value

                    # 增加交易计数
                    tokens[contract_address]["transaction_count"] += 1
                    # 更新代币符号和精度
                    tokens[contract_address]["symbol"] = symbol
                    tokens[contract_address]["decimals"] = decimals

                # 转换结果为列表形式（便于输出或处理）
                tokens = [
                    {
                        "contract_address": contract,
                        "symbol": token["symbol"],
                        "balance": token["balance"],
                        "transaction_count": token["transaction_count"],
                    }
                    for contract, token in tokens.items()
                ]
                total = len(tokens)
                # 按交易笔数排序，并只取前 top_n 个
                tokens = sorted(tokens, key=lambda x: x["transaction_count"], reverse=True)[:3]
                return total, tokens
            else:
                return 0, []


# 查询命令的处理函数
async def query_address(update: Update, context: ContextTypes.DEFAULT_TYPE, *args):
    if len(args) != 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=("请使用格式：/query_address <地址>"))
        return
    address = args[0]
    total, tokens = await _query_address(address)
    text = [f"该钱包地址共进行过{total}种代币的交易，笔数最多的三种如下："]
    for token in tokens:
        text.append(f"代币类型: {token['symbol']}")
        text.append(f"合约地址: {token['contract_address']}")
        text.append(f"余额: {token['balance']}")
        text.append(f"交易笔数: {token['transaction_count']}")
        text.append("-" * 30)
    text = "\n".join(text)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


# 地址监听注册
def handle_watch(update: Update, context: CallbackContext) -> None:
    if len(context.args) != 1:
        update.message.reply_text("请使用格式：/watch_address <地址>")
        return
    address = context.args[0]
    watched_addresses[address] = {"user_id": update.message.chat_id, "last_tx_count": 0}
    update.message.reply_text(f"已开始监听地址：{address}")

# 定时检查监听地址
def check_addresses():
    for address, info in watched_addresses.items():
        data = query_address(address)
        new_tx_count = len(data["transactions"])
        if new_tx_count > info["last_tx_count"]:
            new_txs = new_tx_count - info["last_tx_count"]
            Updater.bot.send_message(chat_id=info["user_id"], text=f"地址：{address}\n检测到 {new_txs} 笔新交易！")
            watched_addresses[address]["last_tx_count"] = new_tx_count

# 定时任务
# def start_schedule():
#     schedule.every(30).seconds.do(check_addresses)
#     while True:
#         schedule.run_pending()
#         time.sleep(1)
#
# # 主函数
# def main():
#     # 初始化 Telegram Bot
#     updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
#     dispatcher = updater.dispatcher
#
#     # 注册命令
#     dispatcher.add_handler(CommandHandler("query_address", handle_query))
#     dispatcher.add_handler(CommandHandler("watch_address", handle_watch))
#
#     # 启动 Bot
#     updater.start_polling()
#
#     # 启动定时任务
#     start_schedule()
#
# if __name__ == "__main__":
#     main()
