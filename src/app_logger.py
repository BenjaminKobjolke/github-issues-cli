"""The single logging entry point for the project.

This is the only module that imports `logging`. Everything else calls `AppLogger`,
so verbosity is one toggle (`AppLogger.configure`) rather than a decision at every
call site. Diagnostics go here; the CLI's actual result lines are `print`ed by
`cli.py` because they are the program's output, not diagnostics.
"""

from __future__ import annotations

import logging
import sys

_LOGGER_NAME = "github-issues-cli"
_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class AppLogger:
    """Static wrapper over one stdlib logger."""

    _logger: logging.Logger | None = None

    @classmethod
    def configure(cls, verbose: bool) -> None:
        """Set up the underlying logger. Safe to call more than once."""
        logging.basicConfig(
            level=logging.INFO if verbose else logging.ERROR,
            format=_LOG_FORMAT,
            stream=sys.stdout,
            force=True,
        )
        cls._logger = logging.getLogger(_LOGGER_NAME)

    @classmethod
    def _get(cls) -> logging.Logger:
        if cls._logger is None:
            cls.configure(verbose=False)
        assert cls._logger is not None
        return cls._logger

    @classmethod
    def debug(cls, message: str) -> None:
        cls._get().debug(message)

    @classmethod
    def info(cls, message: str) -> None:
        cls._get().info(message)

    @classmethod
    def warning(cls, message: str) -> None:
        cls._get().warning(message)

    @classmethod
    def error(cls, message: str) -> None:
        cls._get().error(message)
