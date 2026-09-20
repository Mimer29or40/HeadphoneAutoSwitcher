"""Infrastructure runner, as described by Clean Architecture."""

from __future__ import annotations

import logging
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

    from application.base import BaseApplication


logger: Logger = logging.getLogger("infrastructure.runner")


class BaseRunner(ABC):
    """Base runner class, implementing Clean Architecture patterns."""

    application: BaseApplication

    @property
    @abstractmethod
    def is_running(self) -> bool:
        """True, if the application is running, False otherwise."""

    @abstractmethod
    def start(self) -> None:
        """Start the application."""

    @abstractmethod
    def stop(self) -> None:
        """Stop the application."""


# ---------- Project Specific ---------- #
