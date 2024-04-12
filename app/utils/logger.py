import os
import logging
from pythonjsonlogger import jsonlogger

from logging.handlers import TimedRotatingFileHandler


def setup_logger():
    logger = logging.getLogger("MyLogger")

    log_format = "%(asctime)s - %(levelname)s - %(message)s"

    # if we are unable to determine environment default to 'prod' settings
    if os.getenv("ENV") == "dev":
        log_handler = logging.StreamHandler()
        formatter = logging.Formatter(log_format)
        logger.setLevel(logging.DEBUG)
    else:
        log_name = "app.log"
        log_handler = TimedRotatingFileHandler(
            log_name, when="midnight", backupCount=30
        )
        log_handler.suffix = "%Y%m%d"
        formatter = jsonlogger.JsonFormatter(log_format)
        logger.setLevel(logging.INFO)

    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

    return logger


log = setup_logger()
