from telegram import Update
from telegram.ext import ContextTypes

from bot.admin.admin_commands import AdminCommandHandler
from bot.common_commands import CommonCommandHandler
from bot.const import EAT_PREY, LEAVE_PREY, TAKE_PREY
from bot.conversations import HuntConversation
from logs.logs import main_logger as logger


class CommandRouter:
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.command: str = update.message.text.split(" ", 1)[0].replace("/", "")  # type: ignore
        self.update = update
        self.context = context

    async def route(self):
        if self.command in CommonCommandHandler.__dict__:
            async with CommonCommandHandler(self.update, self.context) as c:
                await getattr(c, self.command)()
        else:
            async with AdminCommandHandler(self.update, self.context) as c:
                await c.route()


class ConversationRouter:
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.update = update
        self.context = context

    async def route(self):
        if self.context.user_data.get("state"):
            pass


class CallbackRouter:
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.update = update
        self.context = context
        self.hunt_conv = HuntConversation(update, context)

    async def route(self):
        if state := self.context.user_data.get("state", {}):
            logger.debug(f"Starting callback routing with state: {state}")
            match state.get("name"):
                case "hunt_completed":
                    async with self.hunt_conv as conv:
                        await conv.action()
