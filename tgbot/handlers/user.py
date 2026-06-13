from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.db.db_api import get_city, get_all_projects, create_request, get_agents, get_agent
from tgbot.keyboards.inline import city_kb, project_kb, menu_kb
from tgbot.misc.states import Register, MainMenu


async def start(m: Message, config):
    res = await get_agents(config)
    agents = [i["tg_id"] for i in res]
    if m.from_user.id in agents:
        user = await get_agent(config, m.from_user.id)
        await MainMenu.get_menu.set()
        return await m.answer(f"Здравствуйте, {m.from_user.full_name} 👋\n"
                              f"Рады видеть вас в боте Support Samarkand\n\n"
                              f"Пожалуйста, выберите нужный раздел с помощью кнопок ниже 👇",
                              reply_markup=menu_kb(user["is_boss"]))
    citys = await get_city(config)
    await m.answer("Выберите город 🏬", reply_markup=city_kb(citys))
    await Register.get_city.set()


async def register(c: CallbackQuery, config):
    citys = await get_city(config)
    await c.message.edit_text("Выберите город 🏬", reply_markup=city_kb(citys))
    await Register.next()


async def get_city_id(c: CallbackQuery, state: FSMContext, config):
    await state.update_data(city_id=c.data)
    projects = await get_all_projects(config)
    await c.message.edit_text("Выберите проект 📄", reply_markup=project_kb(projects))
    await Register.next()


async def get_project_id(c: CallbackQuery, state: FSMContext):
    await state.update_data(project_id=c.data)
    await c.message.edit_text("Напишите свое имя")
    await Register.next()


async def get_name(m: Message, state: FSMContext, config):
    data = await state.get_data()
    await create_request(config, name=m.text, city=data["city_id"], project=data["project_id"], tg_id=m.from_user.id)
    await m.answer("Ваша заявка на регистрацию принята ожидайте одобрение администратора")


def register_user(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start"], state="*")
    dp.register_callback_query_handler(register, state=Register.get_approve)
    dp.register_callback_query_handler(get_city_id, state=Register.get_city)
    dp.register_callback_query_handler(get_project_id, state=Register.get_proj)
    dp.register_message_handler(get_name, state=Register.get_name)
