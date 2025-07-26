import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (Application, CallbackQueryHandler, ContextTypes,
                          MessageHandler, filters)

from bot.commands import CallbackRouter, CommandRouter, ConversationRouter
from bot.errors import ErrorHandler

load_dotenv()


async def command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await CommandRouter(update, context).route()


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    await ErrorHandler(context, os.getenv("DEV_ID")).route()  # type: ignore


async def conversation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ConversationRouter(update, context).route()


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await CallbackRouter(update, context).route()


def bot_main(token: str):
    app = Application.builder().token(token).build()
    app.add_handler(MessageHandler(filters.COMMAND, command_handler))
    app.add_handler(MessageHandler(filters.TEXT, conversation_handler))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_error_handler(error_handler)
    app.run_polling()
