import logging
import os
import sys
import warnings
from typing import Literal

import structlog
from structlog.stdlib import BoundLogger
from structlog.types import Processor

LogFormat = Literal["console", "json"]
APP_LOGGER_NAME = "app"

_configured = False
_HUGGING_FACE_WARNING = "You are sending unauthenticated requests to the HF Hub."


class _HuggingFaceAuthenticationWarningFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return _HUGGING_FACE_WARNING not in record.getMessage()


_hugging_face_warning_filter = _HuggingFaceAuthenticationWarningFilter()


def suppress_model_loading_noise() -> None:
    """Hide known, non-actionable warnings emitted while loading Kokoro."""
    warnings.filterwarnings(
        "ignore",
        message=r"dropout option adds dropout after all but last recurrent layer.*",
        category=UserWarning,
        module=r"torch\.nn\.modules\.rnn",
    )
    warnings.filterwarnings(
        "ignore",
        message=(
            r"`torch\.nn\.utils\.weight_norm` is deprecated in favor of "
            r"`torch\.nn\.utils\.parametrizations\.weight_norm`\."
        ),
        category=FutureWarning,
        module=r"torch\.nn\.utils\.weight_norm",
    )

    hugging_face_logger = logging.getLogger("huggingface_hub.utils._http")
    if _hugging_face_warning_filter not in hugging_face_logger.filters:
        hugging_face_logger.addFilter(_hugging_face_warning_filter)


def setup_logging(
    *,
    log_format: LogFormat | None = None,
    log_level: str | None = None,
) -> None:
    global _configured

    selected_format = _resolve_format(log_format)
    selected_level = _resolve_level(log_level)

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]
    if selected_format == "json":
        shared_processors.append(structlog.processors.format_exc_info)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=False,
    )

    renderer: Processor = (
        structlog.processors.JSONRenderer()
        if selected_format == "json"
        else structlog.dev.ConsoleRenderer()
    )
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(logging.NullHandler())
    root_logger.setLevel(logging.CRITICAL + 1)

    application_logger = logging.getLogger(APP_LOGGER_NAME)
    application_logger.handlers.clear()
    application_logger.addHandler(handler)
    application_logger.setLevel(selected_level)
    application_logger.propagate = False

    _configured = True


def get_logger(name: str | None = None) -> BoundLogger:
    if not _configured:
        setup_logging()
    return structlog.stdlib.get_logger(_application_logger_name(name))


def _application_logger_name(name: str | None) -> str:
    if not name or name == APP_LOGGER_NAME:
        return APP_LOGGER_NAME
    if name.startswith(f"{APP_LOGGER_NAME}."):
        return name
    return f"{APP_LOGGER_NAME}.{name}"


def _resolve_format(log_format: str | None) -> LogFormat:
    selected = (log_format or os.getenv("LOG_FORMAT") or "console").lower()
    if selected == "console":
        return "console"
    if selected == "json":
        return "json"
    raise ValueError(
        f"Unknown log format: {selected!r}. Expected one of: console, json"
    )


def _resolve_level(log_level: str | None) -> int:
    selected = (log_level or os.getenv("LOG_LEVEL") or "INFO").upper()
    level_names = logging.getLevelNamesMapping()
    if selected not in level_names:
        raise ValueError(f"Unknown log level: {selected}")
    return level_names[selected]
