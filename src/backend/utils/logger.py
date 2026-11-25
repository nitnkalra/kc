import logging

from config import LOG_DIR

# Log folder: src/backend/logs/ (git-ignored), defined in config/paths.py
_LOG_DIR  = LOG_DIR
_LOG_FILE = _LOG_DIR / "kc_leaderboard.log"


def get_logger() -> logging.Logger:
    """
    Return the 'kc' logger, creating file handler on first call.
    Log directory is resolved relative to the backend (src/backend/logs/),
    so the log lands in the same place regardless of cwd.
    """
    logger = logging.getLogger("kc")

    if logger.handlers:
        return logger

    _LOG_DIR.mkdir(exist_ok=True)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
