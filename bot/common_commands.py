from sqlmodel import select
from telegram import Update
from telegram.ext import ContextTypes

from bot.command_base import CommandBase
from bot.herbs import HerbCommandHandler
from bot.hunt import HuntCommandHandler
from bot.inventory import InventoryCommandHandler
from db import Players
from db.characters import DbCharacterUser
from db.players import DbPlayerConfig
from exceptions import BannedException, WrongChatError
from logs.logs import main_logger


class CommonCommandHandler(CommandBase):
    allowed_outside_group = [
        "health",
        "view_own_chars",
        "view_single_char",
        "commands",
        "hunt_help",
        "start",
    ]
    char_404_msg = "Персонаж с таким именем не найден или не принадлежит Вам."

    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.player_db = DbPlayerConfig()
        self.hunt_db = HuntCommandHandler(update, context)
        self.herb_db = HerbCommandHandler(update, context)
        self.inventory_db = InventoryCommandHandler(update, context)
        self.character_user_db = DbCharacterUser(update.message.from_user.id)

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
        if (
            self.command not in self.allowed_outside_group
            and str(self.chat_id) not in self.group_chats
            and (not player.is_admin or not player.is_superuser)
        ):
            await self.bot.send_message(
                self.chat_id, f"Эта команда доступна только в групповом чате!"
            )
            raise WrongChatError
        return self

    async def __aexit__(self, *args):
        main_logger.debug("Command handler shutting down")

    async def commands(self):
        commands = "\n".join(
            [
                "Доступные на текущий момент команды:",
                "health - если бот ответил, значит он работает!",
                "hunt [имя персонажа] [название клана, на территории которого он будет охотиться]",
                "hunt_help - помощь по использовании команды /hunt",
                "view_own_chars - просмотреть состояние всех ваших персонажей",
                "view_single_char [Имя персонажа] - просмотреть состояние персонажа с указанным именем",
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
        await self.context.bot.send_message(
            self.chat_id, commands, reply_to_message_id=self.update.message.id
        )

    async def start(self):
        if self.chat_id > 0:
            await self.context.bot.send_message(
                self.chat_id,
                "Добро пожаловать!",
                reply_to_message_id=self.update.message.id,
            )

    async def health(self):
        await self.context.bot.send_message(
            self.chat_id,
            "I'm here for you!",
            reply_to_message_id=self.update.message.id,
        )

    async def hunt(self):
        name = self.text.split(" ")[0].strip()
        if not self.character_user_db.get_one_own_char(name):
            await self.bot.send_message(
                self.chat_id,
                self.char_404_msg,
                reply_to_message_id=self.update.message.id,
            )
            return None
        await self.hunt_db.hunt()

    async def hunt_help(self):
        await self.hunt_db.hunt_help()

    async def view_own_chars(self):
        chars = self.character_user_db.get_all_own_chars()
        await self.view_list_from_db(chars)

    async def view_single_char(self):
        char = self.character_user_db.get_one_own_char(self.text)
        if not char:
            await self.bot.send_message(
                self.chat_id,
                self.char_404_msg,
                reply_to_message_id=self.update.message.id,
            )
        else:
            await self.bot.send_message(self.chat_id, str(char))

    async def gather(self):
        return
        await self.herb_db.gather()

    async def gather_help(self):
        return
        await self.herb_db.gather_help()

    async def inventory(self):
        return
        await self.inventory_db.send_inventory_message()
