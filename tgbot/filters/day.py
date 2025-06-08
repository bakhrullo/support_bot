from aiogram.dispatcher.filters import BoundFilter
from datetime import datetime

from tgbot.db.db_api import get_agent


class WeekdayFilter(BoundFilter):
    key = 'allow_weekdays'

    def __init__(self, allow_weekdays: bool):
        self.allow_weekdays = allow_weekdays

    async def check(self, obj):
        weekday = datetime.now().weekday()  # Пн = 0, Вс = 6
        if not self.allow_weekdays:
            return True
        if weekday < 5:
            return True  # Только если Пн–Пт (0–4)
        user = await get_agent(obj.bot.get('config'), obj.from_user.id)
        if user["is_permission"]:
            return True
        await obj.answer("Извините, но по выходным мы не работаем 😔")
        return False
