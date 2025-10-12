from sqlalchemy.exc import IntegrityError
from telegram import Update
from telegram.ext import ContextTypes

from bot.command_base import CommandBase
from db import Characters
from db.characters import DbCharacterConfig
from db.decorators import superuser_command
from db.players import DbPlayerConfig
from exceptions import NotRealClanError
from logs.logs import main_logger
from utils import prepare_for_db


class CharacterCommandHandler(CommandBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.char_config = DbCharacterConfig()
        self.player_db = DbPlayerConfig()

    async def add_char(self):
        params_dict = {}
        name, params_str = self.text.strip().split("\n", 1)
        params_list = params_str.strip().split("\n")
        for item in params_list:
            col, val = prepare_for_db(item.strip().split(":", 1))
            if (
                col
                and val
                and col in Characters.attrs()
                or col + "*" in Characters.attrs()
            ):
                params_dict.update({col: val})
        params_dict.update({"name": name.capitalize()})
        if self.char_config.get_char_by_name(name.capitalize()):
            await self.bot.send_message(
                self.chat_id, f"Персонаж с именем {name} уже существует!"
            )
            main_logger.info(f"Попытка создания кота с одинаковым именем {name}")
            return
        try:
            self.char_config.add_character(params_dict)
            await self.context.bot.send_message(self.chat_id, "Character added!")
        except NotRealClanError:
            await self.bot.send_message(
                self.chat_id, f"Не найден клан {params_dict['clan_no']}"
            )
        except IntegrityError as err:
            main_logger.info(f"Ошибка создания персонажа: {err}")
            await self.bot.send_message(
                self.chat_id, "Ошибка создания персонажа! Проверьте параметры!"
            )

    async def add_char_help(self):
        attrs = "\n".join(Characters.attrs())
        text = (
            "Это комманда для создания нового персонажа! "
            "Необходимо через пробел ввести имя нового персонажа, и далее через перенос строки атрибуты в формате атрибут:значение\n"
        )
        text += f"Список атрибутов персонажа, которые можно задать:\n{attrs}"
        text += "Если не указать характеристику, то ее значение будет равно 0"
        await self.context.bot.send_message(self.chat_id, text)

    async def view_chars_by_player(self):
        chat_id = self.player_db.get_player_by_username(self.text).chat_id
        chars = self.char_config.get_chars_for_player(chat_id)
        if chars:
            await self.view_list_from_db(chars)
        else:
            await self.bot.send_message(self.chat_id, 'У этого игрока нет персонажей!')

    async def view_all_chars(self):
        chars = self.char_config.get_all_chars()
        if chars:
            await self.view_list_from_db(chars)
        else:
            await self.bot.send_message(self.chat_id, 'В игре нет персонажей!')

    async def edit_char(self):
        params_dict = {}
        name, params_str = self.text.strip().split("\n", 1)
        params_list = params_str.strip().split("\n")
        for item in params_list:
            col, val = prepare_for_db(item.strip().split(":", 1))
            if col and val and col in Characters.attrs() or col.lower() == "name":
                params_dict.update({col: val})
        # params_dict.update({"name": name.capitalize()})
        try:
            self.char_config.edit_character(name, params_dict)
            new_char = self.char_config.get_char_by_name(
                params_dict.get("name") or name
            )
            await self.context.bot.send_message(self.chat_id, str(new_char))
        except NotRealClanError:
            await self.bot.send_message(
                self.chat_id, f"Не найден клан {params_dict['clan_no']}"
            )
    
    async def freeze(self):
        name = self.text.strip().capitalize()
        self.char_config.edit_freeze_char_by_name(name)
        await self.bot.send_message(self.chat_id, f'Персонаж {name} заморожен.', reply_to_message_id=self.update.message.id)
    
    async def unfreeze(self):
        name = self.text.strip().capitalize()
        self.char_config.edit_freeze_char_by_name(name, False)
        await self.bot.send_message(self.chat_id, f'Персонаж {name} разморожен.', reply_to_message_id=self.update.message.id)
    
    @superuser_command
    async def kill(self):
        name = self.text
        self.char_config.edit_death_char_by_name(name, True)
        await self.bot.send_message(self.chat_id, f'Персонаж {name} убит.', reply_to_message_id=self.update.message.id)
    
    @superuser_command
    async def resurrect(self):
        name = self.text
        self.char_config.edit_death_char_by_name(name, False)
        await self.bot.send_message(self.chat_id, f'Персонаж {name} воскрешен.', reply_to_message_id=self.update.message.id)
