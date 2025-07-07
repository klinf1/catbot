from telegram import Update
from telegram.ext import ContextTypes

from db import Characters
from db.characters import DbCharacterConfig
from db.decorators import admin_command
from db.players import DbPlayerConfig
from logs.logs import main_logger as logger
from utils import prepare_for_db


@admin_command
async def add_char(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.replace("/add_char", "")
        params_dict = {}
        name, params_str = text.strip().split("\n", 1)
        params_list = params_str.strip().split("\n")
        for item in params_list:
            col, val = prepare_for_db(item.strip().split(":", 1))
            if col and val and col in Characters.attrs():
                params_dict.update({col: val})
        params_dict.update({"name": name.capitalize()})
        DbCharacterConfig().add_character(params_dict)
        await context.bot.send_message(update.effective_chat.id, "Character added!")
    except Exception as err:
        await context.bot.send_message(
            update.effective_chat.id, "Ошибка. Тагните Клинфа."
        )
        logger.error(err)


@admin_command
async def add_char_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        attrs = "\n".join(Characters.attrs())
        text = (
            "Это комманда для создания нового персонажа! "
            "Необходимо через пробел ввести имя нового персонажа, и далее через перенос строки атрибуты в формате атрибут:значение\n"
        )
        text += f"Список атрибутов персонажа, которые можно задать:\n{attrs}"
        await context.bot.send_message(update.effective_chat.id, text)
    except Exception as err:
        await context.bot.send_message(
            update.effective_chat.id, "Ошибка. Тагните Клинфа."
        )
        logger.error(err)


@admin_command
async def view_chars_by_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.replace("/view_chars_by_player", "").strip()
        chat_id = DbPlayerConfig().get_player_by_username(text).chat_id
        chars = DbCharacterConfig().get_chars_for_player(chat_id)
        res = ""
        for char in chars:
            res = "\n".join([res, str(char), "______"])
        await context.bot.send_message(update.effective_chat.id, res)
    except Exception as err:
        await context.bot.send_message(
            update.effective_chat.id, "Ошибка. Тагните Клинфа."
        )
        logger.error(err)


@admin_command
async def view_all_chars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chars = DbCharacterConfig().get_all_chars()
        res = ""
        for char in chars:
            res = "\n".join([res, str(char), "______"])
        await context.bot.send_message(update.effective_chat.id, res)
    except Exception as err:
        await context.bot.send_message(
            update.effective_chat.id, "Ошибка. Тагните Клинфа."
        )
        logger.error(err)
