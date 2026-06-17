import logging
from pathlib import Path


def get_logger():

    Path("logs").mkdir(exist_ok=True)

    logger = logging.getLogger("kc")

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(
        "logs/kc_leaderboard.log",
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger