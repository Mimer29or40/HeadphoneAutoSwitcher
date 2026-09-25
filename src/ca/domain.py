"""Clean architecture domain module."""

from __future__ import annotations

import logging.config
from abc import ABC
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import override
from uuid import UUID
from uuid import uuid4

if TYPE_CHECKING:
    from logging import Logger

logger: Logger = logging.getLogger("ca.domain")


# ---------- Entity ---------- #


@dataclass(eq=False)
class BaseEntity(ABC):
    """Clean architecture base entity class."""

    id: UUID = field(default_factory=uuid4, init=False)

    @override
    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, type(self)):
            return NotImplemented
        return self.id == value.id

    @override
    def __hash__(self) -> int:
        return hash(self.id)


# ---------- Error ---------- #


@dataclass(frozen=True, slots=True)
class ErrorMsg:
    """Clean architecture error message."""

    message: str
    code: str | None = None


class BaseError(Exception, ABC):
    """Clean architecture base error class."""

    @override
    def __init__(self, message: ErrorMsg) -> None:
        super().__init__(message)

        self.message: ErrorMsg = message


# ---------- Service ---------- #


class BaseService(ABC):
    """Clean architecture base service class."""


# ---------- Repository ---------- #


class BaseRepository(ABC):
    """Clean architecture base repository class."""


# ---------- Value ---------- #


@dataclass(frozen=True, slots=True)
class BaseValue(ABC):
    """Clean architecture base value class."""
