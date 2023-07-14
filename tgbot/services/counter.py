from tgbot.db.db_api import get_count, update_count
from datetime import datetime


async def count(config):
    res = await get_count(config)
    if res["year"] == int(datetime.now().strftime("%Y")):
        return res["count"]
    await update_count(config, year=datetime.now().strftime("%Y"))
    return 1
