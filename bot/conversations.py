from telegram import Update
from telegram.ext import ContextTypes

from bot.command_base import CallbackBase
from bot.const import EAT_PREY, LEAVE_PREY, TAKE_PREY
from db.characters import DbCharacterConfig
from db.eat import Eater
from db.inventory import InventoryManager
from logs.logs import main_logger as logger


class HuntConversation(CallbackBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.char_db = DbCharacterConfig()
        self.inventory_db = InventoryManager()
        self.nom = Eater()

    async def __aenter__(self):
        await self.answer_query()
        logger.debug(f"Processing callback action: {self.query_data}")
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        logger.debug("Exiting HuntConversation context manager.")

    async def action(self):
        prey = self.context.user_data["state"]["args"]["prey"]
        char = self.char_db.get_char_by_name(
            self.context.user_data["state"]["args"]["cat"]
        )
        match self.query_data:
            case "take_prey":
                res = self.inventory_db.add_item(
                    char_no=char.no, type="prey", item_id=prey.no
                )
                await self.context.bot.send_message(self.chat_id, res)
            case "leave_prey":
                await self.bot.send_message(self.chat_id, "Вы оставили добычу.")
            case "eat_prey":
                res = self.nom.eat(char, prey)
                await self.context.bot.send_message(self.chat_id, res)
