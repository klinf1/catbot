from telegram import Update
from telegram.ext import ContextTypes

from bot.buttons import (get_single_inv_keyboard,
                         get_view_inv_keyboard)
from bot.command_base import CallbackBase
from db.characters import DbCharacterConfig
from db.eat import Eater
from db.inventory import InventoryManager
from db.pile import PreyPileConfig
from db.prey import DbPreyConfig


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
                if not self.inventory_db.get_char_inventory(char.no):
                    await self.bot.send_message(self.chat_id, f"Инвентарь персонажа {char.name} пуст")
                    return
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
                    f"Инвентарь персонажа {char.name}",
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
        clan_cat = char.clan_no is not None
        if "Дичь:" in self.query_data:
            prey = self.prey_db.get_prey_by_no(self.query_data.replace("Дичь:", ""))
            text = f"Дичь:\n{prey}\n\nЧто бы вы хотели сделать?"
            self.context.user_data.update(
                {
                    "state": {
                        "name": "prey_view",
                        "args": {"prey": prey, "cat": char.name},
                    }
                }
            )
            await self.bot.send_message(
                self.chat_id, text, reply_markup=get_single_inv_keyboard(clan_cat)
            )


class PreyViewConv(CallbackBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.prey_db = DbPreyConfig()
        self.nom = Eater()
        self.pile = PreyPileConfig()
        self.inv = InventoryManager()
        self.char_db = DbCharacterConfig()
    
    async def action(self):
        prey = self.context.user_data["state"]["args"]["prey"]
        char = self.char_db.get_char_by_name(
            self.context.user_data["state"]["args"]["cat"]
        )
        match self.query_data:
            case "carry_prey":
                res = self.pile.add_to_pile(char.clan_no, prey)
                self.inv.remove_item(char.no, prey.no)
                await self.context.bot.send_message(self.chat_id, res)
            case "leave_prey":
                self.inv.remove_item(char.no, prey.no)
                await self.bot.send_message(self.chat_id, "Вы оставили добычу.")
            case "eat_prey":
                res = self.nom.eat(char, prey)
                self.inv.remove_item(char.no, prey.no)
                await self.context.bot.send_message(self.chat_id, res)
