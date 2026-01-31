import os
from typing import Literal

from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

from python_loki_logger import LokiLogger

load_dotenv()


def _set_up_logger(logger_name):
    path = os.getenv("LOG_PATH", "files/")
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


def _set_up_logger_linux():
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


class LoggingCommand:
    _logger = None
    _file_logger = None

    def __init__(self, log_labels: dict = {}, log_extras: dict = {}):
        self.log_labels = log_labels
        self.log_extras = log_extras
        self._logger = _set_up_logger_linux()
        self._file_logger = _set_up_logger(__name__)

    def write_log(
        self,
        level: Literal["debug", "info", "warn", "error", "exception"],
        message: str | dict,
        extras: dict = {},
        labels: dict = {},
    ):
        if not all([self._logger, self._file_logger]):
            return None
        labels.update(self.log_labels)
        extras.update(self.log_extras)
        getattr(self._logger, level)(message=message, extras=extras, labels=labels)
        getattr(self._file_logger, level)(message)

    def debug(self, message: str | dict, extras: dict = {}, labels: dict = {}):
        return self.write_log("debug", message, extras, labels)

    def info(self, message: str | dict, extras: dict = {}, labels: dict = {}):
        return self.write_log("info", message, extras, labels)

    def warn(self, message: str | dict, extras: dict = {}, labels: dict = {}):
        return self.write_log("warn", message, extras, labels)

    def error(self, message: str | dict, extras: dict = {}, labels: dict = {}):
        return self.write_log("error", message, extras, labels)

    def exception(self, message: str | dict, extras: dict = {}, labels: dict = {}):
        return self.write_log("exception", message, extras, labels)
