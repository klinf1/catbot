from telegram import Update
from telegram.ext import ContextTypes

from bot.command_base import CommandBase
from db import Prey
from db.prey import DbPreyConfig
from utils import prepare_for_db


class PreyCommandHandler(CommandBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.prey_db = DbPreyConfig()

    async def add_prey(self):
        params_dict = {}
        name, params_str = self.text.strip().split("\n", 1)
        params_list = params_str.strip().split("\n")
        params_dict.update({"name": name.capitalize()})
        for item in params_list:
            col, value = prepare_for_db(item.strip().split(":", 1))
            if col and value and col in Prey.attrs():
                params_dict.update({col.strip(): value.strip()})
        self.prey_db.add_new_prey(params_dict)
        await self.context.bot.send_message(
            self.chat_id, f"Дичь {name} добавлена успешно!"
        )

    async def add_prey_help(self):
        attrs = "\n".join(Prey.attrs())
        text = (
            "Это комманда для добавления нового вида дичи! "
            "Необходимо через пробел ввести его название, и далее через перенос строки атрибуты в формате атрибут:значение\n"
        )
        text += f"Список атрибутов дичи, которые можно задать:\n{attrs}"
        await self.context.bot.send_message(self.chat_id, text)

    async def view_all_prey(self):
        all_prey = self.prey_db.get_all_prey()
        await self.view_list_from_db(all_prey)

    async def delete_prey(self):
        prey = self.prey_db.get_prey_by_name(self.text.capitalize())
        self.prey_db.delete(prey)

    async def delete_prey_help(self):
        text = "Это команда для удаления одного вида дичи. Необходимо ввести название через пробел."
        await self.context.bot.send_message(self.chat_id, text)
