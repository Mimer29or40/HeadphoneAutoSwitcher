"""Application data transfer objects (DTOs), as described by Clean Architecture."""

from __future__ import annotations

import logging
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Self
from typing import override

from domain.entity import BaseEntity
from domain.entity import SoundDevice

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


@dataclass(frozen=True, slots=True)
class GetSoundDevicesRequest(BaseRequest):
    """Request for GetSoundDevicesUseCase."""

    @override
    def __post_init__(self) -> None:
        pass

    @override
    def convert(self) -> dict[str, Any]:
        return {}


@dataclass(frozen=True, slots=True)
class SoundDeviceResponse(BaseResponse):  # TODO(Ryan): Update when SoundDevice has more fields
    """Response for a SoundDevice entity."""

    id: str
    name: str
    type: str
    default: str

    @classmethod
    @override
    def from_entity(cls, entity: SoundDevice) -> Self:
        return cls(
            id=str(entity.id),
            name=entity.name,
            type=entity.type,
            default=entity.default,
        )
