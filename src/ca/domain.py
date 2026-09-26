"""Clean architecture domain module."""

from __future__ import annotations

import logging.config
from abc import ABC
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import overload
from typing import override
from uuid import UUID
from uuid import uuid4

from ca.utils import log_call

if TYPE_CHECKING:
    from logging import Logger

logger: Logger = logging.getLogger("ca.domain")


# ---------- Entity ---------- #


@dataclass(eq=False, kw_only=True)
class BaseEntity(ABC):
    """Clean architecture base entity class."""

    id: UUID = field(default_factory=uuid4)

    @override
    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, type(self)):
            return NotImplemented
        return self.id == value.id

    @override
    def __hash__(self) -> int:
        return hash(self.id)

    @log_call(type="static", level=logging.DEBUG, arg_func="str")
    def __post_init__(self) -> None:
        """Empty function call to enable trace logging."""


# ---------- Error ---------- #


@dataclass(frozen=True, slots=True)
class ErrorMsg:
    """Clean architecture error message."""

    message: str
    code: str | None = None


class BaseError(Exception, ABC):
    """Clean architecture base error class."""

    @overload
    def __init__(self, message: ErrorMsg, /) -> None: ...

    @overload
    def __init__(self, *args: object) -> None: ...

    @override
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

    @property
    def message(self) -> ErrorMsg:
        """ErrorMsg."""
        return self.args[0]


class ServiceError(BaseError):
    """Exception raised by a Service."""


class RepositoryError(BaseError):
    """Exception raised by a Repository."""


class FrameworkError(BaseError):
    """Exception raised by a Framework."""


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
