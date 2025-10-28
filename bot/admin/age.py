from telegram import Update
from telegram.ext import ContextTypes

from bot.command_base import CommandBase
from db import Ages
from db.age import AgeConfig


class SeasonCommandHandler(CommandBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.age_db = AgeConfig()
    
    async def view_all_ages(self):
        ages = self.age_db.get_ages()
        return self.view_list_from_db(ages)
    
    async def add_age(self):
        params = self.make_params_for_db_entity_create(Ages)
        return self.age_db.new_age(params)
    
    async def set_food_req(self):
        name, val = self.text.strip().split("\n")
        if not self.validate_setting(val):
            await self.bot.send_message(self.chat_id, "Возраст должен быть целым числом больше 0!")
            return
        await self.bot.send_message(self.chat_id, str(self.age_db.edit_food_req(name.strip().capitalize(), val)))
