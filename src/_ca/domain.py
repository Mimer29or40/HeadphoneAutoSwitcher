"""Domain layer base classes, as described by Clean Architecture."""

from __future__ import annotations

import logging
from abc import ABC
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import override
from uuid import UUID
from uuid import uuid4

if TYPE_CHECKING:
    from logging import Logger

logger: Logger = logging.getLogger("domain")


@dataclass(eq=False)
class BaseEntity(ABC):
    """Base entity class, implementing Clean Architecture patterns."""

    id: UUID = field(default_factory=uuid4, init=False)

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.id == other.id

    @override
    def __hash__(self) -> int:
        return hash(self.id)


@dataclass(frozen=True, slots=True)
class ErrorMsg:  # TODO(Ryan): Move to domain.value
    """Exception raised when an error occurs."""

    message: str
    code: str | None = None


class BaseError(BaseException, ABC):
    """Base error class, implementing Clean Architecture patterns."""

    @override
    def __init__(self, message: ErrorMsg) -> None:
        super().__init__(message)

        self.message: ErrorMsg = message


class BaseService(ABC):
    """Base service class, implementing Clean Architecture patterns."""


@dataclass(frozen=True, slots=True)
class BaseValue(ABC):
    """Base value class, implementing Clean Architecture patterns."""
