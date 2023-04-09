from aiogram.dispatcher.filters.state import StatesGroup, State


class MainMenu(StatesGroup):
    get_menu = State()


class Contract(StatesGroup):
    get_contract = State()
    get_conf = State()
    get_inn = State()
    get_last_conf = State()


class Check(StatesGroup):
    get_contract = State()
    get_inn = State()
    get_last_conf = State()
