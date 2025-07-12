from telegram import Update
from telegram.ext import ContextTypes

from bot.command_base import CommandBase
from db import Clans
from db.clans import DbClanConfig
from utils import prepare_for_db


class ClanCommandHandler(CommandBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.clan_db = DbClanConfig()

    async def add_clan(self):
        params_dict = {}
        name, params_str = self.text.strip().split("\n", 1)
        params_list = params_str.strip().split("\n")
        params_dict.update({"name": name.capitalize()})
        for item in params_list:
            col, value = prepare_for_db(item.strip().split(":", 1))
            if col and value and col in Clans.attrs():
                params_dict.update({col: value})
        self.clan_db.add_new_clan(params_dict)
        await self.context.bot.send_message(
            self.chat_id, f"Клан {name} добавлен успешно!"
        )

    async def add_clan_help(self):
        attrs = "\n".join(Clans.attrs())
        text = (
            "Это комманда для создания нового клана! "
            "Необходимо через пробел ввести имя нового клана, и далее через перенос строки атрибуты в формате атрибут:значение\n"
        )
        text += f"Список атрибутов клана, которые можно задать:\n{attrs}"
        await self.context.bot.send_message(self.chat_id, text)
