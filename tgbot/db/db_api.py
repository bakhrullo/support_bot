import aiohttp


async def get_projects(user_id, config):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"{config.db.db_url}project", params={"id": user_id}) as \
                response:
            return await response.json()


async def get_project_db(project, config):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"{config.db.db_url}project/{project}") as \
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
        async with session.get(url=f"{config.db.db_url}count/1") as response:
            return await response.json()


async def update_count(config, day):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"{config.db.db_url}count/update", params={"day": day}) as response:
            return await response.json()


async def create_contract(config, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.post(url=f"{config.db.db_url}contract", data={"project": kwargs["project"],
                                                                         "agent": kwargs["agent"],
                                                                         "inn": kwargs["inn"],
                                                                         "code": kwargs["code"]}) as response:
            return await response.json()


async def check_contract(config, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"{config.db.db_url}contract", params={"project": int(kwargs["project"]),
                                                                          "inn": str(kwargs["inn"])}) as response:
            return await response.json()
