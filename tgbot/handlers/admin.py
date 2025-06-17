from datetime import date, datetime

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from aiogram.types import InputFile

from tgbot.db.db_api import get_projects, get_agent, create_contract, check_contract, get_project_db, get_contracts
from tgbot.filters.back import BackFilter
from tgbot.filters.day import WeekdayFilter
from tgbot.keyboards.inline import *
from tgbot.misc.states import MainMenu, Project, Check, Certificate, Send, History, Percent
from tgbot.services.counter import count
from tgbot.services.didox import didox_create_doc, didox_get_token, get_info
from tgbot.services.pdf import pdf_create, pdf_create_percent, pdf_create_special


async def start(m: Message, config):
    user = await get_agent(config, m.from_user.id)
    await m.answer(f"Здравствуйте, {m.from_user.full_name} 👋\n"
                   f"Рады видеть вас в боте Support Samarkand\n\n"
                   f"Пожалуйста, выберите нужный раздел с помощью кнопок ниже 👇", reply_markup=menu_kb(user["is_boss"]))
    await MainMenu.get_menu.set()


async def send(c: CallbackQuery):
    await c.message.edit_text("Выберите нужный раздел 👇", reply_markup=type_kb)
    await Send.get_type.set()


async def get_type(c: CallbackQuery, state: FSMContext):
    await state.update_data(type=c.data)
    await c.message.edit_text("Пожалуйста, отправьте нужный файл 📁", reply_markup=back_kb)
    await Send.next()


async def get_file(m: Message, state: FSMContext):
    await state.update_data(file=m.document.file_id)
    await m.answer("Пожалуйста, введите ИНН организации 📌", reply_markup=back_kb)
    await Send.next()


async def get_inn_send(m: Message, state: FSMContext, config):
    await m.answer("⏳")
    data = await state.get_data()
    doc = await m.bot.download_file_by_id(data["file"], destination_dir="files")
    inn = await didox_create_doc(config, doc.name, data["type"], m.text)
    if not inn:
        return await m.answer("Введён неверный ИНН. Пожалуйста, проверьте и введите заново ❌", reply_markup=back_kb)
    user = await get_agent(config, m.from_user.id)
    await m.bot.send_document(chat_id=config.tg_bot.channel_id, document=data["file"],
                              caption=f"👤 Агент: {user['name']}\n🆔 Номер агента: {user['uniq']}\n📃 Тип договора: {data['type']}\n🗂 ИНН организации: {m.text}\n")
    await m.answer("Договор успешно принят ✅\n"
                   "Для продолжения работы с ботом используйте кнопки ниже 👇",
                   reply_markup=menu_kb(user["is_boss"]))
    await MainMenu.get_menu.set()


async def project(c: CallbackQuery, config):
    projects = await get_projects(c.from_user.id, config)
    await c.message.edit_text(f"У вас {len(projects)} проектов 📋\nС каким из них хотите заключить договор?",
                              reply_markup=contracts_kb(projects))
    await Project.get_project.set()


async def get_project(c: CallbackQuery, state: FSMContext, config):
    project_db = await get_project_db(c.data.split("_")[0], config)
    counter, agent = await count(config), await get_agent(config, c.from_user.id)
    key = f"-{agent['uniq']}"
    number = f"{counter}/{project_db['uniq']}{key if agent['uniq'] is not None else ''}"
    await state.update_data(number=number, name=c.data.split("_")[1], id=c.data.split("_")[0],
                            signature=project_db["signature"], is_special=project_db["is_special"])
    if project_db["is_special"]:
        await Project.next()
        return await c.message.edit_text(f"Номер договора получен ✅\nВаш номер договора:\n<b>{number}</b>"
                                         f"\nВыберите тип договора 📑", reply_markup=doc_type_kb)
    await c.message.edit_text(f"Номер договора получен ✅\nВаш номер договора:\n\n<b>{number}</b>",
                              reply_markup=contract_conf_kb)
    await Project.get_conf.set()


async def get_doc_type(c: CallbackQuery, state: FSMContext):
    await state.update_data(doc_pdf=c.data)
    await c.message.edit_text("Пожалуйста, введите ИНН организации, с которой заключается договор ✍️")
    await Project.get_inn.set()


async def get_conf(c: CallbackQuery):
    await c.message.edit_text("Пожалуйста, введите ИНН организации, с которой заключается договор ✍️")
    await Project.next()


