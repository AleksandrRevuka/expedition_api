import sys

from loguru import logger

__all__ = ["LOGGER"]

logger.remove()
logger.add(
    sys.stdout,
    format="<yellow>[{time:YYYY-MM-DD HH:mm:ss}]</yellow> <level>{level: <8}</level> <cyan>{module}:{line}</cyan> {message}",
    colorize=True,
    level="DEBUG",
)

LOGGER = logger
