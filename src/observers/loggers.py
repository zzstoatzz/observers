"""Module for logging utilities."""

import logging
from collections.abc import Callable
from datetime import datetime
from functools import lru_cache, partial
from typing import NotRequired, TypedDict

from rich.logging import RichHandler
from rich.markup import escape
from rich.text import Text

from observers import settings

FormatTimeCallable = Callable[[datetime], Text]


class RichHandlerKwargs(TypedDict):
    log_time_format: NotRequired[str | FormatTimeCallable]


class ObserverLogger(logging.Logger):
    """A subclass of the standard library `logging.Logger` class that adds methods for
    logging with styles and key-value pairs.
    """

    def __init__(self, name: str, level: int = logging.NOTSET) -> None:
        super().__init__(name, level)

    def debug_style(self, message: str, style: str | None = None) -> None: ...

    def info_style(self, message: str, style: str | None = None) -> None: ...

    def warning_style(self, message: str, style: str | None = None) -> None: ...

    def error_style(self, message: str, style: str | None = None) -> None: ...

    def critical_style(
        self, message: str, style: str | None = None
    ) -> None: ...

    def debug_kv(
        self,
        key: str,
        value: str,
        key_style: str = 'green',
        value_style: str = 'default on default',
        delimiter: str = ': ',
    ) -> None: ...

    def info_kv(
        self,
        key: str,
        value: str,
        key_style: str = 'blue',
        value_style: str = 'default on default',
        delimiter: str = ': ',
    ) -> None: ...

    def warning_kv(
        self,
        key: str,
        value: str,
        key_style: str = 'yellow',
        value_style: str = 'default on default',
        delimiter: str = ': ',
    ) -> None: ...

    def error_kv(
        self,
        key: str,
        value: str,
        key_style: str = 'red',
        value_style: str = 'default on default',
        delimiter: str = ': ',
    ) -> None: ...

    def critical_kv(
        self,
        key: str,
        value: str,
        key_style: str = 'red',
        value_style: str = 'default on default',
        delimiter: str = ': ',
    ) -> None: ...


logging.setLoggerClass(ObserverLogger)


@lru_cache
def get_logger(
    name: str | None = None,
) -> ObserverLogger:
    """
    Retrieves a logger with the given name, or the root logger if no name is given.

    Args:
        name: The name of the logger to retrieve.

    Returns:
        The logger with the given name, or the root logger if no name is given.

    Example:
        Basic Usage of `get_logger`
        ```python
        from assistant.utilities.loggers import get_logger

        logger = get_logger("assistant.test")
        logger.info("This is a test") # Output: assistant.test: This is a test

        debug_logger = get_logger("assistant.debug")
        debug_logger.debug_kv("TITLE", "log message", "green")
        ```
    """
    parent_logger = logging.getLogger('assistant')

    if name:
        # Append the name if given but allow explicit full names e.g. "assistant.test"
        # should not become "assistant.assistant.test"
        if not name.startswith(parent_logger.name + '.'):
            logger = parent_logger.getChild(name)
        else:
            logger = logging.getLogger(name)
    else:
        logger = parent_logger

    add_logging_methods(logger)
    return logger  # type: ignore


def setup_logging(
    level: str | None = None,
    log_time_format: str | FormatTimeCallable | None = None,
) -> None:
    logger: ObserverLogger = get_logger()

    if level is not None:
        logger.setLevel(level)
    else:
        logger.setLevel(settings.log_level)

    logger.handlers.clear()

    show_time = log_time_format is not None

    handler_kwargs: RichHandlerKwargs = {}
    if show_time and log_time_format is not None:
        handler_kwargs['log_time_format'] = log_time_format

    handler = RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_path=False,
        show_level=True,
        show_time=show_time,
        enable_link_path=True,
        omit_repeated_times=True,
        **handler_kwargs,
    )

    formatter = logging.Formatter('%(name)s: %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False


def add_logging_methods(logger: logging.Logger) -> None:
    def log_style(level: int, message: str, style: str | None = None):
        if level == logging.INFO:
            if message.startswith('›') or message.startswith('⋮'):
                # Keep existing hierarchy markers
                pass
            elif '│' in message:
                # Indent nested items
                message = f'  {message}'
            else:
                # Add hierarchy marker for top-level items
                message = f'⋮ {message}'

        if not style:
            style = 'default on default'
        message = f'[{style}]{escape(str(message))}[/]'
        logger.log(level, message, extra={'markup': True})

    def log_kv(
        level: int,
        key: str,
        value: str,
        key_style: str = 'default on default',
        value_style: str = 'default on default',
        delimiter: str = ': ',
    ):
        logger.log(
            level,
            f'[{key_style}]{escape(str(key))}{delimiter}[/][{value_style}]{escape(str(value))}[/]',
            extra={'markup': True},
        )

    setattr(logger, 'debug_style', partial(log_style, logging.DEBUG))
    setattr(logger, 'info_style', partial(log_style, logging.INFO))
    setattr(logger, 'warning_style', partial(log_style, logging.WARNING))
    setattr(logger, 'error_style', partial(log_style, logging.ERROR))
    setattr(logger, 'critical_style', partial(log_style, logging.CRITICAL))

    setattr(logger, 'debug_kv', partial(log_kv, logging.DEBUG))
    setattr(logger, 'info_kv', partial(log_kv, logging.INFO))
    setattr(logger, 'warning_kv', partial(log_kv, logging.WARNING))
    setattr(logger, 'error_kv', partial(log_kv, logging.ERROR))
    setattr(logger, 'critical_kv', partial(log_kv, logging.CRITICAL))