async def get_inn(m: Message, state: FSMContext, config):
    token = await didox_get_token(config)
    res = await get_info(config, m.text, token['token'])
    if res["inn"] is None:
        return await m.answer("Введён неверный ИНН. Пожалуйста, проверьте и введите заново ❌", reply_markup=back_kb)
    data = await state.get_data()
    text = f"Номер договора:\n[{data['number']} от {datetime.now().strftime('%d.%m.%Y')}]✅\nИНН организации:\n[{m.text}]✅\nНазвание фирмы:\n[{res['shortName']}]✅\nНазвание проекта:\n[{data['name']}]✅\n"
    if data["is_special"]:
        text += f"Тип документа[{data['doc_pdf']}]✅\n"
    await m.answer(text, reply_markup=contract_conf_kb)
    await state.update_data(inn=m.text, company_info=res)
    await Project.next()


async def get_last_conf(c: CallbackQuery, state: FSMContext, config):
    await c.message.edit_text("⏳")
    data = await state.get_data()
    user = await get_agent(config, c.from_user.id)
    text = f"👤 Агент: {user['name']}\n📥 Номер агента: {user['uniq']}\n🆔 Номер договора: {data['number']} от {datetime.now().strftime('%d.%m.%Y')}\n🗂 ИНН организации: {data['inn']}\n🏭 Название фирмы: {data['company_info']['shortName']}\n📃 Название проекта: {data['name']}"
    await create_contract(config, project=data['id'], agent=user['id'], firm=data['company_info']['shortName'],
                          inn=data['inn'], code=data['number'])
    if data["is_special"]:
        text += f"\n📑 Тип документа: {data['doc_pdf']}"
        pdf_create_special(data['number'], c.from_user.id, data['signature'], data['company_info'], data['doc_pdf'])
    else:
        pdf_create(data['number'], c.from_user.id, data['signature'], data['company_info'])
    await didox_create_doc(config, f"{c.from_user.id}.pdf", data["number"], data["inn"])
    await c.bot.send_document(chat_id=config.tg_bot.channel_id, document=InputFile(f"{c.from_user.id}.pdf"),
                              caption=text)
    await c.message.edit_text("Договор успешно принят ✅\n"
                              "Для продолжения работы с ботом используйте кнопки ниже 👇",
                              reply_markup=menu_kb(user["is_boss"]))
    await MainMenu.get_menu.set()


async def history(c: CallbackQuery, config):
    projects = await get_projects(c.from_user.id, config)
    await c.message.edit_text(f"У вас {len(projects)} проектов 📋\nКакой хотите просмотреть?",
                              reply_markup=contracts_kb(projects))
    await History.get_contract.set()


async def get_history_projects(c: CallbackQuery, config):
    res = await get_contracts(c.from_user.id, config)
    if len(res) == 0:
        return await c.answer("Созданные договоры не найдены ❌")
    await c.message.delete()
    text, counts = "", 0
    for i in res:
        if counts == 7:
            await c.message.answer(text)
            text, counts = "", 0
        counts += 1
        text += f"📄 Номер договора: {i['code']}\n🗂 ИНН организации: {i['inn']}\n🏭 Имя организации: {i['firm']}\n📅 Дата заключения: {i['created_at'][0:10]}\n\n"
    await c.message.answer(text, reply_markup=back_kb)


async def check(c: CallbackQuery, config):
    projects = await get_projects(c.from_user.id, config)
    await c.message.edit_text(f"У вас {len(projects)} проектов 📋\nКакой хотите проверить?",
                              reply_markup=contracts_kb(projects))
    await Check.get_contract.set()


async def get_check_contract(c: CallbackQuery, state: FSMContext):
    await state.update_data(name=c.data.split("_")[1], id=c.data.split("_")[0])
    await c.message.edit_text(
        "Введите ИНН той организации, договор которой вы хотите проверить ✍️")
    await Check.next()


async def get_check_inn(m: Message, state: FSMContext, config):
    data = await state.get_data()
    user = await get_agent(config, m.from_user.id)
    res = await check_contract(config, project=data["id"], inn=m.text)
    if res["status"] == "Not Found":
        await m.answer("Для этой организации договоры не найдены ❌", reply_markup=menu_kb(user["is_boss"]))
    elif res["status"]:
        await m.answer("Нет неподписанных договоров по этому магазину", reply_markup=menu_kb(user["is_boss"]))
    elif not res["status"]:
        await m.answer(f"По данному магазину есть неподписанный договор № {res['number']}",
                       reply_markup=menu_kb(user["is_boss"]))
    return await MainMenu.get_menu.set()


