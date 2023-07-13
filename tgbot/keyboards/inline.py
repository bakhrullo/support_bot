from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

back_btn = InlineKeyboardButton("Orqaga 🔙", callback_data="back")

back_kb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Orqaga 🔙", callback_data="backs"))


def menu_kb(is_boss):
    menu_btn = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("Dogovor raqam olish 🔗", callback_data="contract"),
        InlineKeyboardButton("Sertifikat olish 📄", callback_data="Certificate"),
        InlineKeyboardButton("Joriy shartnomani tekshirish ☑️", callback_data="check"))
    if is_boss:
        menu_btn.add(InlineKeyboardButton("Shartnoma yuborish 📧", callback_data="send"))
    return menu_btn


contract_conf_kb = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Tasdiqlash ✅", callback_data="confirm"),
    InlineKeyboardButton("Bekor qilish ❌", callback_data="back"))

type_kb = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Аксиверка", callback_data="Аксиверка"),
    InlineKeyboardButton("Доп соглашения", callback_data="Доп соглашения"),
    InlineKeyboardButton("Договор", callback_data="Договор"),
    InlineKeyboardButton("Сертификат", callback_data="Сертификат"),
    InlineKeyboardButton("Спецификация", callback_data="Спецификация"),
    back_btn)


def contracts_kb(projects):
    kb = InlineKeyboardMarkup(row_width=1)
    for project in projects:
        kb.insert(InlineKeyboardButton(project["name"], callback_data=f"{project['id']}_{project['name']}"))
    kb.insert(back_btn)
    return kb
