import logging
from enum import Enum


class Status(str, Enum):
    CACHE_HIT = "CACHE_HIT"
    SAVING = "SAVING"
    LOADING = "LOADING"
    COMPUTING = "COMPUTING"


def init(level: str = "INFO"):  # pragma: no cover
    logging.basicConfig()
    logger = logging.getLogger()
    logger.setLevel(level)
    return logger
