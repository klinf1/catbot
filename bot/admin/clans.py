from telegram import Update
from telegram.ext import ContextTypes

from bot.command_base import CommandBase
from db import Clans
from db.characters import DbCharacterConfig
from db.clans import DbClanConfig
from utils import prepare_for_db


class ClanCommandHandler(CommandBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.clan_db = DbClanConfig()
        self.char_db = DbCharacterConfig()

    async def add_clan(self):
        params_dict = {}
        if "\n" in self.text:
            name, params_str = self.text.strip().split("\n", 1)
            params_list = params_str.strip().split("\n")
            for item in params_list:
                col, value = prepare_for_db(item.strip().split(":", 1))
                if col and value and col in Clans.attrs():
                    params_dict.update({col: value})
        else:
            name = self.text.strip()
            params_str = ""
        if not name:
            await self.bot.send_message(self.chat_id, f"Вы не указали название клана!")
            return
        params_dict.update({"name": name.capitalize()})

        self.clan_db.add_new_clan(params_dict)
        if 'is_true_clan' in params_dict.keys() and params_dict.get('is_true_clan'):
            await self.context.bot.send_message(
                self.chat_id, f"Клан {name} добавлен успешно!"
            )
        else:
            await self.context.bot.send_message(
                self.chat_id, f"Территория {name} добавлена успешно!"
            )

    async def add_clan_help(self):
        attrs = "\n".join(Clans.attrs())
        text = (
            "Это комманда для создания нового клана! "
            "Необходимо через пробел ввести имя нового клана, и далее через перенос строки атрибуты в формате атрибут:значение\n"
        )
        text += f"Список атрибутов клана, которые можно задать:\n{attrs}"
        text += f"\nОбязательно указать имя клана. В дальнейшем можно указать лидера с помощью /appoint_leader"
        text += f"\nЕсли не указать is_true_clan, то будет создана отдельная территория, а не клан."
        await self.context.bot.send_message(self.chat_id, text)

    async def view_all_clans(self):
        clan_list = self.clan_db.get_all_clans()
        print(f" clan {clan_list}")
        await self.view_list_from_db(clan_list)

    async def view_all_territories(self):
        terr_list = self.clan_db.get_all_territories()
        print(f"terr {terr_list}")
        await self.view_list_from_db(terr_list)

    async def delete_clan(self):
        clan_name = self.text.capitalize()
        clan = self.clan_db.get_clan_by_name(clan_name)
        self.clan_db.delete_clan_by_no(clan.no)
        await self.bot.send_message(
            self.chat_id, f"Клан или территория {clan.name} удалена успешно."
        )

    async def appoint_leader(self):
        leader, clan_name = self.text.split(";", 1)
        char = self.char_db.get_char_by_name(leader.strip())
        if not char:
            await self.bot.send_message(
                self.chat_id, f"Персонаж с именем {leader} не найден."
            )
            return
        clan = self.clan_db.get_real_clan(clan_name.strip())
        if not clan:
            await self.bot.send_message(
                self.chat_id, f"Клан под названием {clan_name} не найден."
            )
            return
        self.clan_db.appoint_leader(clan, char.no)
        await self.bot.send_message(
            self.chat_id, f"Новый лидер {char.name} для клана {clan} добавлен успешно."
        )

    async def appoint_leader_help(self):
        text = """Это команда для назначения лидера клана! Нужно ввести /appoint_leader [Имя лидера];[Название клана]."""
        await self.context.bot.send_message(self.chat_id, text)

    async def remove_leader(self):
        clan = self.text.capitalize()
        self.clan_db.remove_leader(clan)
        await self.bot.send_message(
            self.chat_id, f"Лидер для клана {clan} удален успешно."
        )
