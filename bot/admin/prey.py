from telegram import Update
from telegram.ext import ContextTypes

from bot.command_base import CommandBase
from db import Prey
from db.clans import DbClanConfig
from db.prey import DbPreyConfig
from utils import prepare_for_db


class PreyCommandHandler(CommandBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.prey_db = DbPreyConfig()
        self.terr_db = DbClanConfig()

    async def add_prey(self):
        params_dict = {}
        name, params_str = self.text.strip().split("\n", 1)
        params_list = params_str.strip().split("\n")
        params_dict.update({"name": name.capitalize()})
        for item in params_list:
            col, value = prepare_for_db(item.strip().split(":", 1))
            if (
                col and value and (col in Prey.attrs() or (col + "*") in Prey.attrs())
            ):  # TODO: убрать ебучий костыль
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
        text += f"\nЕсли не указать территорию дичи, то она будет встречаться везде."
        await self.context.bot.send_message(self.chat_id, text)

    async def view_all_prey(self):
        all_prey = self.prey_db.get_all_prey()
        await self.view_list_from_db(all_prey)

    async def delete_prey(self):
        prey = self.prey_db.get_prey_by_name(self.text.capitalize())
        self.prey_db.delete(prey)
        await self.context.bot.send_message(self.chat_id, f'Дичь {self.text.capitalize()} удалена успешно.')

    async def delete_prey_help(self):
        text = "Это команда для удаления одного вида дичи. Необходимо ввести название через пробел."
        await self.context.bot.send_message(self.chat_id, text)

    async def edit_prey(self):
        params_dict = {}
        name, params_str = self.text.strip().split("\n", 1)
        params_list = params_str.strip().split("\n")
        for item in params_list:
            col, value = prepare_for_db(item.strip().split(":", 1))
            if col and value and col in Prey.attrs():
                if col == "territory":
                    self.bot.send_message(
                        self.chat_id,
                        f"Для редактирования территорий проживания дичи воспользуйтесь соответствующими коммандами.",
                    )
                    continue
                params_dict.update({col.strip(): value.strip()})
        self.prey_db.edit_prey_by_name(name.capitalize(), params_dict)
        upd_prey = self.prey_db.get_prey_by_name(name)
        self.bot.send_message(self.chat_id, str(upd_prey))

    async def new_prey_territory(self):
        name, terr = self.text.strip().split("\n")
        prey = self.prey_db.get_prey_by_name(name)
        territory = self.terr_db.get_clan_by_name(terr)
        self.prey_db.new_prey_territory(prey, territory)
        await self.context.bot.send_message(
            self.chat_id,
            f"Территория проживания {territory.name} для дичи {prey.name} добавлена успешно.",
        )

    async def remove_prey_territory(self):
        name, terr = self.text.strip().split("\n")
        prey = self.prey_db.get_prey_by_name(name)
        territory = self.terr_db.get_clan_by_name(terr)
        self.prey_db.remove_prey_terr(prey, territory)
        await self.context.bot.send_message(
            self.chat_id,
            f"Территория проживания {territory.name} для дичи {prey.name} удалена успешно.",
        )

    async def reset_prey_territories(self):
        name, terr = self.text.strip().split("\n")
        prey = self.prey_db.get_prey_by_name(name)
        self.prey_db.reset_territories(prey, terr)
        self.prey_db.refresh()
        prey = self.prey_db.get_prey_by_name(name)
        await self.context.bot.send_message(
            self.chat_id, f"Обновленная дичь: {str(prey)}"
        )
