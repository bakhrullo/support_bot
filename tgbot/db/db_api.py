import aiohttp


async def get_projects(user_id, option, config):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"{config.db.db_url}project", params={"id": user_id, "option": option}) as \
                response:
            return await response.json()


async def get_agents(config):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"{config.db.db_url}agent") as response:
            return await response.json()


async def get_agent(config, user_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"{config.db.db_url}agent/{user_id}") as response:
            return await response.json()


async def get_count(config):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"{config.db.db_url}count") as response:
            return await response.json()


async def update_count(config):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"{config.db.db_url}count/update") as response:
            return await response.json()
