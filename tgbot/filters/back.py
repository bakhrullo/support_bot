import typing

from aiogram.types import CallbackQuery
from aiogram.dispatcher.filters import BoundFilter


class BackFilter(BoundFilter):

    def __init__(self, is_back: typing.Optional[bool] = None):
        self.is_back = is_back

    async def check(self, c: CallbackQuery):
        if c.data == 'back' or c.data == 'backs':
            return False
        return True