async def certificate(c: CallbackQuery, config):
    projects = await get_projects(c.from_user.id, config)
    await c.message.edit_text(f"У вас {len(projects)} проектов 📋\nДля какого хотите получить сертификат?",
                              reply_markup=contracts_kb(projects))
    await Certificate.get_certificate.set()


async def get_certificate(c: CallbackQuery, config):
    certificate_project = await get_project_db(c.data.split("_")[0], config)
    if certificate_project["file"] is None:
        return await c.answer("Сертификат не добавлен")
    await c.message.delete()
    await c.message.answer_document(document=certificate_project["file"], reply_markup=back_kb)


async def percent(c: CallbackQuery, config):
    projects = await get_projects(c.from_user.id, config)
    await c.message.edit_text(f"У вас {len(projects)} проектов 📋\nС каким из них хотите заключить договор?",
                              reply_markup=contracts_kb(projects, True))
    await Percent.get_project.set()


async def percent_get_project(c: CallbackQuery, state: FSMContext):
    await state.update_data(project_id=c.data.split("_")[0], project_uniq=c.data.split("_")[1],
                            project_name=c.data.split("_")[2])
    await c.message.edit_text("Отправьте процентную ставку %")
    await Percent.next()


async def get_percent(m: Message, state: FSMContext):
    if not m.text.isdigit():
        return await m.answer("Пожалуйста отправьте число! ❌")
    if not 1 <= int(m.text) <= 99:
        return await m.answer("Процент должен быть в районе от 1 до 99 ! ❌")
    await state.update_data(percent=m.text)
    await m.answer("Отправьте срок 📅")
    await Percent.next()


async def get_day(m: Message, state: FSMContext):
    if not m.text.isdigit():
        return await m.answer("Пожалуйста отправьте число! ❌")
    await state.update_data(day=m.text)
    await m.answer("Пожалуйста, введите ИНН организации, с которой заключается договор ✍️")
    await Percent.next()


async def get_inn_percent(m: Message, state: FSMContext, config):
    token = await didox_get_token(config)
    res = await get_info(config, m.text, token['token'])
    try:
        if res["inn"] is None:
            return await m.answer("Введён неверный ИНН. Пожалуйста, проверьте и введите заново ❌", reply_markup=back_kb)
    except:
        return await m.answer("Введён неверный ИНН. Пожалуйста, проверьте и введите заново ❌", reply_markup=back_kb)
    counter, agent = await count(config), await get_agent(config, m.from_user.id)
    data = await state.get_data()
    key = f"-{agent['uniq']}"
    number = f"{counter}/{data['project_uniq']}{key if agent['uniq'] is not None else ''}"
    await m.answer(
        f"Номер договора:\n[{number} от {datetime.now().strftime('%d.%m.%Y')}]✅\nИНН организации:\n[{m.text}]✅\nНазвание фирмы:\n[{res['shortName']}]✅\nНазвание проекта:\n[{data['project_name']}]✅\n"
        f"Для подтверждения используйте кнопки ниже 👇",
        reply_markup=contract_conf_kb)
    await state.update_data(inn=m.text, company_info=res, number=number)
    await Percent.next()


async def get_percent_confirm(c: CallbackQuery, state: FSMContext, config):
    await c.message.edit_text("⏳")
    data = await state.get_data()
    user = await get_agent(config, c.from_user.id)
    await create_contract(config, project=data['project_id'], agent=user['id'],
                          firm=data['company_info']['shortName'], inn=data['inn'], code=data['number'])
    pdf_create_percent(data['number'], c.from_user.id, data['signature'], data['company_info'], data['percent'],
                       data['day'])
    await didox_create_doc(config, f"{c.from_user.id}.pdf", data["number"], data["inn"])
    await c.bot.send_document(chat_id=config.tg_bot.channel_id, document=InputFile(f"{c.from_user.id}.pdf"), caption=
    f"👤 Агент: {user['name']}\n📥 Номер агента: {user['uniq']}\n🆔 Номер договора: {data['number']} от {datetime.now().strftime('%d.%m.%Y')}\n🗂 ИНН организации: {data['inn']}\n🏭 Название фирмы: {data['company_info']['shortName']}\n📃 Название проекта: {data['name']}")
    await c.message.edit_text("Договор успешно принят ✅\n"
                              "Для продолжения работы с ботом используйте кнопки ниже 👇",
                              reply_markup=menu_kb(user["is_boss"]))
    await MainMenu.get_menu.set()


