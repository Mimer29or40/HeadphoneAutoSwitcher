"""Application layer base classes, as described by Clean Architecture."""

from __future__ import annotations

import logging
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import Any
from typing import Self

from _ca.domain import BaseEntity
from _ca.domain import ErrorMsg

if TYPE_CHECKING:
    from logging import Logger

    from _ca.utils import Result


logger: Logger = logging.getLogger("application")


@dataclass(frozen=True, slots=True)
class BaseConfig(ABC):
    """Base config class, implementing Clean Architecture patterns."""


class BaseConfigProvider[C: BaseConfig](ABC):
    """Base config provider class, implementing Clean Architecture patterns."""

    @abstractmethod
    def get(self) -> C:
        """Get the configuration."""


class BaseApplication(ABC):
    """Base application class, implementing Clean Architecture patterns."""

    name: str
    description: str
    version: str

    config: BaseConfig

    def __post_init__(self) -> None:
        """Wire up use cases and controllers."""


# ----- Data Transfer Object ----- #


class BaseRequest(ABC):
    """Base request class, implementing Clean Architecture patterns."""

    @abstractmethod
    def __post_init__(self) -> None:
        """Validate request data."""

    @abstractmethod
    def convert(self) -> dict[str, Any]:
        """Convert validated request data to use case parameters."""


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


class BaseAdapter[A, B](ABC):
    """Base class for adapters."""

    @abstractmethod
    def convert(self, value: A) -> B:
        """Convert the value to another type."""


# ----- Port ----- #


class BasePort(ABC):
    """Base port class, implementing Clean Architecture patterns."""


# ----- Repository ----- #


class BaseRepository(ABC):
    """Base repository class, implementing Clean Architecture patterns."""


# ----- Use Case ----- #


type UseCaseRequestType = BaseRequest
type UseCaseResponseType = BaseResponse | BaseOutcome | list[BaseResponse | BaseOutcome]


@dataclass(frozen=True, slots=True)
class BaseUseCase[REQ: UseCaseRequestType, RES: UseCaseResponseType](ABC):
    """Base use case class, implementing Clean Architecture patterns."""

    _optional_services: dict[str, Any] = field(default_factory=dict, init=False)

    def register_service(self, name: str, service: Any) -> None:
        """Register an optional service with the use cases at runtime."""
        self._optional_services[name] = service

    def unregister_service(self, name: str) -> None:
        """Unregister an optional service with the use cases at runtime."""
        self._optional_services.pop(name)

    @abstractmethod
    def execute(self, request: REQ) -> Result[RES, ErrorMsg]:
        """Execute the use case with the provided request."""
