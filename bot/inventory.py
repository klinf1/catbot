from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.buttons import get_base_inv_keyboard
from bot.command_base import CommandBase
from db.characters import DbCharacterConfig
from db.inventory import InventoryManager
from exceptions import CharacterDeadException, CharacterFrozenException
from logs.logs import main_logger
from utils import capitalize_for_db


class InventoryCommandHandler(CommandBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.inventory_db = InventoryManager()
        self.character_db = DbCharacterConfig()

    async def send_inventory_message(self):
        char = self.character_db.get_char_by_name(self.text.capitalize())
        if char.player_chat_id != self.user.id:
            await self.bot.send_message(
                self.chat_id, "Этот персонаж не принадлежит вам!"
            )
        elif char.is_frozen:
            await self.bot.send_message(
                self.chat_id, "Этот персонаж заморожен!"
            )
        elif char.is_dead:
            await self.bot.send_message(
                self.chat_id, "Этот персонаж мертв!"
            )    
        else:
            self.context.user_data.update(
                {
                    "state": {
                        "name": "inv_base",
                        "args": {"cat": self.text},
                    }
                }
            )
            await self.bot.send_message(
                self.chat_id,
                "Что бы вы хотели сделать?",
                reply_markup=get_base_inv_keyboard(),
            )
