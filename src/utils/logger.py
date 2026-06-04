import logging
from datetime import datetime

from core.settings import PROJECT_NAME, DEBUG
from core.paths import PATHS


def _build_logger(name: str) -> logging.Logger:
    """Create and configure the underlying logger instance."""
    logger = logging.getLogger(name)

    if not DEBUG:
        logger.disabled = True
        return logger

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    log_file = PATHS["logs"] / f"log_{datetime.now().strftime('%Y%m%d')}.log"

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


class Logger:
    """
    Thin wrapper around Python's standard logger.

    Usage:
        log = Logger()          # default project logger
        log = Logger("module")  # named module logger
    """

    _instances: dict[str, "Logger"] = {}
    _logger: logging.Logger

    def __new__(cls, name: str = PROJECT_NAME) -> "Logger":
        if name not in cls._instances:
            instance = super().__new__(cls)
            instance._logger = _build_logger(name)
            cls._instances[name] = instance
        return cls._instances[name]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def info(self, message: str) -> None:
        self._logger.info(message)

    def error(self, message: str) -> None:
        self._logger.error(message)

    def warning(self, message: str) -> None:
        self._logger.warning(message)

    def debug(self, message: str) -> None:
        self._logger.debug(message)
