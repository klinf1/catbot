from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.command_base import CommandBase
from db.inventory import InventoryManager
from exceptions import CharacterDeadException, CharacterFrozenException
from logs.logs import main_logger
from utils import capitalize_for_db


class InventoryCommandHandler(CommandBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.inventory_db = InventoryManager()
