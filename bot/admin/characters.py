from telegram import Update
from telegram.ext import ContextTypes

from bot.command_base import CommandBase
from db import Characters
from db.characters import DbCharacterConfig
from db.players import DbPlayerConfig
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
            if col and val and col in Characters.attrs():
                params_dict.update({col: val})
        params_dict.update({"name": name.capitalize()})
        self.char_config.add_character(params_dict)
        await self.context.bot.send_message(self.chat_id, "Character added!")

    async def add_char_help(self):
        attrs = "\n".join(Characters.attrs())
        text = (
            "Это комманда для создания нового персонажа! "
            "Необходимо через пробел ввести имя нового персонажа, и далее через перенос строки атрибуты в формате атрибут:значение\n"
        )
        text += f"Список атрибутов персонажа, которые можно задать:\n{attrs}"
        await self.context.bot.send_message(self.chat_id, text)

    async def view_chars_by_player(self):
        chat_id = self.player_db.get_player_by_username(self.text).chat_id
        chars = self.char_config.get_chars_for_player(chat_id)
        await self.view_list_from_db(chars)

    async def view_all_chars(self):
        chars = self.char_config.get_all_chars()
        await self.view_list_from_db(chars)
