import aiohttp


async def get_contracts(user_id, option, config):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"{config.db.db_url}project", params={"id": user_id, "option": option}) as\
                response:
            return await response.json()


async def get_agents(config):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"{config.db.db_url}agent") as response:
            return await response.json()