async def back(c: CallbackQuery, state: FSMContext, config):
    user = await get_agent(config, c.from_user.id)
    if str(await state.get_state()) == "Project:get_conf" or str(await state.get_state()) == "Project.get_doc_type":
        data = await state.get_data()
        await c.bot.send_message(config.tg_bot.channel_id, f"Договор по номеру {data['number']} аннулирован")
    await c.message.delete()
    await c.message.answer("Главное меню", reply_markup=menu_kb(user["is_boss"]))
    return await MainMenu.get_menu.set()


def register_admin(dp: Dispatcher):
    dp.register_message_handler(start, WeekdayFilter(allow_weekdays=True), commands=["start"], state="*", is_admin=True)
    dp.register_callback_query_handler(project, WeekdayFilter(allow_weekdays=True), Text(equals="contract"),
                                       state=MainMenu.get_menu, is_admin=True)
    dp.register_callback_query_handler(percent, WeekdayFilter(allow_weekdays=True), Text(equals="percent"),
                                       state=MainMenu.get_menu, is_admin=True)
    dp.register_callback_query_handler(percent_get_project, WeekdayFilter(allow_weekdays=True),
                                       state=Percent.get_project, is_admin=True)
    dp.register_message_handler(get_percent, WeekdayFilter(allow_weekdays=True), state=Percent.get_percent,
                                is_admin=True)
    dp.register_message_handler(get_day, WeekdayFilter(allow_weekdays=True), state=Percent.get_day, is_admin=True)
    dp.register_message_handler(get_inn_percent, WeekdayFilter(allow_weekdays=True), state=Percent.get_inn,
                                is_admin=True)
    dp.register_callback_query_handler(get_percent_confirm, WeekdayFilter(allow_weekdays=True),
                                       state=Percent.get_last_conf, is_admin=True)
    dp.register_callback_query_handler(get_doc_type, WeekdayFilter(allow_weekdays=True), BackFilter(),
                                       state=Project.get_doc_type, is_admin=True)
    dp.register_callback_query_handler(send, WeekdayFilter(allow_weekdays=True),
                                       Text(equals="send"), state=MainMenu.get_menu, is_admin=True)
    dp.register_callback_query_handler(get_type, WeekdayFilter(allow_weekdays=True), BackFilter(), state=Send.get_type,
                                       is_admin=True)
    dp.register_callback_query_handler(check, WeekdayFilter(allow_weekdays=True), Text(equals="check"),
                                       state=MainMenu.get_menu, is_admin=True)
    dp.register_callback_query_handler(history, WeekdayFilter(allow_weekdays=True), Text(equals="history"),
                                       state=MainMenu.get_menu, is_admin=True)
    dp.register_callback_query_handler(get_history_projects, WeekdayFilter(allow_weekdays=True), BackFilter(),
                                       state=History.get_contract, is_admin=True)
    dp.register_callback_query_handler(certificate, WeekdayFilter(allow_weekdays=True), Text(equals="certificate"),
                                       state=MainMenu.get_menu, is_admin=True)
    dp.register_message_handler(get_file, WeekdayFilter(allow_weekdays=True), state=Send.get_file, is_admin=True,
                                content_types="document")
    dp.register_message_handler(get_inn_send, WeekdayFilter(allow_weekdays=True), state=Send.get_inn, is_admin=True)
    dp.register_callback_query_handler(get_certificate, WeekdayFilter(allow_weekdays=True), BackFilter(),
                                       state=Certificate.get_certificate, is_admin=True)
    dp.register_callback_query_handler(get_check_contract, WeekdayFilter(allow_weekdays=True), BackFilter(),
                                       state=Check.get_contract, is_admin=True)
    dp.register_callback_query_handler(get_project, WeekdayFilter(allow_weekdays=True), BackFilter(),
                                       state=Project.get_project, is_admin=True)
    dp.register_callback_query_handler(get_conf, WeekdayFilter(allow_weekdays=True), BackFilter(),
                                       state=Project.get_conf, is_admin=True)
    dp.register_message_handler(get_inn, WeekdayFilter(allow_weekdays=True), state=Project.get_inn, is_admin=True)
    dp.register_message_handler(get_check_inn, WeekdayFilter(allow_weekdays=True), state=Check.get_inn, is_admin=True)
    dp.register_callback_query_handler(get_last_conf, WeekdayFilter(allow_weekdays=True), BackFilter(),
                                       state=Project.get_last_conf, is_admin=True)
    dp.register_callback_query_handler(back, WeekdayFilter(allow_weekdays=True), state="*", is_admin=True)
