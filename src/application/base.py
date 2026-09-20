"""Application layer base."""

from __future__ import annotations

import logging
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger


logger: Logger = logging.getLogger("application")


class BaseApplication(ABC):
    """Base application class, implementing Clean Architecture patterns."""

    name: str
    description: str
    version: str

    @abstractmethod
    def __post_init__(self) -> None:
        """Wire up use cases and controllers."""


# ---------- Project Specific ---------- #
