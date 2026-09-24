"""Clean architecture presentation module."""

from __future__ import annotations

import logging.config
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

logger: Logger = logging.getLogger("ca.application")


class BaseApplicationContainer(ABC):
    """Base application container."""


class BaseApplicationFactory[A: BaseApplicationContainer](ABC):
    """Base application factory."""

    name: str
    description: str
    version: str

    @abstractmethod
    def create(self) -> A:
        """Create the application container."""
