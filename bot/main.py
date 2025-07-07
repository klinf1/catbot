import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from bot.admin.characters import add_char, add_char_help, view_chars_by_player
from bot.admin.clans import add_clan, add_clan_help
from bot.admin.injuries import add_injury, add_injury_help
from bot.admin.players import ban, demote, promote, unban, view_all_players
from bot.admin.prey import add_prey, add_prey_help, view_all_prey
from bot.hunt import hunt, hunt_help
from db.decorators import not_banned, register_player_if_not_exists
from db.players import DbPlayerConfig
from logs.logs import main_logger, user_logger

load_dotenv()


@register_player_if_not_exists
@not_banned
async def commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = "\n".join(
        [
            "Доступные на текущий момент команды:",
            "health - если бот ответил, значит он работает!",
            "hunt",
            "hunt_help",
        ]
    )
    try:
        if DbPlayerConfig().check_if_user_is_admin(update.message.from_user.id):
            commands = "\n".join(
                [
                    commands,
                    "add_char",
                    "add_clan",
                    "add_prey",
                    "add_prey_help",
                    "add_char_help",
                    "add_clan_help",
                    "ban [username]",
                    "unban [username]",
                    "view_all_prey",
                    "view_chars_by_player [username]",
                    "promote [username]",
                    "demote [username]",
                    "view_all_players",
                    "add_injury",
                    "add_injury_help",
                ]
            )
    except Exception as err:
        main_logger.error(f"Ошибка проверки прав админа: {err}")
    await context.bot.send_message(update.effective_chat.id, commands)


@register_player_if_not_exists
async def health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.effective_chat.id, "I'm here for you!")


@register_player_if_not_exists
@not_banned
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id > 0:
        await context.bot.send_message(update.effective_chat.id, "Добро пожаловать!")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    if not context.chat_data:
        main_logger.exception(context.error)
        await context.bot.send_message(os.getenv("DEV_ID"), str(context.error))
    if "admin_error" in context.chat_data.keys():
        user_logger.info(
            f"{context.chat_data['admin_error'][1]} хотел использовать админскую комманду!"
        )
        context.chat_data.__delitem__("admin_error")
    if "banned" in context.chat_data.keys():
        user_logger.info(
            f"{context.chat_data['banned'][1]} забанен, но очень хочет играть."
        )
        await context.bot.send_message(context.chat_data["banned"][0], "Вы в бане!")
        context.chat_data.__delitem__("banned")
    if "superuser_error" in context.chat_data.keys():
        user_logger.info(
            f"{context.chat_data['admin_error'][1]} хотел использовать команду суперюзера!"
        )
        context.chat_data.__delitem__("superuser_error")


def bot_main(token: str):
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("health", health))
    app.add_handler(CommandHandler("commands", commands))
    app.add_handler(CommandHandler("hunt", hunt))
    app.add_handler(CommandHandler("hunt_help", hunt_help))
    app.add_handler(CommandHandler("add_char", add_char))
    app.add_handler(CommandHandler("add_clan", add_clan))
    app.add_handler(CommandHandler("add_prey", add_prey))
    app.add_handler(CommandHandler("add_prey_help", add_prey_help))
    app.add_handler(CommandHandler("add_char_help", add_char_help))
    app.add_handler(CommandHandler("add_clan_help", add_clan_help))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("view_all_prey", view_all_prey))
    app.add_handler(CommandHandler("view_chars_by_player", view_chars_by_player))
    app.add_handler(CommandHandler("promote", promote))
    app.add_handler(CommandHandler("demote", demote))
    app.add_handler(CommandHandler("view_all_players", view_all_players))
    app.add_handler(CommandHandler("add_injury", add_injury))
    app.add_handler(CommandHandler("add_injury_help", add_injury_help))
    app.add_error_handler(error_handler)
    app.run_polling()
