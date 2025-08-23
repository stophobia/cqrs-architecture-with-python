import logging

import structlog
from decouple import config
from structlog.contextvars import merge_contextvars
from structlog.processors import (
    CallsiteParameter,
    CallsiteParameterAdder,
    EventRenamer,
    JSONRenderer,
    StackInfoRenderer,
    TimeStamper,
    UnicodeDecoder,
    format_exc_info,
)
from structlog.stdlib import (
    AsyncBoundLogger,
    LoggerFactory,
    PositionalArgumentsFormatter,
    filter_by_level,
    recreate_defaults,
)


def configure_logger() -> None:
    """Configure structlog with sane defaults for JSON logging."""

    recreate_defaults()

    shared_processors: list[structlog.types.Processor] = [
        merge_contextvars,
        filter_by_level,
        structlog.stdlib.add_log_level,
        PositionalArgumentsFormatter(),
        TimeStamper(fmt='iso'),
        StackInfoRenderer(),
        UnicodeDecoder(),
        CallsiteParameterAdder(
            {
                CallsiteParameter.FILENAME,
                CallsiteParameter.FUNC_NAME,
                CallsiteParameter.LINENO,
                CallsiteParameter.MODULE,
            }
        ),
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            EventRenamer('message'),
            format_exc_info,
            CallsiteParameterAdder(
                {
                    CallsiteParameter.PATHNAME,
                    CallsiteParameter.PROCESS,
                    CallsiteParameter.PROCESS_NAME,
                    CallsiteParameter.THREAD,
                    CallsiteParameter.THREAD_NAME,
                }
            ),
            JSONRenderer(default=str),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        wrapper_class=AsyncBoundLogger,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> AsyncBoundLogger:
    """Return a configured structlog logger."""
    if not logging.getLogger().handlers:
        configure_logger()

    def cast_log_level(value: str) -> int:
        return getattr(logging, value.upper(), logging.WARNING)

    root_logger = logging.getLogger()
    root_logger.setLevel(cast_log_level(config('LOG_LEVEL', default='WARNING')))
    return structlog.get_logger(name or __name__)
