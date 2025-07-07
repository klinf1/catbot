from telegram import Update
from telegram.ext import ContextTypes

from db import InjuryStat
from db.decorators import admin_command
from db.injuries import DbInjuryConfigure
from logs.logs import main_logger as logger
from utils import prepare_for_db


@admin_command
async def add_injury(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.replace("/add_injury", "").strip()
        params_dict = {}
        name, params_str = text.strip().split("\n", 1)
        params_list = params_str.strip().split("\n")
        for item in params_list:
            col, value = prepare_for_db(item.strip().split(":", 1))
            params_dict.update({col.strip(): value.strip()})
        DbInjuryConfigure().add_new_injury(name, params_dict)
    except Exception as err:
        await context.bot.send_message(
            update.effective_chat.id, "Ошибка. Тагните Клинфа."
        )
        logger.error(err)


@admin_command
async def add_injury_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attrs = "\n".join(InjuryStat.attrs())
    text = (
        "Это комманда для добавления нового ранения! "
        "Необходимо через пробел ввести его название, и далее через перенос строки характеристики в формате характеристика:штраф\n"
        f"Список характеристик, которые можно задать:\n{attrs}"
        "\nВсе штрафы должны быть меньше 0."
    )
    await context.bot.send_message(update.effective_chat.id, text)
