from telegram import Update
from telegram.ext import ContextTypes

from bot.buttons import get_pile_keyboard
from bot.command_base import CommandBase
from db.characters import DbCharacterConfig
from db.pile import PreyPileConfig


class PileCommandHandler(CommandBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.char_db = DbCharacterConfig()
        self.pile_db = PreyPileConfig()
    
    async def send_pile_message(self):
        char = self.char_db.get_char_by_name(self.text.capitalize())
        if not char:
            await self.bot.send_message(self.chat_id, "Персонаж с таким именем не найден")
        elif char.player_chat_id != self.user.id:
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
        elif not char.clan_no:
            await self.bot.send_message(
                self.chat_id, "Этот персонаж не принадлежит ни одному клану!"
            )    
        else:
            self.context.user_data.update(
                {
                    "state": {
                        "name": "pile_view",
                        "args": {"cat": char},
                    }
                }
            )
            prey = self.pile_db.get_prey_for_clan(char.clan_no)
            await self.bot.send_message(
                self.chat_id,
                "Список дичи в вашем клане:",
                reply_markup=get_pile_keyboard(prey),
            )
