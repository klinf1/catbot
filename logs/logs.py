import os
import platform

from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

from python_loki_logger import LokiLogger

load_dotenv()


def set_up_logger(logger_name):
    path = os.getenv("LOG_PATH")
    file_name = f"{path}main.log"
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler(file_name, maxBytes=50000000, backupCount=5, encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(pathname)s - %(lineno)s - %(funcName)s - %(message)s"
    )
    out_handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    out_handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.addHandler(out_handler)
    return logger


def set_up_logger_linux():
    url, user, passw = os.environ["GRAPHANA_URL"], os.environ["GRAPHANA_USER"], os.environ["GRAPHANA_PASS"]
    if os.environ["TEST_MODE"].lower() == "true":
        env = "test"
    else:
        env = "prod"
    logger = LokiLogger(
        baseUrl=url,
        auth=(
            user,
            passw,
        ),
        labels={"app": "catbot", "env": env},
    )
    return logger


if platform.system() == "Windows":
    logger = set_up_logger("main")
else:
    logger = set_up_logger_linux()
