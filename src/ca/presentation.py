"""Clean architecture presentation module."""

from __future__ import annotations

import logging.config
import sys
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any
from typing import Never

from ca.application import BaseApplicationContainer
from ca.application import BaseApplicationFactory

if TYPE_CHECKING:
    from logging import Logger

logger: Logger = logging.getLogger("ca.presentation")


type FrameworkResult = str | int | None

FRAMEWORK_SUCCESS: FrameworkResult = 0
FRAMEWORK_FAILURE: FrameworkResult = -1


class BaseFramework[A: BaseApplicationContainer](ABC):
    """Base framework class."""

    app_factory: BaseApplicationFactory[A]

    @abstractmethod
    def run(self, *args: Any) -> FrameworkResult:
        """Run the framework."""

    def main(self) -> Never:
        """Main entry point for the framework."""
        args: list[str] = sys.argv[1:]
        result: FrameworkResult = self.run(*args)
        sys.exit(result)


class LogConfigProvider(ABC):
    """Provider for logging configurations."""

    @abstractmethod
    def get(self) -> dict[str, Any]:
        """Get the logging configuration."""


def configure_logging(log_config: LogConfigProvider) -> None:
    """Configure logging module."""
    config: dict[str, Any] = log_config.get()

    logging.config.dictConfig(config)
