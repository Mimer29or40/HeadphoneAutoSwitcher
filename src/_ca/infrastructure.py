"""Infrastructure layer, as described by Clean Architecture."""

from __future__ import annotations

import json
import logging.config
import sys
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Never
from typing import override

from _ca.application import BaseConfig
from _ca.application import BaseConfigProvider

if TYPE_CHECKING:
    from logging import Logger
    from pathlib import Path

    from _ca.application import BaseApplication


logger: Logger = logging.getLogger("infrastructure")


@dataclass(frozen=True, slots=True)
class MemoryConfigProvider[C: BaseConfig](BaseConfigProvider[C]):
    """ConfigProvider that loads a config from memory."""

    data: dict[str, Any]
    config_cls: type[C]

    def get(self) -> C:
        """Get the configuration."""
        return self.config_cls(**self.data)


@dataclass(frozen=True, slots=True)
class JsonConfigProvider[C: BaseConfig](BaseConfigProvider[C]):
    """ConfigProvider that loads a config from a JSON file."""

    file: Path
    config_cls: type[C]

    def get(self) -> C:
        """Get the configuration."""
        data: dict[str, Any] = json.loads(self.file.read_text())
        return self.config_cls(**data)


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


class BaseFramework[A: BaseApplication](ABC):
    """Base framework class, implementing Clean Architecture patterns."""

    application: A

    @abstractmethod
    def run(self, *args: Any) -> FrameworkResult:
        """Run the framework."""

    def main(self) -> Never:
        """Main entry point for the console application."""
        args: list[str] = sys.argv[1:]
        result: FrameworkResult = self.run(*args)
        sys.exit(result)
