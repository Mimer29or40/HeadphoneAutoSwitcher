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
    from domain.entity import UsbDevice


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
class GetUsbDevicesRequest(BaseRequest):
    """Request for GetUsbDevicesUseCase."""

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
    selected: bool

    @classmethod
    @override
    def from_entity(cls, entity: SoundDevice) -> Self:
        return cls(
            id=str(entity.id),
            name=entity.name,
            type=entity.type.name.lower(),
            selected=entity.selected,
        )


@dataclass(frozen=True, slots=True)
class UsbDeviceResponse(BaseResponse):  # TODO(Ryan): Update when UsbDevice has more fields
    """Response for a UsbDevice entity."""

    id: str
    serial_number: str
    vendor_name: str
    vendor_id: int
    product_name: str
    product_id: int
    version_number: int

    @classmethod
    @override
    def from_entity(cls, entity: UsbDevice) -> Self:
        return cls(
            id=str(entity.id),
            serial_number=entity.serial_number,
            vendor_name=entity.vendor_name,
            vendor_id=entity.vendor_id,
            product_name=entity.product_name,
            product_id=entity.product_id,
            version_number=entity.version_number,
        )
