from sqlmodel import select
from telegram import Update
from telegram.ext import ContextTypes

from bot.command_base import CommandBase
from bot.herbs import HerbCommandHandler
from bot.hunt import HuntCommandHandler
from db import Players
from db.players import DbPlayerConfig
from exceptions import BannedException
from logs.logs import main_logger


class CommonCommandHandler(CommandBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.player_db = DbPlayerConfig()
        self.hunt_db = HuntCommandHandler(update, context)
        self.herb_db = HerbCommandHandler(update, context)

    async def __aenter__(self):
        main_logger.debug(
            f"Common command manager starting with command: {self.command}"
        )
        query = select(Players).where(Players.chat_id == self.user.id)
        with self.player_db.session as s:
            player = s.exec(query).first()
        if not player:
            self.player_db.add_player(
                self.user.id,
                self.user.username,  # type: ignore
                self.user.first_name,
                self.user.last_name,
            )
            main_logger.info(
                f"Игрок {self.user.id} {self.user.username} зарегистрирован"
            )
        else:
            if player.is_banned and self.command != "health":
                raise BannedException("banned af")
        return self

    async def __aexit__(self, *args):
        main_logger.debug("Command handler shutting down")

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

    async def start(self):
        if self.chat_id > 0:
            await self.context.bot.send_message(self.chat_id, "Добро пожаловать!")

    async def health(self):
        await self.context.bot.send_message(self.chat_id, "I'm here for you!")

    async def hunt(self):
        await self.hunt_db.hunt()

    async def hunt_help(self):
        await self.hunt_db.hunt_help()

    async def gather(self):
        await self.herb_db.gather()

    async def gather_help(self):
        await self.herb_db.gather_help()
