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
        success, reply = self.player_db.ban_player(self.text)
        await self.context.bot.send_message(self.chat_id, reply)
        if success:
            player = self.player_db.get_player_by_username(self.text)
            await self.bot.send_message(
                player.chat_id,
                "к сожалению, вы были внесены в черный список. "
                "До разбана бот не будет реагировать на ваши команды, а все ваши персонажи будут заморожены. "
                "Если вы считаете, что вас забанили несправедливо, свяжитесь с админинстрацией.",
            )

    async def unban(self):
        success, reply = self.player_db.unban_player(self.text)
        await self.bot.send_message(self.chat_id, reply)
        if success:
            player = self.player_db.get_player_by_username(self.text)
            await self.bot.send_message(
                player.chat_id,
                "Вы были убраны из черного списка."
                "Бот готов отвечать на ваши команды, "
                "а все ваши персонажи разморожены и находятся в том же состоянии, что и до бана. "
                "Хорошей игры!",
            )

    @superuser_command
    async def promote(self):
        reply = self.player_db.promote_or_demote(self.text, True)
        await self.bot.send_message(self.chat_id, reply)

    @superuser_command
    async def demote(self):
        reply = self.player_db.promote_or_demote(self.text, False)
        await self.bot.send_message(self.chat_id, reply)

    async def view_all_players(self):
        players = self.player_db.get_all_players()
        await self.view_list_from_db(players)
    
    async def view_ban_list(self):
        players = self.player_db.get_all_banned()
        await self.view_list_from_db(players, "Черный список пуст.")

