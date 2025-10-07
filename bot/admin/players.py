from telegram import Update
from telegram.ext import ContextTypes

from bot.command_base import CommandBase
from db.decorators import superuser_command
from db.players import DbPlayerConfig


class PlayerCommandHandler(CommandBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.player_db = DbPlayerConfig()

    async def ban(self):
        reply = self.player_db.ban_player(self.text)
        await self.context.bot.send_message(self.chat_id, reply)

    async def unban(self):
        reply = self.player_db.unban_player(self.text)
        await self.bot.send_message(self.chat_id, reply)

    @superuser_command
    async def promote(self):
        reply = self.player_db.promote_or_demote(self.text, True)
        await self.bot.send_message(self.chat_id, reply)

    @superuser_command
    async def demote(self):
        reply = self.player_db.promote_or_demote(self.text, False)
        await self.bot.send_message(self.chat_id, reply)

    async def view_all_players(self):
        players = DbPlayerConfig().get_all_players()
        await self.view_list_from_db(players)
