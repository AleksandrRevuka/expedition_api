import traceback
from types import TracebackType

from fastapi import Request

from src.common.utils.color_message import color_message
from src.conf.logging_config import LOGGER


def exc_name(ex: Exception) -> str:
    return f"{ex.__class__.__name__}: {ex}"


def exc_name_without_ex(exc: Exception) -> str:
    return f"{exc.__class__.__name__}"


def log_wrapper(request: Request, exc: Exception, status_code: int) -> None:
    tb: TracebackType | None = exc.__traceback__

    LOGGER.error(color_message(f"{'Start ' + str(status_code) + ' Error':-^100}", "error"))
    LOGGER.error(color_message("url: ", "error") + f"{request.method}, {request.url}")
    LOGGER.error(color_message("exc_type: ", "error") + f"{exc_name_without_ex(exc)}")

    if hasattr(exc, "errors") and callable(exc.errors):
        for index, err in enumerate(exc.errors(), 1):  # type: ignore
            LOGGER.error(color_message(f"   ─ Error #{index} ─", "error"))
            for key, val in err.items():
                if key == "loc":
                    loc_str = " → ".join(str(x) for x in val)
                    LOGGER.error(color_message("       loc: ", "error") + loc_str)
                elif key == "ctx" and isinstance(val, dict):
                    for ctx_key, ctx_val in val.items():
                        LOGGER.error(
                            color_message(f"       ctx.{ctx_key}: ", "error") + str(ctx_val)
                        )
                else:
                    LOGGER.error(color_message(f"       {key}: ", "error") + str(val))
    else:
        LOGGER.error(color_message("exc_message: ", "error") + repr(exc))

    if tb:
        last_trace = traceback.format_tb(tb)[-1]
        formatted_trace = "\n".join([" " * 63 + line for line in last_trace.splitlines()])
        LOGGER.debug(color_message("Traceback:", "error") + f"\n{formatted_trace}")

    LOGGER.error(color_message(f"{'End ' + str(status_code) + ' Error':-^100}", "error"))
