from datetime import date

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from tgbot.db.db_api import get_projects, get_agent, update_count
from tgbot.filters.back import BackFilter
from tgbot.keyboards.inline import *
from tgbot.misc.states import MainMenu, Project, Check
from tgbot.services.counter import count
from tgbot.services.pdf import pdf_create


async def start(m: Message):
    await m.answer(f"Assalomu alaykum {m.from_user.full_name} 👋\n"
                   f"Sizni Supprot Samarkand Botida ko'rib turganimizdan mamnunmiz\n\n"
                   f"Iltimos pastdagi tugmalar orqali kerakli bo'limni tanlang👇", reply_markup=menu_kb)
    await MainMenu.get_menu.set()


async def project(c: CallbackQuery, config):
    projects = await get_projects(c.from_user.id, "user", config)
    await c.message.edit_text(f"Sizda {len(projects)} ta proekt mavjud 📋\nQaysi biriga shartnoma qilishni istaysiz?",
                              reply_markup=contracts_kb(projects))
    await Project.get_project.set()


async def get_project(c: CallbackQuery, state: FSMContext, config):
    counter, agent = await count(config), await get_agent(config, c.from_user.id)
    number = f"{counter}/{agent['uniq']} от {date.today().strftime('%d.%m.%Y')}"
    await state.update_data(number=number, id=c.data)
    await c.message.edit_text(f"Dogovor raqam olindi ✅\nSizning dogovor raqamingiz:\n\n{number}",
                              reply_markup=contract_conf_kb)
    await Project.next()


async def get_conf(c: CallbackQuery):
    await c.message.edit_text("Iltimos INN ni kiriting")
    await Project.next()


async def get_inn(m: Message, state: FSMContext):
    data = await state.get_data()
    await m.answer(f"Dogovor raqam:\n{data['number']}\nKorxona INN si:\n{m.text}\nProekt nomi:\n{data['id']}\n"
                   f"keltirilgan ma'lumotlarni\ntasdiqlaysizmi?", reply_markup=contract_conf_kb)
    await state.update_data(inn=m.text)
    await Project.next()


async def last_conf(c: CallbackQuery, state: FSMContext, config):
    data = await state.get_data()
    await update_count(config)
    pdf_create(data['number'])




async def check(c: CallbackQuery, config):
    kb, count = await contracts_kb(c.from_user.id, config)
    await c.message.edit_text(f"Sizda {count} ta proekt mavjud 📋\nQaysi proekt uchun tekshirmoxchisiz?",
                              reply_markup=kb)
    await Check.get_contract.set()


async def get_check_contract(c: CallbackQuery):
    await c.message.edit_text("Qaysi do'konning shartnomasini tekshirmoxchisiz?\nIltimos do'kon INN sini kiriting")
    await Check.next()


async def get_check_inn(m: Message):
    await m.answer("Ushbu do'konda imzolanmay\nqolgan shartnoma mavjud emas", reply_markup=menu_kb)
    await MainMenu.get_menu.set()


async def get_last_conf(c: CallbackQuery):
    await c.message.edit_text("Qabul qilindi ✅", reply_markup=menu_kb)
    await MainMenu.get_menu.set()


async def back(c: CallbackQuery):
    await c.message.edit_text("Bosh menu", reply_markup=menu_kb)
    await MainMenu.get_menu.set()


def register_admin(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start"], state="*", is_admin=True)
    dp.register_callback_query_handler(project, Text(equals="contract"), state=MainMenu.get_menu, is_admin=True)
    dp.register_callback_query_handler(check, Text(equals="check"), state=MainMenu.get_menu, is_admin=True)
    dp.register_callback_query_handler(get_check_contract, state=Check.get_contract, is_admin=True)
    dp.register_callback_query_handler(get_project, BackFilter(), state=Project.get_project, is_admin=True)
    dp.register_callback_query_handler(get_conf, BackFilter(), state=Project.get_conf, is_admin=True)
    dp.register_message_handler(get_inn, state=Project.get_inn, is_admin=True)
    dp.register_message_handler(get_check_inn, state=Check.get_inn, is_admin=True)
    dp.register_callback_query_handler(get_last_conf, BackFilter(), state=Project.get_last_conf, is_admin=True)
    dp.register_callback_query_handler(back, state="*", is_admin=True)
