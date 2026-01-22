from sqlalchemy.exc import IntegrityError
from telegram import Update
from telegram.ext import ContextTypes

from bot.command_base import CommandBase
from db import Characters
from db.characters import DbCharacterConfig
from db.decorators import superuser_command
from db.players import DbPlayerConfig
from exceptions import CharNotFound, NotRealClanError
from logs.logs import main_logger
from utils import prepare_for_db


class CharacterCommandHandler(CommandBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.char_config = DbCharacterConfig(self.user.username)
        self.player_db = DbPlayerConfig()

    async def add_char(self):
        params_dict = {}
        name, params_str = self.text.strip().split("\n", 1)
        params_list = params_str.strip().split("\n")
        for item in params_list:
            col, val = prepare_for_db(item.strip().split(":", 1))
            if col and val and col in Characters.attrs() or col + "*" in Characters.attrs():
                params_dict.update({col: val})
        params_dict.update({"name": name.capitalize()})
        if self.char_config.get_char_by_name(name.capitalize()):
            await self.bot.send_message(self.chat_id, f"Персонаж с именем {name} уже существует!")
            main_logger.info(f"Попытка создания кота с одинаковым именем {name}")
            return
        try:
            self.char_config.add_character(params_dict)
            await self.context.bot.send_message(self.chat_id, "Character added!")
        except NotRealClanError:
            await self.bot.send_message(self.chat_id, f"Не найден клан {params_dict['clan_no']}")
        except IntegrityError as err:
            main_logger.info(f"Ошибка создания персонажа: {err}")
            await self.bot.send_message(self.chat_id, "Ошибка создания персонажа! Проверьте параметры!")

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
            await self.bot.send_message(self.chat_id, "У этого игрока нет персонажей!")

    async def view_all_chars(self):
        chars = self.char_config.get_all_chars()
        if chars:
            await self.view_list_from_db(chars)
        else:
            await self.bot.send_message(self.chat_id, "В игре нет персонажей!")

    async def edit_char(self):
        params_dict = {}
        name, params_str = self.text.strip().split("\n", 1)
        params_list = params_str.strip().split("\n")
        reason = ""
        for item in params_list:
            col, val = prepare_for_db(item.strip().split(":", 1))
            if col and val and col in Characters.attrs() or col.lower() == "name":
                params_dict.update({col: val})
            if col == "reason":
                reason = val
        # params_dict.update({"name": name.capitalize()})
        if not reason:
            await self.bot.send_message(self.chat_id, "Пожалуйста, укажите причину изменения характеристик")
            return
        try:
            self.char_config.edit_character(name.capitalize(), params_dict, reason)
            new_char = self.char_config.get_char_by_name(params_dict.get("name") or name.capitalize())
            await self.context.bot.send_message(self.chat_id, str(new_char))
        except NotRealClanError:
            await self.bot.send_message(self.chat_id, f"Не найден клан {params_dict['clan_no']}")

    async def freeze(self):
        if "\n" in self.text:
            name, reason = self.text.split("\n")
        else:
            await self.bot.send_message(self.chat_id, "Пожалуйста, укажите причину заморозки")
            return
        self.char_config.edit_freeze_char_by_name(name.strip().capitalize(), reason.strip())
        await self.bot.send_message(
            self.chat_id,
            f"Персонаж {name} заморожен.",
            reply_to_message_id=self.update.message.id,
        )

    async def unfreeze(self):
        if "\n" in self.text:
            name, reason = self.text.split("\n")
        else:
            await self.bot.send_message(self.chat_id, "Пожалуйста, укажите причину воскрешения")
            return
        self.char_config.edit_freeze_char_by_name(name.strip().capitalize(), reason.strip(), False)
        await self.bot.send_message(
            self.chat_id,
            f"Персонаж {name} разморожен.",
            reply_to_message_id=self.update.message.id,
        )

    @superuser_command
    async def kill(self):
        if "\n" in self.text:
            name, reason = self.text.split("\n")
        else:
            await self.bot.send_message(self.chat_id, "Пожалуйста, укажите причину убийства")
            return
        self.char_config.edit_death_char_by_name(name.capitalize().strip(), reason, True)
        await self.bot.send_message(
            self.chat_id,
            f"Персонаж {name} убит.",
            reply_to_message_id=self.update.message.id,
        )

    @superuser_command
    async def resurrect(self):
        if "\n" in self.text:
            name, reason = self.text.split("\n")
        else:
            await self.bot.send_message(self.chat_id, "Пожалуйста, укажите причину воскрешения")
            return
        self.char_config.edit_death_char_by_name(name.capitalize().strip(), reason, False)
        await self.bot.send_message(
            self.chat_id,
            f"Персонаж {name} воскрешен.",
            reply_to_message_id=self.update.message.id,
        )

    async def view_char_hist(self):
        name = self.text.capitalize().strip()
        try:
            hist = self.char_config.get_char_history(name)
            await self.view_list_from_db(hist)
        except CharNotFound:
            await self.bot.send_message(self.chat_id, f"Персонаж с именем {name} не найден.")

    async def set_hunt_attempts(self):
        def validate_new(val: str) -> int | Exception:
            try:
                new = int(val)
                if new < 0:
                    return Exception("Новое число должно быть больше 0")
                return new
            except ValueError:
                return Exception("Новое число должно быть целым.")
            except Exception as err:
                main_logger.error(f"Ошибка установки количества охот: {err}")
                raise

        if "\n" in self.text:
            cat, params = self.text.split("\n", 1)
        else:
            self.bot.send_message(
                self.chat_id,
                "Не все параметры указаны: необходимо передать новое значение (опционально) и причину изменений!",
            )
            return
        d_params = {"new": 0}
        for param in params.split("\n"):
            key, val = param.split(":")
            if key.lower() == "reason":
                d_params["reason"] = val
            elif key.lower() == "new":
                if isinstance(new := validate_new(val), Exception):
                    await self.bot.send_message(self.chat_id, new.args[0])
                    return
                d_params["new"] = new
        try:
            self.char_config.set_curr_hunts(cat.capitalize(), d_params["new"], d_params["reason"])
        except CharNotFound as err:
            await self.bot.send_message(self.chat_id, err.tg_answer)
            return
        await self.bot.send_message(self.chat_id, f"Новое количество охот персонажу {cat} успешно задано.")
        main_logger.debug(f"Установлено новое количество охот для {cat} = {d_params['new']}")
