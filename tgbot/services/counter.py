from tgbot.db.db_api import get_count, update_count
from datetime import datetime


async def count(config):
    res = await get_count(config)
    print(res)
    if res["day"] == int(datetime.now().strftime("%d")):
        return res["count"]
    await update_count(config, day=datetime.now().strftime("%d"))
    return 1
