import aiohttp
import base64


async def didox_create(config):
    async with aiohttp.ClientSession() as session:
        async with session.post(url=config.misc.didox_token_url, data={"password": config.misc.didox_pass}) as \
                response:
            res = await response.json()
    async with aiohttp.ClientSession() as session:
        async with session.post(url=config.misc.didox_token_url, data={"password": config.misc.didox_pass}) as \
                response:
            res = await response.json()