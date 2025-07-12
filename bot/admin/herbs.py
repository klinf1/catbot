from telegram import Update
from telegram.ext import ContextTypes

from bot.command_base import CommandBase
from db import Herbs
from db.herbs import HerbConfig
from exceptions import EditError


class HerbCommandHandler(CommandBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.herb_db = HerbConfig()

    async def add_herb(self):
        params = await self.make_params_for_db_entity_create(Herbs)
        self.herb_db.add_herb(params)

    async def delete_herb(self):
        self.herb_db.delete_herb(self.text.capitalize())

    async def edit_herb(self):
        try:
            name, params = await self.make_params_for_db_entity_edit(Herbs)
        except EditError as e:
            await self.bot.send_message(self.chat_id, e.text)
        else:
            self.herb_db.edit_herb(name.capitalize(), params)

    async def view_herb_by_name(self):
        herb = self.herb_db.get_herb_by_name(self.text)
        await self.bot.send_message(self.chat_id, str(herb))

    async def view_all_herbs(self):
        herbs = self.herb_db.get_all_herbs()
        await self.view_list_from_db(herbs)
