from typing import Any

from telegram import Bot, Update, User
from telegram.ext import ContextTypes

from exceptions import EditError
from logs.logs import main_logger


class CommandBase:
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.update = update
        self.context = context
        self.command: str = self.update.message.text.split(" ", 1)[0].replace("/", "")  # type: ignore
        self.user: User = self.update.message.from_user  # type: ignore
        self.chat_id: int = self.update.effective_chat.id  # type: ignore
        self.text = self.update.message.text.replace(f"/{self.command}", "").strip()  # type: ignore
        self.bot: Bot = self.context.bot

    async def unknown_command(self):
        await self.context.bot.send_message(self.chat_id, "Неизвестная команда!")

    async def view_list_from_db(self, db_res):
        res = ""
        for i in db_res:
            res = "\n".join([res, str(i), "______"])
        await self.context.bot.send_message(self.chat_id, res)

    @staticmethod
    async def __set_explicit_none(value: Any) -> Any | None:
        if not value:
            return None
        return value

    async def set_explicit_none(self, values: list | dict):
        if isinstance(values, dict):
            for key, value in values.items():
                values[key] = self.__set_explicit_none(value)
        elif isinstance(values, list):
            for i in range(len(values)):
                values[i] = self.__set_explicit_none(values[i])
        return values

    @staticmethod
    def prepare_for_db(str_list: list[str]) -> list[str]:
        str_list = list(map(str.lower, str_list))
        str_list = list(map(str.strip, str_list))
        return str_list

    async def make_params_for_db_entity_create(self, db_entity) -> dict[str, str]:
        params_dict = {}
        name, params_str = self.text.split("\n", 1)
        params_list = params_str.strip().split("\n")
        for item in params_list:
            col, value = self.prepare_for_db(item.strip().split(":", 1))
            if col and value and col in db_entity.attrs():
                params_dict.update({col: value})
        params_dict["name"] = name.capitalize()
        return params_dict

    async def make_params_for_db_entity_edit(self, db_entity) -> list:
        params_dict = {}
        try:
            name, params_str = self.text.split("\n", 1)
        except ValueError as e:
            main_logger.error(e)
            raise EditError(
                "Ошибка при формировании параметров для замены: отсутствуют подходящие параметры."
            )
        params_list = params_str.strip().split("\n")
        for item in params_list:
            col, value = self.prepare_for_db(item.strip().split(":", 1))
            if col and (col in db_entity.attrs() or col in ("name", "Name")):
                value = await self.__set_explicit_none(value)
                params_dict.update({col: value})
        if params_dict == {}:
            raise EditError(
                "Ошибка при формировании параметров для замены: отсутствуют подходящие параметры."
            )
        return [name.capitalize(), params_dict]
