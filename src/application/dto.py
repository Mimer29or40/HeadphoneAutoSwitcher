"""Application data transfer objects (DTOs), as described by Clean Architecture."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Self
from typing import override

from _ca.application import BaseRequest
from _ca.application import BaseResponse

if TYPE_CHECKING:
    from logging import Logger

    from domain.entity import SoundDevice


logger: Logger = logging.getLogger("application.dto")


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
