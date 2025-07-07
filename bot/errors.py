from telegram.ext import ContextTypes

from logs.logs import main_logger, user_logger


class ErrorHandler:
    def __init__(self, context: ContextTypes.DEFAULT_TYPE, dev_id: str) -> None:
        self.context = context
        self.dev_id: int = int(dev_id)
        self.exc_dict: dict = context.chat_data.get("exc", {})  # type: ignore

    @property
    def error_dict(self):
        return {
            "admin_error": self.admin_error,
            "banned": self.banned_error,
            "superuser_error": self.superuser_error,
        }

    async def route(self):
        for key in self.exc_dict.keys():
            if key in  self.error_dict.keys():
                await self.error_dict[key]()
                break
        else:
            await self.unexpected_error()

    async def admin_error(self):
        user_logger.info(
            f"{self.exc_dict['admin_error'][1]} хотел использовать админскую комманду!"
        )
        self.context.chat_data["exc"].__delitem__("admin_error")  # type: ignore

    async def banned_error(self):
        user_logger.info(
            f"{self.exc_dict['banned'][1]} забанен, но очень хочет играть."  # type: ignore
        )
        await self.context.bot.send_message(
            self.exc_dict["banned"][0], "Вы в бане!"  # type: ignore
        )
        self.context.chat_data["exc"].__delitem__("banned")  # type: ignore

    async def superuser_error(self):
        user_logger.info(
            f"{self.exc_dict['superuser_error'][1]} хотел использовать команду суперюзера!"  # type: ignore
        )
        await self.context.bot.send_message(self.exc_dict["superuser_error"][0], 'Это команда для владельцев бота.')  # type: ignore
        self.context.chat_data["exc"].__delitem__("superuser_error")  # type: ignore

    async def unexpected_error(self):
        main_logger.exception(self.context.error)
        await self.context.bot.send_message(
            self.dev_id, str(self.context.error)
        )
