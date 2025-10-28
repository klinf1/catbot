from apscheduler.job import Job
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.const import (CARRY_PREY, CLEAR_INVENTORY, EAT_PREY, LEAVE_PREY, TAKE_PREY,
                       VIEW_INVENTORY)
from db.inventory import InventoryManager
from db.herbs import HerbConfig
from db.prey import DbPreyConfig


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
            InlineKeyboardButton("Очистить инвентарь", callback_data=CLEAR_INVENTORY),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_view_inv_keyboard(no: int) -> InlineKeyboardMarkup:
    inv = InventoryManager().get_char_inventory(no)
    keyboard = [[]]
    for i in inv:
        type = i.type
        if type == 'prey':
            item = DbPreyConfig().get_prey_by_no(i.item)
            keyboard[0].append(InlineKeyboardButton(item.name, callback_data=f"Дичь:{item.no}"))
        elif type == 'herb':
            item = HerbConfig().get_herb_by_no(i.item)
            keyboard[0].append(InlineKeyboardButton(item.name, callback_data=f"Трава:{item.no}"))
    return InlineKeyboardMarkup(keyboard)


def get_single_inv_keyboard(clan_cat: bool = True) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("Выбросить", callback_data=LEAVE_PREY),
            InlineKeyboardButton("Съесть", callback_data=EAT_PREY),            
        ]
    ]
    if clan_cat is True:
        keyboard[0].append(InlineKeyboardButton("Унести в кучу", callback_data=CARRY_PREY))
    return InlineKeyboardMarkup(keyboard)


def get_job_keyboard(job_list: list[Job]) -> InlineKeyboardMarkup:
    keyboard = [[]]
    for job in job_list:
        keyboard[0].append(InlineKeyboardButton(job.name, callback_data=job.id))
    return InlineKeyboardMarkup(keyboard)
