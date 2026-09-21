"""Infrastructure logger, as described by Clean Architecture."""

from __future__ import annotations

import logging.config
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import override

if TYPE_CHECKING:
    from logging import Logger


logger: Logger = logging.getLogger("infrastructure.logger")


class LogConfigProvider(ABC):
    """Provider for logging configurations."""

    @abstractmethod
    def get(self) -> dict[str, Any]:
        """Get the logging configuration."""


@dataclass(frozen=True, slots=True)
class DefaultLogConfigProvider(LogConfigProvider):
    """Default logging configuration."""

    @override
    def get(self) -> dict[str, Any]:
        """Get the logging configuration."""
        return {"version": 1, "disable_existing_loggers": False, "handlers": [], "root": {"level": "WARNING"}}


def configure_logging(log_config: LogConfigProvider) -> None:
    """Configure logging module."""
    config: dict[str, Any] = log_config.get()

    logging.config.dictConfig(config)


# ---------- Project Specific ---------- #
