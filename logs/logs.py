import logging
from logging.handlers import RotatingFileHandler


def set_up_logger(logger_name, file_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler(
        file_name, maxBytes=50000000, backupCount=5, encoding="utf-8"
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(pathname)s - %(lineno)s - %(funcName)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


main_logger = set_up_logger("main", "main.log")
user_logger = set_up_logger("user_exc", "user_exc.log")
