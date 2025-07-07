from sqlmodel import Session, select
from telegram import Update
from telegram.ext import ContextTypes

from db import Players, engine
from db.exceptions import BannedException, NoRightException
from db.players import DbPlayerConfig
from logs.logs import main_logger as logger


def register_player_if_not_exists(func):
    def wrapper(update: Update, *args, **kwargs):
        tg_user = update.message.from_user
        query = select(Players).where(Players.chat_id == tg_user.id)
        with Session(engine) as s:
            res = s.exec(query).all()
            if not res:
                DbPlayerConfig().add_player(
                    tg_user.id, tg_user.username, tg_user.first_name, tg_user.last_name
                )
                logger.info(f"Игрок {tg_user.id} {tg_user.username} зарегистрирован")
        return func(update, *args, **kwargs)

    return wrapper


def admin_command(func):
    def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        tg_user = update.message.from_user
        query = select(Players).where(Players.chat_id == tg_user.id)
        with Session(engine) as s:
            user = s.exec(query).one()
        if user.is_admin is False and user.is_superuser is False:
            context.chat_data.update(
                {"exc": {"admin_error": [user.chat_id, user.username]}}
            )
            raise NoRightException("No rights!")
        return func(update, context, *args, **kwargs)

    return wrapper


def not_banned(func):
    def wrapper(self, *args, **kwargs):
        tg_user = self.user
        query = select(Players).where(Players.chat_id == tg_user.id)
        with Session(engine) as s:
            user = s.exec(query).one()
        if user.is_banned:
            self.context.chat_data.update(
                {"exc": {"banned": [user.chat_id, user.username]}}
            )
            raise BannedException("Banned af")
        return func(self, *args, **kwargs)

    return wrapper


def superuser_command(func):
    def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        tg_user = update.message.from_user
        query = select(Players).where(Players.chat_id == tg_user.id)
        with Session(engine) as s:
            user = s.exec(query).one()
        if user.is_superuser is False:
            context.chat_data.update(
                {"exc": {"superuser_error": [user.chat_id, user.username]}}
            )
            raise NoRightException("No rights!")
        return func(update, context, *args, **kwargs)

    return wrapper
