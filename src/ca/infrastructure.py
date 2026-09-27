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
from ca.domain import BaseError
from ca.domain import ErrorMsg
from ca.domain import FrameworkError
from ca.utils import log_call

if TYPE_CHECKING:
    from logging import Logger

logger: Logger = logging.getLogger("ca.infrastructure")


# ---------- Framework ---------- #


type FrameworkResult = str | int | None

RESULT_SUCCESS: FrameworkResult = 0
RESULT_FAILURE: FrameworkResult = 1
RESULT_USER_INTERRUPT: FrameworkResult = "USER_INTERRUPT"
RESULT_EXCEPTION: FrameworkResult = -1


class BaseFramework[A: BaseApplication](ABC):
    """Base framework class."""

    app_factory: BaseApplicationFactory[A]

    @abstractmethod
    @log_call(type="method")
    def run_impl(self, *args: Any) -> FrameworkResult:  # TODO(Ryan): run_impl(self, args: tuple[Any])
        """Run the Framework."""

    @log_call(type="method")
    def run(self, *args: Any) -> FrameworkResult:
        """Run the Framework."""
        result: FrameworkResult
        try:
            logger.debug("Framework launched with args: %s", args)
            result = self.run_impl(*args)
            logger.debug("Framework result: %s", result)
        except BaseError as e:
            logger.critical("Application error: %s", e.message, exc_info=False)
            result = RESULT_FAILURE
        except KeyboardInterrupt:
            logger.critical("User interrupt received.", exc_info=False)
            result = RESULT_USER_INTERRUPT
        except Exception as e:
            logger.exception("Unhandled exception:", exc_info=e)
            result = RESULT_EXCEPTION
        return result

    @log_call(type="method")
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

    @log_call(type="method")
    def register(self, name: str, command: CommandFrameworkCommand[A]) -> None:
        """Register a command with the Framework."""
        if name in self.commands:
            raise FrameworkError(COMMAND_ALREADY_REGISTERED)
        self.commands[name] = command

    @log_call(type="method")
    def register_default(self, command: CommandFrameworkCommand[A]) -> None:
        """Register a command as the default action for the Framework."""
        self.register(COMMAND_FRAMEWORK_DEFAULT_CMD, command)

    @log_call(type="method")
    def unregister(self, name: str) -> None:
        """Unregister a command with the Framework."""
        if name not in self.commands:
            raise FrameworkError(COMMAND_NOT_REGISTERED)
        self.commands.pop(name)


# ---------- Logging ---------- #


class LogConfigProvider(ABC):
    """Provider for logging configurations."""

    @abstractmethod
    @log_call(type="method")
    def get(self) -> dict[str, Any]:
        """Get the logging configuration."""


@log_call(type="static")
def configure_logging(log_config: LogConfigProvider) -> None:
    """Configure logging module."""
    config: dict[str, Any] = log_config.get()

    logging.config.dictConfig(config)
