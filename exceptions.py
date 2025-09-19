from telegram.error import TelegramError


class OwnException(BaseException):
    def __init__(self, text: str, *args) -> None:
        super().__init__(*args)
        self.text = text


class CharacterFrozenException(Exception):
    pass


class CharacterDeadException(Exception):
    pass


class NoRightException(TelegramError):
    pass


class BannedException(TelegramError):
    pass


class EditError(OwnException):
    pass


class NoItemFoundDbError(Exception):
    pass


class WrongChatError(Exception):
    pass


class NotRealClanError(Exception):
    pass
