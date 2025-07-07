from telegram import Update
from telegram.ext import ContextTypes

from bot.command_base import CommandBase
from db import InjuryStat
from db.injuries import DbInjuryConfigure
from utils import prepare_for_db


class InjuryCommandHandler(CommandBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.injury_db = DbInjuryConfigure()

    async def add_injury(self):
        params_dict = {}
        name, params_str = self.text.strip().split("\n", 1)
        params_list = params_str.strip().split("\n")
        for item in params_list:
            col, value = prepare_for_db(item.strip().split(":", 1))
            params_dict.update({col.strip(): value.strip()})
        self.injury_db.add_new_injury(name, params_dict)

    async def add_injury_help(self):
        attrs = "\n".join(InjuryStat.attrs())
        text = (
            "Это комманда для добавления нового ранения! "
            "Необходимо через пробел ввести его название, и далее через перенос строки характеристики в формате характеристика:штраф\n"
            f"Список характеристик, которые можно задать:\n{attrs}"
            "\nВсе штрафы должны быть меньше 0."
        )
        await self.context.bot.send_message(self.chat_id, text)
