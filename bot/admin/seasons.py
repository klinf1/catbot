from telegram import Update
from telegram.ext import ContextTypes

from bot.command_base import CommandBase
from db import Seasons
from db.seasons import SeasonsConfig


class SeasonCommandHandler(CommandBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.season_db = SeasonsConfig()
    
    async def view_all_seasons(self):
        seasons = self.season_db.get_all_seasons()
        await self.view_list_from_db(seasons)
    
    async def get_active_season(self):
        season: Seasons = self.season_db.get_active_season()
        await self.bot.send_message(self.chat_id, str(season))
    
    async def add_season(self):
        params = await self.make_params_for_db_entity_create(Seasons)
        self.season_db.add_season(params)
        await self.bot.send_message(self.chat_id, "Season added")
    
    async def delete_season(self):
        season = self.text.capitalize().strip()
        self.season_db.remove_season(season)
        await self.bot.send_message(self.chat_id, "Season deleted")
    
    async def edit_season(self):
        season, params = await self.make_params_for_db_entity_edit(Seasons)
        self.season_db.edit_season(season, params)
        await self.bot.send_message(self.chat_id, "Season edited")