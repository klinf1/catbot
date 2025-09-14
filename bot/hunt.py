from telegram import Update
from telegram.ext import ContextTypes

from bot.buttons import get_hunt_keyboard
from bot.command_base import CommandBase
from db.hunt import Hunt
from exceptions import CharacterDeadException, CharacterFrozenException
from logs.logs import main_logger
from utils import capitalize_for_db


class HuntCommandHandler(CommandBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)

    async def hunt(self):
        params = capitalize_for_db(self.text.strip().split(" "))
        try:
            main_logger.debug(f"Начало охоты для {self.user.username} {params}")
            prey, success = Hunt(
                params[0], (params[1] if len(params) > 1 else None)
            ).hunt()
        except CharacterDeadException:
            await self.context.bot.send_message(self.chat_id, "Этот персонаж мертв!")
            main_logger.info(f"Охота с мертвым персонажем: {self.user.username}")
        except CharacterFrozenException:
            await self.context.bot.send_message(
                self.chat_id, "Этот персонаж сейчас неактивен!"
            )
            main_logger.info(f"Охота с замороженным персонажем: {self.user.username}")
        except Exception as err:
            main_logger.error(err)
        else:
            if success and prey:
                await self.context.bot.send_message(
                    self.chat_id, f"Охота на {prey.name} успешна!"
                )
                self.context.user_data.update(
                    {
                        "state": {
                            "name": "hunt_completed",
                            "args": {"prey": prey, "cat": params[0]},
                        }
                    }
                )  # type: ignore
                await self.context.bot.send_message(
                    self.chat_id,
                    text=f"Охота успешна! Добыча: {prey.name}",
                    #"Что вы хотите сделать с добычей?",
                    #reply_markup=get_hunt_keyboard(),
                    reply_to_message_id=self.topic_id
                )
            elif not prey:
                await self.bot.send_message(self.chat_id, "Вы не нашли никакой дичи.", reply_to_message_id=self.topic_id)
            else:
                await self.context.bot.send_message(
                    self.chat_id, f"Охота на {prey.name} провалилась!", self.topic_id
                )

    async def hunt_help(self):
        text = (
            "Это команда для охоты! Необходимо указать имя кота и территорию, на которой он охотится через пробел. "
            "Если кот охотится на ничейной территории, то только имя кота."
        )
        await self.context.bot.send_message(self.chat_id, text, reply_to_message_id=self.update.message.id)
