from telegram import Update
from telegram.ext import ContextTypes

from bot.admin.admin_commands import AdminCommandHandler
from bot.common_commands import CommonCommandHandler


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
