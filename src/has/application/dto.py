"""Headphone Auto Switcher application data transfer object module."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Self
from typing import TypedDict
from typing import override

from ca.application import BaseRequest
from ca.application import BaseRequestDict
from ca.application import BaseResponse
from ca.utils import log_call

if TYPE_CHECKING:
    from logging import Logger

    from has.domain.entity import SoundDevice
    from has.domain.entity import UsbDevice

logger: Logger = logging.getLogger("has.application.dto")


class GetSoundDevicesRequestDict(BaseRequestDict, TypedDict):
    """Clean architecture base request dictionary class."""


@dataclass(frozen=True, slots=True)
class GetSoundDevicesRequest(BaseRequest):
    """Request for GetSoundDevicesUseCase."""

    @override
    def __post_init__(self) -> None:
        pass

    @override
    def convert(self) -> GetSoundDevicesRequestDict:
        return {}


class GetUsbDevicesRequestDict(BaseRequestDict, TypedDict):
    """Clean architecture base request dictionary class."""


@dataclass(frozen=True, slots=True)
class GetUsbDevicesRequest(BaseRequest):
    """Request for GetUsbDevicesUseCase."""

    @override
    def __post_init__(self) -> None:
        pass

    @override
    def convert(self) -> GetUsbDevicesRequestDict:
        return {}


@dataclass(frozen=True, slots=True)
class SoundDeviceResponse(BaseResponse):
    """Response for a SoundDevice."""

    id: str
    name: str
    type: str
    selected: bool

    @classmethod
    @override
    @log_call(type="class")
    def from_entity(cls, entity: SoundDevice) -> Self:
        return cls(
            id=str(entity.id),
            name=entity.name,
            type=entity.type.name.lower(),
            selected=entity.selected,
        )


@dataclass(frozen=True, slots=True)
class UsbDeviceResponse(BaseResponse):
    """Response for a UsbDevice."""

    id: str
    product_name: str
    product_id: str
    vendor_name: str
    vendor_id: str

    @classmethod
    @override
    @log_call(type="class")
    def from_entity(cls, entity: UsbDevice) -> Self:
        return cls(
            id=str(entity.id),
            product_name=entity.product_name,
            product_id=f"{entity.product_id:04X}",
            vendor_name=entity.vendor_name,
            vendor_id=f"{entity.vendor_id:04X}",
        )
