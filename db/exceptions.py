from telegram.error import TelegramError


class CharacterFrozenException(Exception):
    pass


class CharacterDeadException(Exception):
    pass


class NoRightException(TelegramError):
    pass


class BannedException(TelegramError):
    pass
