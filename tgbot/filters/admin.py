import typing

from aiogram.dispatcher.filters import BoundFilter

from tgbot.config import Config
from tgbot.db.db_api import get_agents
from tgbot.keyboards.inline import register_kb
from tgbot.misc.states import Register


class AdminFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin: typing.Optional[bool] = None):
        self.is_admin = is_admin

    async def check(self, obj):
        if self.is_admin is None:
            return False
        config: Config = obj.bot.get('config')
        res = await get_agents(config)
        agents = [i["tg_id"] for i in res]
        if (obj.from_user.id in agents) == self.is_admin:
            return True
        await Register.get_approve.set()
        await obj.answer("Увы но вы не зарегистрированы, Для регистрации нажмите кнопку ниже 👇", reply_markup=register_kb)
        return False

