from telegram import Update
from telegram.ext import ContextTypes

from bot.admin.admin_commands import AdminCommandHandler
from bot.common_commands import CommonCommandHandler


class CommandRouter:
    common_commands = ["commands", "start", "health", "hunt", "hunt_help"]

    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.command: str = update.message.text.split(" ", 1)[0].replace("/", "")  # type: ignore
        self.common = CommonCommandHandler(update, context)
        self.admin = AdminCommandHandler(update, context)

    async def route(self):
        if self.command in self.common_commands:
            async with self.common as c:
                await c.route()
        else:
            async with self.admin as c:
                await c.route()
