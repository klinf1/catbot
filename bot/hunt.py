from telegram import Update
from telegram.ext import ContextTypes

from db.decorators import not_banned, register_player_if_not_exists
from db.exceptions import CharacterDeadException, CharacterFrozenException
from db.hunt import Hunt
from logs.logs import main_logger
from utils import capitalize_for_db


@register_player_if_not_exists
@not_banned
async def hunt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/hunt", "")
    params = capitalize_for_db(text.strip().split(" "))
    try:
        main_logger.debug(
            f"Начало охоты для {update.message.from_user.username} {params}"
        )
        prey, success = Hunt(params[0], (params[1] if len(params) > 1 else None)).hunt()
    except CharacterDeadException as e:
        await context.bot.send_message(update.effective_chat.id, "Этот персонаж мертв!")
        main_logger.info(
            f"Охота с мертвым персонажем: {update.message.from_user.username}"
        )
    except CharacterFrozenException as e:
        await context.bot.send_message(
            update.effective_chat.id, "Этот персонаж сейчас неактивен!"
        )
        main_logger.info(
            f"Охота с замороженным персонажем: {update.message.from_user.username}"
        )
    except Exception as err:
        main_logger.error(err)
    else:
        if success:
            await context.bot.send_message(
                update.effective_chat.id, f"Охота на {prey.name} успешна!"
            )
        else:
            await context.bot.send_message(
                update.effective_chat.id, f"Охота на {prey.name} провалилась!"
            )


@register_player_if_not_exists
@not_banned
async def hunt_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Это команда для охоты! Необходимо указать имя кота и территорию, на которой он охотится через пробел. "
        "Если кот охотится на ничейной территории, то только имя кота."
    )
    await context.bot.send_message(update.effective_chat.id, text)
