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
from ca.application import EmptyRequest
from ca.application import EmptyRequestDict
from ca.utils import log_call

if TYPE_CHECKING:
    from logging import Logger

    from has.domain.entity import SoundDevice
    from has.domain.entity import UsbDevice
    from has.domain.entity import Validation
    from has.domain.value import UsbDevicePacketCallback

logger: Logger = logging.getLogger("has.application.dto")


class GetSoundDevicesRequestDict(EmptyRequestDict):
    """RequestDict for GetSoundDevicesUseCase."""


@dataclass(frozen=True, slots=True)
class GetSoundDevicesRequest(EmptyRequest):
    """Request for GetSoundDevicesUseCase."""


class GetUsbDevicesRequestDict(EmptyRequestDict):
    """RequestDict for GetUsbDevicesUseCase."""


@dataclass(frozen=True, slots=True)
class GetUsbDevicesRequest(EmptyRequest):
    """Request for GetUsbDevicesUseCase."""


class ValidationRequestDict(EmptyRequestDict):
    """RequestDict for ValidationUseCase."""


@dataclass(frozen=True, slots=True)
class ValidationRequest(EmptyRequest):
    """Request for ValidationUseCase."""


class ListenRequestDict(BaseRequestDict, TypedDict):
    """RequestDict for ListenUseCase."""

    listener: UsbDevicePacketCallback


@dataclass(frozen=True, slots=True)
class ListenRequest(BaseRequest):
    """Request for ListenUseCase."""

    listener: UsbDevicePacketCallback

    @override
    def __post_init__(self) -> None:
        if not callable(self.listener):
            raise ValueError("listener must be callable")  # noqa: TRY004

    @override
    def convert(self) -> ListenRequestDict:
        return ListenRequestDict(listener=self.listener)


class RunRequestDict(EmptyRequestDict):
    """RequestDict for RunUseCase."""


@dataclass(frozen=True, slots=True)
class RunRequest(EmptyRequest):
    """Request for RunUseCase."""


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


@dataclass(frozen=True, slots=True)
class ValidationResponse(BaseResponse):
    """Response for a Validation."""

    id: str
    is_valid: bool
    reasons: list[str]

    @classmethod
    @override
    @log_call(type="class")
    def from_entity(cls, entity: Validation) -> Self:
        return cls(
            id=str(entity.id),
            is_valid=entity.is_valid,
            reasons=[reason.message for reason in entity.reasons],
        )
