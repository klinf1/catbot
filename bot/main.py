import os

from dotenv import load_dotenv
from sqlmodel import select
from telegram import Update, User
from telegram.ext import (Application, CommandHandler, ContextTypes,
                          MessageHandler, filters)

from bot.admin.characters import add_char, add_char_help, view_chars_by_player
from bot.admin.clans import add_clan, add_clan_help
from bot.admin.injuries import add_injury, add_injury_help
from bot.admin.players import ban, demote, promote, unban, view_all_players
from bot.admin.prey import add_prey, add_prey_help, view_all_prey
from bot.hunt import hunt, hunt_help
from db import Players
from db.decorators import not_banned
from db.players import DbPlayerConfig
from logs.logs import main_logger, user_logger

load_dotenv()


class CommandBase:
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.update = update
        self.context = context
        self.command: str = self.update.message.text.split(" ", 1)[0].replace("/", "")
        self.user: User = self.update.message.from_user
        self.chat_id: int = self.update.effective_chat.id
        self.player_db = DbPlayerConfig()

    async def unknown_command(self):
        await self.context.bot.send_message(self.chat_id, "Неизвестная команда!")


class CommonCommandHandler(CommandBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)

    async def __aenter__(self):
        main_logger.debug(f"Command manager starting with command: {self.command}")
        query = select(Players).where(Players.chat_id == self.user.id)
        with self.player_db.session as s:
            res = s.exec(query).all()
        if not res:
            self.player_db.add_player(
                self.user.id,
                self.user.username,
                self.user.first_name,
                self.user.last_name,
            )
            main_logger.info(
                f"Игрок {self.user.id} {self.user.username} зарегистрирован"
            )
        return self

    async def __aexit__(self, *args):
        main_logger.debug("Command handler shutting down")

    async def route(self):
        match self.command:
            case "commands":
                await self.commands()
            case "start":
                await self.start()
            case "health":
                await self.health()
            case _:
                await self.unknown_command()

    @not_banned
    async def commands(self):
        commands = "\n".join(
            [
                "Доступные на текущий момент команды:",
                "health - если бот ответил, значит он работает!",
                "hunt",
                "hunt_help",
            ]
        )
        if self.player_db.check_if_user_is_admin(self.user.id):
            commands = "\n".join(
                [
                    commands,
                    "add_char",
                    "add_clan",
                    "add_prey",
                    "add_prey_help",
                    "add_char_help",
                    "add_clan_help",
                    "ban [username]",
                    "unban [username]",
                    "view_all_prey",
                    "view_chars_by_player [username]",
                    "promote [username]",
                    "demote [username]",
                    "view_all_players",
                    "add_injury",
                    "add_injury_help",
                ]
            )
        await self.context.bot.send_message(self.chat_id, commands)

    @not_banned
    async def start(self):
        if self.chat_id > 0:
            await self.context.bot.send_message(self.chat_id, "Добро пожаловать!")

    async def health(self):
        await self.context.bot.send_message(self.chat_id, "I'm here for you!")


class ErrorHandler:
    def __init__(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.context = context

    @property
    def error_dict(self):
        return {
            "admin_error": self.admin_error,
            "banned": self.banned_error,
            "superuser_error": self.superuser_error,
        }

    async def route(self):
        for key in self.context.chat_data.get("exc", {}).keys():
            callback = self.error_dict.get(key, self.unexpected_error)
            await callback()

    async def admin_error(self):
        user_logger.info(
            f"{self.context.chat_data['admin_error'][1]} хотел использовать админскую комманду!"
        )
        self.context.chat_data.__delitem__("admin_error")

    async def banned_error(self):
        user_logger.info(
            f"{self.context.chat_data['banned'][1]} забанен, но очень хочет играть."
        )
        await self.context.bot.send_message(
            self.context.chat_data["banned"][0], "Вы в бане!"
        )
        self.context.chat_data.__delitem__("banned")

    async def superuser_error(self):
        user_logger.info(
            f"{self.context.chat_data['admin_error'][1]} хотел использовать команду суперюзера!"
        )
        self.context.chat_data.__delitem__("superuser_error")

    async def unexpected_error(self):
        main_logger.exception(self.context.error)
        await self.context.bot.send_message(
            os.getenv("DEV_ID"), str(self.context.error)
        )


async def command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with CommonCommandHandler(update, context) as handler:
        await handler.route()


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    await ErrorHandler(context).route()


def bot_main(token: str):
    app = Application.builder().token(token).build()
    app.add_handler(MessageHandler(filters.COMMAND, command_handler))
    app.add_handler(CommandHandler("hunt", hunt))
    app.add_handler(CommandHandler("hunt_help", hunt_help))
    app.add_handler(CommandHandler("add_char", add_char))
    app.add_handler(CommandHandler("add_clan", add_clan))
    app.add_handler(CommandHandler("add_prey", add_prey))
    app.add_handler(CommandHandler("add_prey_help", add_prey_help))
    app.add_handler(CommandHandler("add_char_help", add_char_help))
    app.add_handler(CommandHandler("add_clan_help", add_clan_help))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("view_all_prey", view_all_prey))
    app.add_handler(CommandHandler("view_chars_by_player", view_chars_by_player))
    app.add_handler(CommandHandler("promote", promote))
    app.add_handler(CommandHandler("demote", demote))
    app.add_handler(CommandHandler("view_all_players", view_all_players))
    app.add_handler(CommandHandler("add_injury", add_injury))
    app.add_handler(CommandHandler("add_injury_help", add_injury_help))
    app.add_error_handler(error_handler)
    app.run_polling()
