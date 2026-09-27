"""Clean architecture application module."""

from __future__ import annotations

import logging.config
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import Any
from typing import Self
from typing import TypedDict

from ca.domain import BaseEntity
from ca.domain import ErrorMsg
from ca.utils import log_call

if TYPE_CHECKING:
    from collections.abc import Iterable
    from logging import Logger

    from ca.utils import Result

logger: Logger = logging.getLogger("ca.application")


# ---------- Application ---------- #


class BaseApplication(ABC):
    """Clean architecture base application class."""

    @abstractmethod
    @log_call(type="method")
    def __post_init__(self) -> None:
        """Wire up application UseCases and Controllers."""


class BaseApplicationFactory[A: BaseApplication](ABC):
    """Clean architecture base application factory class."""

    name: str
    description: str
    version: str

    @abstractmethod
    @log_call(type="method")
    def create(self) -> A:
        """Create the application."""


# ---------- Data Transfer Object (DTO) ---------- #


class BaseRequestDict(TypedDict):
    """Clean architecture base request dictionary class."""


class BaseRequest[T: BaseRequestDict](ABC):
    """Clean architecture base request class."""

    @abstractmethod
    @log_call(type="method")
    def __post_init__(self) -> None:
        """Validate Request parameters."""

    @abstractmethod
    @log_call(type="method")
    def convert(self) -> T:
        """Convert the Request parameters into UseCase parameters."""


class BaseResponse[T: BaseEntity](ABC):
    """Clean architecture base response class."""

    @classmethod
    @abstractmethod
    @log_call(type="method")
    def from_entity(cls, entity: T) -> Self:
        """Create a Response from an Entity."""

    @classmethod
    @log_call(type="class")
    def from_entities(cls, entities: Iterable[T]) -> list[Self]:
        """Create multiple Responses from many Entities."""
        return [cls.from_entity(entity) for entity in entities]


# ---------- Port ---------- #


class BasePort(ABC):
    """Clean architecture base port class."""


# ---------- Use Case ---------- #


type UseCaseRequestType = BaseRequest
type UseCaseResponseType = BaseResponse | list[BaseResponse]


@dataclass(frozen=True, slots=True)
class BaseUseCase[REQ: UseCaseRequestType, RES: UseCaseResponseType](ABC):
    """Clean architecture base use case class."""

    optional: dict[str, Any] = field(default_factory=dict, init=False)

    @log_call(type="method")
    def register(self, name: str, extension: Any) -> None:
        """Register an optional extension to the UseCase."""
        self.optional[name] = extension

    @log_call(type="method")
    def unregister(self, name: str) -> None:
        """Unregister an optional extension from the UseCase."""
        self.optional.pop(name)

    @abstractmethod
    @log_call(type="method")
    def execute(self, request: REQ) -> Result[RES, ErrorMsg]:
        """Execute the UseCase with the provided Parameters."""
