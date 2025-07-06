from telegram import Update
from telegram.ext import ContextTypes

from db import Prey
from db.decorators import admin_command
from db.prey import DbPreyConfig
from logs.logs import main_logger as logger
from utils import prepare_for_db


@admin_command
async def add_prey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.replace("/add_prey", "")
        params_dict = {}
        name, params_str = text.strip().split("\n", 1)
        params_list = params_str.strip().split("\n")
        params_dict.update({"name": name})
        for item in params_list:
            col, value = prepare_for_db(item.strip().split(":", 1))
            if col and value and col in Prey.attrs():
                params_dict.update({col.strip(): value.strip()})
        DbPreyConfig().add_new_prey(params_dict)
        await context.bot.send_message(
            update.effective_chat.id, f"Дичь {name} добавлена успешно!"
        )
    except Exception as err:
        await context.bot.send_message(
            update.effective_chat.id, "Ошибка. Тагните Клинфа."
        )
        logger.error(err)


@admin_command
async def add_prey_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attrs = "\n".join(Prey.attrs())
    text = (
        "Это комманда для добавления нового вида дичи! "
        "Необходимо через пробел ввести его название, и далее через перенос строки атрибуты в формате атрибут:значение\n"
    )
    text += f"Список атрибутов дичи, которые можно задать:\n{attrs}"
    await context.bot.send_message(update.effective_chat.id, text)


@admin_command
async def view_all_prey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        all_prey = DbPreyConfig().get_all_prey()
        res = ""
        for prey in all_prey:
            res = "\n".join([res, str(prey), "______"])
        await context.bot.send_message(update.effective_chat.id, res)
    except Exception as err:
        await context.bot.send_message(
            update.effective_chat.id, "Ошибка. Тагните Клинфа."
        )
        logger.error(err)
