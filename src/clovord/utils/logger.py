from __future__ import annotations

import logging

_LOGGER_NAME = "clovord"


def get_logger() -> logging.Logger:
    logger = logging.getLogger(_LOGGER_NAME)
    if logger.handlers:
        return logger

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[CLOVORD] %(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger
