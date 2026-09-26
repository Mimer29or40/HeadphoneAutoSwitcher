"""Clean architecture infrastructure module."""

from __future__ import annotations

import logging.config
import sys
from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import Any
from typing import Never

from ca.application import BaseApplication
from ca.application import BaseApplicationFactory
from ca.domain import ErrorMsg
from ca.domain import FrameworkError
from ca.utils import log_call

if TYPE_CHECKING:
    from logging import Logger

logger: Logger = logging.getLogger("ca.infrastructure")


# ---------- Framework ---------- #


type FrameworkResult = str | int | None

FRAMEWORK_SUCCESS: FrameworkResult = 0
FRAMEWORK_FAILURE: FrameworkResult = 1
FRAMEWORK_ERROR: FrameworkResult = -1


class BaseFramework[A: BaseApplication](ABC):
    """Base framework class."""

    app_factory: BaseApplicationFactory[A]

    @abstractmethod
    def run_impl(self, *args: Any) -> FrameworkResult:
        """Run the Framework."""

    def run(self, *args: Any) -> FrameworkResult:
        """Run the Framework."""
        result: FrameworkResult
        try:
            logger.debug("Framework launched with args: %s", args)
            result = self.run_impl(*args)
            logger.debug("Framework result: %s", result)
        except FrameworkError as e:
            logger.critical("Framework error: %s", e.message, exc_info=False)
            result = FRAMEWORK_ERROR
        except KeyboardInterrupt:
            logger.critical("User interrupted")
            result = "USER_INTERRUPT"
        except Exception as e:
            logger.exception("Unhandled exception:", exc_info=e)
            result = FRAMEWORK_FAILURE
        return result

    def main(self) -> Never:
        """Main entry point for the Framework."""
        args: list[str] = sys.argv[1:]
        result: FrameworkResult = self.run(*args)
        sys.exit(result)


type CommandFrameworkCommand[A: BaseApplication] = Callable[[A], FrameworkResult]

COMMAND_FRAMEWORK_DEFAULT_CMD: str = "DEFAULT_COMMAND"

COMMAND_ALREADY_REGISTERED: ErrorMsg = ErrorMsg("Command already registered with that name.")
COMMAND_NOT_REGISTERED: ErrorMsg = ErrorMsg("Command not registered with that name.")


@dataclass(frozen=True, slots=True)
class CommandFramework[A: BaseApplication](BaseFramework[A], ABC):  # TODO(Ryan): Move to separate file
    """Framework that uses commands."""

    app_factory: BaseApplicationFactory[A]
    commands: dict[str, CommandFrameworkCommand[A]] = field(default_factory=dict, init=False)

    @log_call(type="method", level=logging.DEBUG)
    def register(self, name: str, command: CommandFrameworkCommand[A]) -> None:
        """Register a command with the Framework."""
        if name in self.commands:
            raise FrameworkError(COMMAND_ALREADY_REGISTERED)
        self.commands[name] = command

    @log_call(type="method", level=logging.DEBUG)
    def register_default(self, command: CommandFrameworkCommand[A]) -> None:
        """Register a command as the default action for the Framework."""
        self.register(COMMAND_FRAMEWORK_DEFAULT_CMD, command)

    @log_call(type="method", level=logging.DEBUG)
    def unregister(self, name: str) -> None:
        """Unregister a command with the Framework."""
        if name not in self.commands:
            raise FrameworkError(COMMAND_NOT_REGISTERED)
        self.commands.pop(name)


# ---------- Logging ---------- #


class LogConfigProvider(ABC):
    """Provider for logging configurations."""

    @abstractmethod
    def get(self) -> dict[str, Any]:
        """Get the logging configuration."""


@log_call(type="static")
def configure_logging(log_config: LogConfigProvider) -> None:
    """Configure logging module."""
    config: dict[str, Any] = log_config.get()

    logging.config.dictConfig(config)
