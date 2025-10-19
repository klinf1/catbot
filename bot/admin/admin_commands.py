import traceback

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from bot.admin.characters import CharacterCommandHandler
from bot.admin.clans import ClanCommandHandler
from bot.admin.herbs import HerbCommandHandler
from bot.admin.injuries import InjuryCommandHandler
from bot.admin.players import PlayerCommandHandler
from bot.admin.prey import PreyCommandHandler
from bot.admin.seasons import SeasonCommandHandler
from bot.admin.system import SystemCommandHandler
from bot.command_base import CommandBase
from db.players import DbPlayerConfig
from exceptions import NoRightException
from logs.logs import main_logger


class AdminCommandHandler(CommandBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.player_db = DbPlayerConfig()

    @property
    def subclasses(self) -> list:
        return [
            CharacterCommandHandler,
            PreyCommandHandler,
            PlayerCommandHandler,
            InjuryCommandHandler,
            ClanCommandHandler,
            HerbCommandHandler,
            SeasonCommandHandler,
            SystemCommandHandler,
        ]

    async def __aenter__(self):
        main_logger.debug(
            f"Admin command manager starting with command: {self.command}\nparams: {self.text}"
        )
        if not self.player_db.check_if_user_is_admin(self.user.id):
            self.context.chat_data.update(  # type: ignore
                {"exc": {"admin_error": [self.user.id, self.user.username]}}
            )
            raise NoRightException("No rights!")
        return self

    async def __aexit__(self, *args):
        main_logger.debug("Admin command handler shutting down")

    async def route(self):
        for handler in self.subclasses:
            if self.command in handler.__dict__:
                cls = handler(self.update, self.context)
                try:
                    await getattr(cls, self.command)()
                except TelegramError as err:
                    raise TelegramError(str(err)) from err
                except Exception as err:
                    await self.context.bot.send_message(self.chat_id, "Ошибка. Тагните Клинфа.")
                    main_logger.error(f"Error in {self.command}: {err}\n{traceback.format_exc()}")
                break
        else:
            await self.unknown_command()
