from telegram import Update
from telegram.ext import ContextTypes

from bot.buttons import (
    get_view_inv_keyboard,
    get_hunt_keyboard,
    get_single_inv_keyboard,
)
from bot.command_base import CallbackBase
from bot.const import EAT_PREY, LEAVE_PREY, TAKE_PREY
from db.characters import DbCharacterConfig
from db.eat import Eater
from db.inventory import InventoryManager
from db.prey import DbPreyConfig
from logs.logs import main_logger as logger


class HuntConversation(CallbackBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.char_db = DbCharacterConfig()
        self.inventory_db = InventoryManager()
        self.nom = Eater()

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


class InvBaseConv(CallbackBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.char_db = DbCharacterConfig()
        self.inventory_db = InventoryManager()

    async def action(self):
        char = self.char_db.get_char_by_name(
            self.context.user_data["state"]["args"]["cat"]
        )
        match self.query_data:
            case "view_inv":
                self.context.user_data.update(
                    {
                        "state": {
                            "name": "inv_view",
                            "args": {"cat": char},
                        }
                    }
                )
                await self.bot.send_message(
                    self.chat_id,
                    f"Инвентарь кота {char.name}",
                    reply_markup=get_view_inv_keyboard(char.no),
                )
            case "clear_inv":
                self.inventory_db.clear_inventory(char.no)
                await self.bot.send_message(self.chat_id, "Инвентарь очищен!")


class InvViewConv(CallbackBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.prey_db = DbPreyConfig()

    async def action(self):
        char = self.context.user_data["state"]["args"]["cat"]
        prey = self.prey_db.get_prey_by_no(self.query_data)
        text = f"Дичь:\n{prey}\n\nЧто бы вы хотели сделать?"
        self.context.user_data.update(
            {
                "state": {
                    "name": "hunt_completed",
                    "args": {"prey": prey, "cat": char.name},
                }
            }
        )
        await self.bot.send_message(
            self.chat_id, text, reply_markup=get_single_inv_keyboard()
        )
