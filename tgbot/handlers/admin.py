from datetime import date

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from tgbot.db.db_api import get_projects, get_agent, create_contract, check_contract, get_project_db
from tgbot.filters.back import BackFilter
from tgbot.keyboards.inline import *
from tgbot.misc.states import MainMenu, Project, Check, Certificate, Send
from tgbot.services.counter import count
from tgbot.services.didox import didox_create_doc
from tgbot.services.pdf import pdf_create


async def start(m: Message):
    await m.answer(f"Assalomu alaykum {m.from_user.full_name} 👋\n"
                   f"Sizni Supprot Samarkand Botida ko'rib turganimizdan mamnunmiz\n\n"
                   f"Iltimos pastdagi tugmalar orqali kerakli bo'limni tanlang👇", reply_markup=menu_kb)
    await MainMenu.get_menu.set()


async def send(c: CallbackQuery):
    await c.message.edit_text("Iltimos kerakli faylni yuboring 📁", reply_markup=back_kb)
    await Send.get_file.set()


async def get_file(m: Message, state: FSMContext):
    await state.update_data(file=m.document.file_id)
    await m.answer("Iltimos korxonaning INN sini kiriting 📌", reply_markup=back_kb)
    await Send.next()


async def get_inn_send(m: Message, state: FSMContext, config):
    mes = await m.answer("⏳")
    data = await state.get_data()
    doc = await m.bot.download_file_by_id(data["file"], destination_dir="files")
    res = await didox_create_doc(config, doc.name, "Shartnoma", m.text)
    await mes.edit_text("Dogovor muvofaqqiyatli qabul qilindi ✅\n"
                        "Botni ishlatishni davom ettirish uchun pastdagi tugmachalardan foydalaning 👇",
                        reply_markup=menu_kb)
    await MainMenu.get_menu.set()


async def project(c: CallbackQuery, config):
    projects = await get_projects(c.from_user.id, config)
    await c.message.edit_text(f"Sizda {len(projects)} ta proekt mavjud 📋\nQaysi biriga shartnoma qilishni istaysiz?",
                              reply_markup=contracts_kb(projects))
    await Project.get_project.set()


async def get_project(c: CallbackQuery, state: FSMContext, config):
    counter, agent = await count(config), await get_agent(config, c.from_user.id)
    number = f"{counter}/{agent['uniq']} от {date.today().strftime('%d.%m.%Y')}"
    await state.update_data(number=number, name=c.data.split("_")[1], id=c.data.split("_")[0])
    await c.message.edit_text(f"Dogovor raqam olindi ✅\nSizning dogovor raqamingiz:\n\n<b>{number}</b>",
                              reply_markup=contract_conf_kb)
    await Project.next()


async def get_conf(c: CallbackQuery):
    await c.message.edit_text("Iltimos dogovor tuzilayotgan korxonaning INN manzilini kiriting ✍️")
    await Project.next()


async def get_inn(m: Message, state: FSMContext):
    data = await state.get_data()
    await m.answer(
        f"Dogovor raqam:\n[{data['number']}]✅\nKorxona INN si:\n[{m.text}]✅\nProekt nomi:\n[{data['name']}]✅\n"
        f"Keltirilgan ma’lumotlarni qabul qilish uchun pastdagi tugmalardan foydalaning 👇",
        reply_markup=contract_conf_kb)
    await state.update_data(inn=m.text)
    await Project.next()


async def get_last_conf(c: CallbackQuery, state: FSMContext, config):
    await c.message.edit_text("⏳")
    data = await state.get_data()
    await create_contract(config, project=data['id'], agent=c.from_user.id, inn=data['inn'], code=data['number'])
    pdf_create(data['number'], c.from_user.id)
    await didox_create_doc(config, f"{c.from_user.id}.pdf", data["number"], data["inn"])
    await c.message.edit_text("Dogovor muvofaqqiyatli qabul qilindi ✅\n"
                              "Botni ishlatishni davom ettirish uchun pastdagi tugmachalardan foydalaning 👇",
                              reply_markup=menu_kb)
    await MainMenu.get_menu.set()


