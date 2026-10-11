import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

def warning(message):
    logger.warning(message)

def error(message):
    logger.error(message)

def critical(message):
    logger.critical(message)

def debug(message):
    logger.debug(message)
    return logging.getLogger(__name__)