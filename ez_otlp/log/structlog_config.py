"""https://www.structlog.org/"""

from dataclasses import dataclass, field
from typing import Callable

import logging
from datetime import datetime, timezone

import orjson
from opentelemetry._logs import std_to_otel
from opentelemetry.sdk._logs._internal import LoggerProvider, LogRecord
from opentelemetry.trace import get_current_span

import structlog
from structlog._log_levels import NAME_TO_LEVEL
from structlog.types import BindableLogger, Processor, WrappedLogger


@dataclass
class StructLoggingConfig:
    processors: list[Processor] | None = field(default=None)
    wrapper_class: type[BindableLogger] | None = field(default=None)
    logger_factory: Callable[..., WrappedLogger] | None = field(default=None)
    cache_logger_on_first_use: bool = field(default=True)

    def configure(self):
        structlog.configure(
            processors=self.processors,
            wrapper_class=self.wrapper_class,
            logger_factory=self.logger_factory,
            cache_logger_on_first_use=self.cache_logger_on_first_use,
        )
        return structlog.get_logger


_EXCLUDE_ATTRS = {"exception", "timestamp"}

_dumps = orjson.dumps


class StructlogHandler:
    def __init__(self, logger_provider: LoggerProvider) -> None:
        self._logger = logger_provider.get_logger(__name__)

    def __call__(
        self,
        logger: structlog.typing.WrappedLogger,
        name: str,
        event_dict: structlog.typing.EventDict,
    ):
        span_context = get_current_span().get_span_context()
        severity_number = std_to_otel(NAME_TO_LEVEL[event_dict["level"]])
        attributes = {
            k: v if isinstance(v, (bool, str, bytes, int, float)) else _dumps(v)
            for k, v in event_dict.items()
            if k not in _EXCLUDE_ATTRS
        }

        self._logger.emit(
            LogRecord(
                timestamp=int(datetime.now(timezone.utc).timestamp() * 1e9),
                trace_id=span_context.trace_id,
                span_id=span_context.span_id,
                trace_flags=span_context.trace_flags,
                severity_text=event_dict["level"],
                severity_number=severity_number,
                body=event_dict["event"],
                resource=self._logger.resource,
                attributes=attributes,
            )
        )
        return event_dict


def get_struct_logging_config(
    logger_provider: LoggerProvider = None,
    log_lever: int = logging.DEBUG,
    output:bool = False,
) -> StructLoggingConfig:
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
    ]
    if logger_provider:
        processors.append(StructlogHandler(logger_provider))
    if output:
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer(serializer=_dumps))
    return StructLoggingConfig(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory() if output else structlog.BytesLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(log_lever),
        cache_logger_on_first_use=True,
    )
