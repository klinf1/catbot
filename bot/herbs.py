from telegram import Update
from telegram.ext import ContextTypes

from bot.command_base import CommandBase
from db.herbs import HerbUser
from exceptions import CharacterDeadException, CharacterFrozenException
from logs.logs import main_logger
from utils import capitalize_for_db


class HerbCommandHandler(CommandBase):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)

    async def gather(self):
        params = capitalize_for_db(self.text.strip().split(" "))
        try:
            main_logger.debug(
                f"Начало собирательства для {self.user.username} {params}"
            )
            herb, success = HerbUser(
                params[0], (params[1] if len(params) > 1 else None)
            ).gather()
        except CharacterDeadException:
            await self.context.bot.send_message(self.chat_id, "Этот персонаж мертв!")
            main_logger.info(
                f"Собирательство с мертвым персонажем: {self.user.username}"
            )
        except CharacterFrozenException:
            await self.context.bot.send_message(
                self.chat_id, "Этот персонаж сейчас неактивен!"
            )
            main_logger.info(
                f"Собирательство с замороженным персонажем: {self.user.username}"
            )
        except Exception as err:
            main_logger.error(err)
        else:
            if success and herb:
                await self.context.bot.send_message(
                    self.chat_id, f"Вы нашли {herb.name}!"
                )
            elif not herb:
                await self.bot.send_message(
                    self.chat_id, "Вы не нашли никакой полезной травы."
                )
            else:
                await self.context.bot.send_message(
                    self.chat_id,
                    f"Вы пытались собрать траву {herb.name}, но испортили ее в процессе",
                )

    async def gather_help(self):
        text = (
            "Это команда для поска целебных трав! Необходимо указать имя кота и территорию, на которой он будет искать через пробел. "
            "Если кот собирает на ничейной территории, то только имя кота."
        )
        await self.context.bot.send_message(self.chat_id, text)
