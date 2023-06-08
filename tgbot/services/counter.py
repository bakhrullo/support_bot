from tgbot.db.db_api import get_count
from datetime import datetime


async def count(config):
    res = await get_count(config)
    if res.day == int(datetime.now().strftime("%d")):
        return res.count
    await res.update(count=1, day=int(datetime.now().strftime("%d"))).apply()
    return 1
