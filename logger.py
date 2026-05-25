import logging
import os
from logging.handlers import RotatingFileHandler

from config import DATA_DIR

LOG_DIR = os.path.join(str(DATA_DIR), "logs")

try:
    os.makedirs(LOG_DIR, exist_ok=True)
except OSError:
    LOG_DIR = os.path.join("/tmp", "mabyte_logs")
    os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "Mabyte.log")

logger = logging.getLogger("Mabyte")

logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s"
)

file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=5 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8"
)

file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def log_info(message):
    logger.info(message)


def log_error(message):
    logger.error(message)


def log_warning(message):
    logger.warning(message)

