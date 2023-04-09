from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.db.db_api import get_contracts

back_btn = InlineKeyboardButton("Orqaga 🔙", callback_data="back")

back_kb = InlineKeyboardMarkup(row_width=1).add(back_btn)

menu_kb = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Dogovor raqam olish", callback_data="contract"),
    InlineKeyboardButton("Sertifikat olish", callback_data="Certificate"),
    InlineKeyboardButton("Joriy shartnomani tekshirish", callback_data="check"))

contract_conf_kb = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Tasdiqlash qilish", callback_data="confirm"),
    InlineKeyboardButton("Bekor qilish", callback_data="back"))


async def contracts_kb(user_id, config):
    kb = InlineKeyboardMarkup(row_width=1)
    contracts = await get_contracts(user_id, "user", config)
    for contract in contracts:
        kb.insert(InlineKeyboardButton(contract["name"], callback_data=contract["id"]))
    kb.insert(back_btn)
    return kb, len(contracts)

