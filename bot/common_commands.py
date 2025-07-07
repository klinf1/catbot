from sqlmodel import select
from telegram import Update
from telegram.ext import ContextTypes

from bot.command_base import CommandBase
from bot.hunt import HuntCommandHandler
from db import Players
from db.decorators import not_banned
from db.players import DbPlayerConfig
from logs.logs import main_logger


class CommonCommandHandler(CommandBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.player_db = DbPlayerConfig()
        self.hunt = HuntCommandHandler(update, context)

    async def __aenter__(self):
        main_logger.debug(
            f"Common command manager starting with command: {self.command}"
        )
        query = select(Players).where(Players.chat_id == self.user.id)
        with self.player_db.session as s:
            res = s.exec(query).all()
        if not res:
            self.player_db.add_player(
                self.user.id,
                self.user.username,  # type: ignore
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
            case 'hunt' | 'hunt_help':
                await getattr(self.hunt, self.command)()
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
