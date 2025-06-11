from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

back_btn = InlineKeyboardButton("Назад 🔙", callback_data="back")

back_kb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Назад 🔙", callback_data="backs"))


def menu_kb(is_boss):
    menu_btn = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("Получить номер договора 🔗", callback_data="contract"),
        InlineKeyboardButton("Получить сертификат 📄", callback_data="certificate"),
        InlineKeyboardButton("Проверить текущий договор ☑️", callback_data="check"),
        InlineKeyboardButton("История договоров ⏳", callback_data="history"))
    if is_boss:
        menu_btn.add(InlineKeyboardButton("Отправить договор 📧", callback_data="send"))
        menu_btn.add(InlineKeyboardButton("Процентный договор 💯", callback_data="percent"))
    return menu_btn


contract_conf_kb = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Подтвердить ✅", callback_data="confirm"),
    InlineKeyboardButton("Отменить ❌", callback_data="back"))

doc_type_kb = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Отсрочка 📅", callback_data="Отсрочка"),
    InlineKeyboardButton("Предоплата 💸", callback_data="Предоплата"),
    back_btn)

type_kb = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Акт сверка", callback_data="Акт сверка"),
    InlineKeyboardButton("Доп соглашение", callback_data="Доп соглашение"),
    InlineKeyboardButton("Договор", callback_data="Договор"),
    InlineKeyboardButton("Сертификат", callback_data="Сертификат"),
    InlineKeyboardButton("Спецификация", callback_data="Спецификация"),
    back_btn)


def contracts_kb(projects, percent=False):
    kb = InlineKeyboardMarkup(row_width=1)
    for project in projects:
        kb.insert(InlineKeyboardButton(project["name"],
                                       callback_data=f"{project['id']}_{project['name']}" if not percent else f"{project['id']}_{project['uniq']}_{project['name']}"))
    kb.insert(back_btn)
    return kb
