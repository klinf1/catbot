from sqlmodel import Session, select

from db import Players, engine
from db.exceptions import BannedException, NoRightException


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
    def wrapper(self, *args, **kwargs):
        tg_user = self.user
        query = select(Players).where(Players.chat_id == tg_user.id)
        with Session(engine) as s:
            user = s.exec(query).one()
        if user.is_superuser is False:
            self.context.chat_data.update(
                {"exc": {"superuser_error": [user.chat_id, user.username]}}
            )
            raise NoRightException("No rights!")
        return func(self, *args, **kwargs)

    return wrapper
