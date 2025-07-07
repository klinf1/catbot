from telegram import Update
from telegram.ext import ContextTypes

from db.decorators import admin_command, superuser_command
from db.players import DbPlayerConfig
from logs.logs import main_logger as logger


@admin_command
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.replace("/ban", "").strip()
        reply = DbPlayerConfig().ban_player(int(text))
        await context.bot.send_message(update.effective_chat.id, reply)
    except Exception as err:
        await context.bot.send_message(
            update.effective_chat.id, "Ошибка. Тагните Клинфа."
        )
        logger.error(err)


@admin_command
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.replace("/unban", "").strip()
        DbPlayerConfig().unban_player(int(text))
    except Exception as err:
        await context.bot.send_message(
            update.effective_chat.id, "Ошибка. Тагните Клинфа."
        )
        logger.error(err)


@superuser_command
async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.replace("/promote", "").strip()
        DbPlayerConfig().promote_or_demote(text, True)
    except Exception as err:
        await context.bot.send_message(
            update.effective_chat.id, "Ошибка. Тагните Клинфа."
        )
        logger.error(err)


@superuser_command
async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.replace("/demote", "").strip()
        DbPlayerConfig().promote_or_demote(text, False)
    except Exception as err:
        await context.bot.send_message(
            update.effective_chat.id, "Ошибка. Тагните Клинфа."
        )
        logger.error(err)


@admin_command
async def view_all_players(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        palyers = DbPlayerConfig().get_all_players()
        res = ""
        for player in palyers:
            res = "\n".join([res, str(player), "______"])
        await context.bot.send_message(update.effective_chat.id, res)
    except Exception as err:
        await context.bot.send_message(
            update.effective_chat.id, "Ошибка. Тагните Клинфа."
        )
        logger.error(err)
