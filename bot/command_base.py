from os import getenv
from typing import Any, Literal

from sqlmodel import SQLModel
from telegram import Bot, Update, User
from telegram.ext import ContextTypes

from exceptions import EditError
from logs.logs import logger


class LoggingCommand:
    log_labels: dict = {}
    log_extras: dict = {}

    def write_log(
        self,
        level: Literal["debug", "info", "warn", "error", "exception"],
        message: str,
        extras: dict = {},
        labels: dict = {},
    ):
        labels.update(self.log_labels)
        extras.update(self.log_extras)
        getattr(logger, level)(message=message, extras=extras, labels=labels)


class CommandBase(LoggingCommand):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.update = update
        self.context = context
        self.command: str = self.update.message.text.split(" ", 1)[0].replace("/", "")  # type: ignore
        self.user: User = self.update.message.from_user  # type: ignore
        self.chat_id: int = self.update.effective_chat.id  # type: ignore
        self.text = self.update.message.text.replace(f"/{self.command}", "").strip()  # type: ignore
        self.bot: Bot = self.context.bot
        self.topic_id: int = getenv("TOPIC", update.message.id)
        self.group_chats = getenv("GROUPS", getenv("ADMINS", "")).split(",")
        self.log_labels = {
            "base": "command",
            "handler": self.__class__.__name__,
            "command": self.command,
            "user_id": self.user.id,
            "user_name": self.user.username,
            "chat_id": self.chat_id,
        }
        self.write_log("debug", self.update.message.text)

    async def unknown_command(self):
        await self.context.bot.send_message(self.chat_id, "Неизвестная команда!")

    async def view_list_from_db(self, db_res, default: str = "Выборка пуста."):
        res = ""
        if not db_res:
            await self.bot.send_message(self.chat_id, default)
            return
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

    async def make_params_for_db_entity_create(self, db_entity: type[SQLModel]) -> dict[str, str]:
        params_dict = {}
        name, params_str = self.text.split("\n", 1)
        params_list = params_str.strip().split("\n")
        for item in params_list:
            col, value = self.prepare_for_db(item.strip().split(":", 1))
            if col and value and (col in db_entity.attrs() or col + "*" in db_entity.attrs()):
                params_dict.update({col: value})
        params_dict["name"] = name.capitalize()
        return params_dict

    async def make_params_for_db_entity_edit(self, db_entity: type[SQLModel]) -> list:
        params_dict = {}
        try:
            name, params_str = self.text.split("\n", 1)
        except ValueError as e:
            self.write_log("error", e)
            raise EditError("Ошибка при формировании параметров для замены: отсутствуют подходящие параметры.")
        params_list = params_str.strip().split("\n")
        for item in params_list:
            col, value = self.prepare_for_db(item.strip().split(":", 1))
            if col and (col in db_entity.attrs() or col + "*" in db_entity.attrs() or col in ("name", "Name")):
                value = await self.__set_explicit_none(value)
                params_dict.update({col: value})
        if params_dict == {}:
            raise EditError("Ошибка при формировании параметров для замены: отсутствуют подходящие параметры.")
        return [name.capitalize(), params_dict]

    @staticmethod
    def validate_setting(val: Any) -> bool:
        try:
            val = int(val)
            assert val > 0
        except Exception:
            return False
        return True

    def strip_split(self, val: str, sym: str, times: int = -1) -> list[str]:
        new = val.split(sym, times)
        new = [i.strip() for i in new]
        return new

    def strip_cap(self, val: str) -> str:
        return val.strip().capitalize()

    def name_params(self, sym: str):
        name, params = self.strip_split(self.text, sym, 1)
        return name.capitalize(), params


class CallbackBase(LoggingCommand):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.update = update
        self.context = context
        self.query = self.update.callback_query
        self.query_data = self.query.data
        self.chat_id: int = self.update.effective_chat.id
        self.bot: Bot = self.context.bot
        self.user: User = self.update.callback_query.from_user  # type: ignore
        self.topic_id: int = getenv("TOPIC")
        self.log_labels = {
            "base": "callback",
            "query_data": self.query_data,
            "user_id": self.user.id,
            "user_name": self.user.username,
            "chat_id": self.chat_id,
        }

    async def __aenter__(self):
        await self.query.answer()
        self.write_log("debug", f"Start {self.__class__.__name__} context manager.")
        self.write_log("debug", f"Processing callback action: {self.query_data}")
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.write_log("debug", f"Exiting {self.__class__.__name__} context manager.")
