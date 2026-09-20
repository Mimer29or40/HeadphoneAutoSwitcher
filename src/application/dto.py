"""Application data transfer objects (DTOs), as described by Clean Architecture."""

from __future__ import annotations

import logging
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any
from typing import Self

from domain.entity import BaseEntity

if TYPE_CHECKING:
    from logging import Logger


logger: Logger = logging.getLogger("application.dto")


class BaseRequest(ABC):
    """Base request class, implementing Clean Architecture patterns."""

    @abstractmethod
    def __post_init__(self) -> None:
        """Validate request data."""

    @abstractmethod
    def convert(self) -> dict[str, Any]:
        """Convert the requested data to a standardized form."""


class BaseResponse[T: BaseEntity](ABC):
    """Base response class, implementing Clean Architecture patterns."""

    @classmethod
    @abstractmethod
    def from_entity(cls, entity: T) -> Self:
        """Create a Response from an Entity."""


class BaseOutcome(ABC):
    """Base outcome class, implementing Clean Architecture patterns."""

    @abstractmethod
    def __str__(self) -> str:
        """Convert the outcome into a human-readable string."""


# ---------- Project Specific ---------- #
