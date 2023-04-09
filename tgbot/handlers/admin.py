from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from tgbot.filters.back import BackFilter
from tgbot.keyboards.inline import *
from tgbot.misc.states import MainMenu, Contract, Check
from tgbot.services.get_random import random_sample


async def start(m: Message):
    await m.answer(f"Assalomu alaykum {m.from_user.full_name} 👋\n"
                  f"Sizni Supprot Samarkand Botida ko'rib turganimizdan mamnunmiz\n\n"
                  f"Iltimos pastdagi tugmalar orqali kerakli bo'limni tanlang👇", reply_markup=menu_kb)
    await MainMenu.get_menu.set()


async def contract(c: CallbackQuery, config):
    kb, count = await contracts_kb(c.from_user.id, config)
    await c.message.edit_text(f"Sizda {count} ta proekt mavjud 📋\nQaysi biriga shartnoma qilishni istaysiz?",
                              reply_markup=kb)
    await Contract.get_contract.set()


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


async def get_contract(c: CallbackQuery, state: FSMContext):
    number = await random_sample()
    await state.update_data(number=number, id=c.data)
    await c.message.edit_text(f"Dogovor raqam olindi ✅\nSizning dogovor raqamingiz:\n\n{number}",
                              reply_markup=contract_conf_kb)
    await Contract.next()


async def get_conf(c: CallbackQuery):
    await c.message.edit_text("Iltimos INN ni kiriting")
    await Contract.next()


async def get_inn(m: Message, state: FSMContext, config):
    data = await state.get_data()
    res = await get_contracts(data['id'], "good", config)
    await m.answer(f"Dogovor raqam:\n{data['number']}\nKorxona INN si:\n{m.text}\nProekt nomi:\n{res[0]['name']}\n"
                   f"keltirilgan ma'lumotlarni\ntasdiqlaysizmi?", reply_markup=contract_conf_kb)
    await Contract.next()


async def get_last_conf(c: CallbackQuery):
    await c.message.edit_text("Qabul qilindi ✅", reply_markup=menu_kb)
    await MainMenu.get_menu.set()


async def back(c: CallbackQuery):
    await c.message.edit_text("Bosh menu", reply_markup=menu_kb)
    await MainMenu.get_menu.set()


def register_admin(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start"], state="*", is_admin=True)
    dp.register_callback_query_handler(contract, Text(equals="contract"), state=MainMenu.get_menu, is_admin=True)
    dp.register_callback_query_handler(check, Text(equals="check"), state=MainMenu.get_menu, is_admin=True)
    dp.register_callback_query_handler(get_check_contract, state=Check.get_contract, is_admin=True)
    dp.register_callback_query_handler(get_contract, BackFilter(), state=Contract.get_contract, is_admin=True)
    dp.register_callback_query_handler(get_conf, BackFilter(),  state=Contract.get_conf, is_admin=True)
    dp.register_message_handler(get_inn, state=Contract.get_inn, is_admin=True)
    dp.register_message_handler(get_check_inn, state=Check  .get_inn, is_admin=True)
    dp.register_callback_query_handler(get_last_conf, BackFilter(), state=Contract.get_last_conf, is_admin=True)
    dp.register_callback_query_handler(back, state="*", is_admin=True)
