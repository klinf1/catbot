from telegram import Update
from telegram.ext import ContextTypes

from db import Clans
from db.clans import DbClanConfig
from db.decorators import admin_command
from logs.logs import main_logger as logger
from utils import prepare_for_db


@admin_command
async def add_clan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.replace("/add_clan", "")
        params_dict = {}
        name, params_str = text.strip().split("\n", 1)
        params_list = params_str.strip().split("\n")
        params_dict.update({"name": name})
        for item in params_list:
            col, value = prepare_for_db(item.strip().split(":", 1))
            if col and value and col in Clans.attrs():
                params_dict.update({col: value})
        DbClanConfig().add_new_clan(params_dict)
        await context.bot.send_message(
            update.effective_chat.id, f"Клан {name} добавлен успешно!"
        )
    except Exception as err:
        await context.bot.send_message(
            update.effective_chat.id, "Ошибка. Тагните Клинфа."
        )
        logger.error(err)


@admin_command
async def add_clan_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        attrs = "\n".join(Clans.attrs())
        text = (
            "Это комманда для создания нового клана! "
            "Необходимо через пробел ввести имя нового клана, и далее через перенос строки атрибуты в формате атрибут:значение\n"
        )
        text += f"Список атрибутов клана, которые можно задать:\n{attrs}"
        await context.bot.send_message(update.effective_chat.id, text)
    except Exception as err:
        await context.bot.send_message(
            update.effective_chat.id, "Ошибка. Тагните Клинфа."
        )
        logger.error(err)
