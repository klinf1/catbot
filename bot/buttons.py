from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.const import EAT_PREY, LEAVE_PREY, TAKE_PREY


def get_hunt_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("Оставить", callback_data=LEAVE_PREY),
            InlineKeyboardButton("Съесть", callback_data=EAT_PREY),
            InlineKeyboardButton("Забрать с собой", callback_data=TAKE_PREY),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
