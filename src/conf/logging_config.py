import sys
from typing import TYPE_CHECKING

from loguru import logger as LOGGER

if TYPE_CHECKING:
    from loguru import Record

__all__ = ["LOGGER"]


def formatter(record: "Record") -> str:
    from datetime import datetime

    time = datetime.fromtimestamp(record["time"].timestamp())
    asctime = time.strftime("%Y-%m-%d %H:%M:%S")
    msecs = f"{int(record['time'].microsecond / 1000):03d}"

    level = record["level"].name
    module_line = f"{record['module']}:{record['line']}".ljust(25)
    message = record["message"]

    if level == "INFO":
        level_formatted = f"<g><bold>{level.ljust(8)}</bold></g>"
    else:
        level_formatted = f"<level><bold>{level.ljust(8)}</bold></level>"

    return (
        f"<yellow>[{asctime}</yellow>"
        f"<yellow>.{msecs}]</yellow> "
        f"{level_formatted} "
        f"<cyan>{module_line}</cyan> "
        f"<n>{message}</n>\n"
    )


LOGGER.remove()
LOGGER.add(sys.stdout, format=formatter, colorize=True, level="DEBUG")
