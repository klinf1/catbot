from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.const import EAT_PREY, LEAVE_PREY, TAKE_PREY, VIEW_INVENTORY, CLEAR_INVENTORY
from db.inventory import InventoryManager


def get_hunt_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("Оставить", callback_data=LEAVE_PREY),
            InlineKeyboardButton("Съесть", callback_data=EAT_PREY),
            InlineKeyboardButton("Забрать с собой", callback_data=TAKE_PREY),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_base_inv_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("Просмотреть инвентарь", callback_data=VIEW_INVENTORY),
            InlineKeyboardButton("Очистить инвентарь", callback_data=CLEAR_INVENTORY)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_view_inv_keyboard(no: int) -> InlineKeyboardMarkup:
    inv = InventoryManager().get_char_inventory(no)
    keyboard = [[]]
    for i in inv:
        keyboard[0].append(InlineKeyboardButton(i.name, callback_data=i.no))
    return InlineKeyboardMarkup(keyboard)


def get_single_inv_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("Выбросить", callback_data=LEAVE_PREY),
            InlineKeyboardButton("Съесть", callback_data=EAT_PREY),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)