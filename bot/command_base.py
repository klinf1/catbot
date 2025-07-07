from telegram import Update, User
from telegram.ext import ContextTypes


class CommandBase:
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.update = update
        self.context = context
        self.command: str = self.update.message.text.split(" ", 1)[0].replace("/", "")  # type: ignore
        self.user: User = self.update.message.from_user  # type: ignore
        self.chat_id: int = self.update.effective_chat.id  # type: ignore
        self.text = self.update.message.text.replace(f"/{self.command}", "").strip()  # type: ignore

    async def unknown_command(self):
        await self.context.bot.send_message(self.chat_id, "Неизвестная команда!")

    async def view_list_from_db(self, db_res):
        res = ""
        for i in db_res:
            res = "\n".join([res, str(i), "______"])
        await self.context.bot.send_message(self.chat_id, res)
