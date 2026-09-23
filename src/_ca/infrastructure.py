"""Infrastructure layer, as described by Clean Architecture."""

from __future__ import annotations

import logging.config
import sys
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Never
from typing import override

if TYPE_CHECKING:
    from logging import Logger

    from _ca.application import BaseApplication


logger: Logger = logging.getLogger("infrastructure")


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


type FrameworkResult = str | int | None
FRAMEWORK_SUCCESS: FrameworkResult = 0
FRAMEWORK_FAILURE: FrameworkResult = -1


class BaseFramework(ABC):
    """Base framework class, implementing Clean Architecture patterns."""

    application: BaseApplication

    @abstractmethod
    def run(self, *args: Any) -> FrameworkResult:
        """Run the framework."""

    def main(self) -> Never:
        """Main entry point for the console application."""
        args: list[str] = sys.argv[1:]
        result: FrameworkResult = self.run(*args)
        sys.exit(result)
