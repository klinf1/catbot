import os

from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

load_dotenv()


def set_up_logger(logger_name, file_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler(
        file_name, maxBytes=50000000, backupCount=5, encoding="utf-8"
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(pathname)s - %(lineno)s - %(funcName)s - %(message)s"
    )
    out_handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    out_handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.addHandler(out_handler)
    return logger


path = os.environ['LOG_PATH']


main_logger = set_up_logger("main", f"{path}main.log")
user_logger = set_up_logger("user_exc", f"{path}user_exc.log")
schedule_logger = set_up_logger("schedule_logger", f"{path}schedule.log")
system_logger = set_up_logger("system_logger", f"{path}system.log")