async def check(c: CallbackQuery, config):
    projects = await get_projects(c.from_user.id, config)
    await c.message.edit_text(f"Sizda {len(projects)} ta proekt mavjud 📋\nQaysi birini tekshirishni istaysiz?",
                              reply_markup=contracts_kb(projects))
    await Check.get_contract.set()


async def get_check_contract(c: CallbackQuery, state: FSMContext):
    await state.update_data(name=c.data.split("_")[1], id=c.data.split("_")[0])
    await c.message.edit_text(
        "Qaysi korxonaning shartnomasini tekshirmoqchi bo’lsangiz, ushbu korxonaning INN raqamini kiriting ✍️")
    await Check.next()


async def get_check_inn(m: Message, state: FSMContext, config):
    data = await state.get_data()
    res = await check_contract(config, project=data["id"], inn=m.text)
    if res["status"] == "Not Found":
        await m.answer("Ushbu korxonada tuzilgan dogovorlar topilmadi ❌", reply_markup=menu_kb)
    elif res["status"]:
        await m.answer("Ushbu do'konda imzolanmay\nqolgan shartnoma mavjud emas", reply_markup=menu_kb)
    elif not res["status"]:
        await m.answer(f"Ushbu do'kon uchun {res['number']} shartnoma imzolanmay qolgan", reply_markup=menu_kb)
    return await MainMenu.get_menu.set()


async def certificate(c: CallbackQuery, config):
    projects = await get_projects(c.from_user.id, config)
    await c.message.edit_text(f"Sizda {len(projects)} ta proekt mavjud 📋\nQaysi birini sertifikatini olishni istaysiz?",
                              reply_markup=contracts_kb(projects))
    await Certificate.get_certificate.set()


async def get_certificate(c: CallbackQuery, config):
    certificate_project = await get_project_db(c.data.split("_")[0], config)
    if certificate_project["file"] is None:
        return await c.answer("Sertifikat qo'shilmagan")
    await c.message.delete()
    print(certificate_project)
    await c.message.answer_document(document=certificate_project["file"], reply_markup=back_kb)


async def back(c: CallbackQuery):
    if c.data == "back":
        await c.message.edit_text("Bosh menu", reply_markup=menu_kb)
    else:
        await c.message.delete()
        await c.message.answer("Bosh menu", reply_markup=menu_kb)
    return await MainMenu.get_menu.set()


def register_admin(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start"], state="*", is_admin=True)
    dp.register_callback_query_handler(project, Text(equals="contract"), state=MainMenu.get_menu, is_admin=True)
    dp.register_callback_query_handler(send, Text(equals="send"), state=MainMenu.get_menu, is_admin=True)
    dp.register_callback_query_handler(check, Text(equals="check"), state=MainMenu.get_menu, is_admin=True)
    dp.register_callback_query_handler(certificate, Text(equals="Certificate"), state=MainMenu.get_menu, is_admin=True)
    dp.register_message_handler(get_file, state=Send.get_file, is_admin=True, content_types="document")
    dp.register_message_handler(get_inn_send, state=Send.get_inn, is_admin=True)
    dp.register_callback_query_handler(get_certificate, BackFilter(), state=Certificate.get_certificate, is_admin=True)
    dp.register_callback_query_handler(get_check_contract, BackFilter(), state=Check.get_contract, is_admin=True)
    dp.register_callback_query_handler(get_project, BackFilter(), state=Project.get_project, is_admin=True)
    dp.register_callback_query_handler(get_conf, BackFilter(), state=Project.get_conf, is_admin=True)
    dp.register_message_handler(get_inn, state=Project.get_inn, is_admin=True)
    dp.register_message_handler(get_check_inn, state=Check.get_inn, is_admin=True)
    dp.register_callback_query_handler(get_last_conf, BackFilter(), state=Project.get_last_conf, is_admin=True)
    dp.register_callback_query_handler(back, state="*", is_admin=True)
