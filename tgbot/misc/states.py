from aiogram.dispatcher.filters.state import StatesGroup, State


class MainMenu(StatesGroup):
    get_menu = State()


class Send(StatesGroup):
    get_type = State()
    get_file = State()
    get_inn = State()


class Project(StatesGroup):
    get_project = State()
    get_doc_type = State()
    get_conf = State()
    get_inn = State()
    get_last_conf = State()


class Percent(StatesGroup):
    get_project = State()
    get_percent = State()
    get_day = State()
    get_inn = State()
    get_last_conf = State()


class Check(StatesGroup):
    get_contract = State()
    get_inn = State()
    get_last_conf = State()


class History(StatesGroup):
    get_contract = State()


class Certificate(StatesGroup):
    get_certificate = State()
