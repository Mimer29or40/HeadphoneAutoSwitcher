"""Headphone Auto Switcher application use case module."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import override

from ca.application import BaseUseCase
from ca.domain import ErrorMsg
from ca.utils import Result
from ca.utils import log_call
from has.application.dto import GetSoundDevicesRequest
from has.application.dto import GetUsbDevicesRequest
from has.application.dto import SoundDeviceResponse
from has.application.dto import UsbDeviceResponse
from has.domain.error import SoundDeviceProviderError
from has.domain.error import UsbDeviceProviderError

if TYPE_CHECKING:
    from logging import Logger

    from has.application.dto import GetSoundDevicesRequestDict
    from has.application.dto import GetUsbDevicesRequestDict
    from has.domain.entity import SoundDevice
    from has.domain.entity import UsbDevice
    from has.domain.service import SoundDeviceProvider
    from has.domain.service import UsbDeviceProvider

logger: Logger = logging.getLogger("has.application.use_case")


NO_SOUND_DEVICES_FOUND_MESSAGE: ErrorMsg = ErrorMsg("No sound devices found.")


@dataclass(frozen=True, slots=True)
class GetSoundDevicesUseCase(BaseUseCase):
    """UseCase to get all SoundDevices available."""

    sound_device_provider: SoundDeviceProvider

    @override
    @log_call(type="method", level=logging.INFO)
    def execute(self, request: GetSoundDevicesRequest) -> Result[list[SoundDeviceResponse], ErrorMsg]:
        _: GetSoundDevicesRequestDict = request.convert()
        try:
            device_entities: list[SoundDevice] = self.sound_device_provider.get_all()
            if len(device_entities) == 0:
                return Result.err(NO_SOUND_DEVICES_FOUND_MESSAGE)

            responses: list[SoundDeviceResponse] = SoundDeviceResponse.from_entities(device_entities)
            return Result.ok(responses)
        except SoundDeviceProviderError as e:
            logger.exception("SoundDeviceProvider raised an error: %s", e.message, exc_info=False)
            return Result.err(e.message)


NO_USB_DEVICES_FOUND_MESSAGE: ErrorMsg = ErrorMsg("No usb devices found.")


@dataclass(frozen=True, slots=True)
class GetUsbDevicesUseCase(BaseUseCase):
    """UseCase to get all UsbDevices available."""

    usb_device_provider: UsbDeviceProvider

    @override
    @log_call(type="method", level=logging.INFO)
    def execute(self, request: GetUsbDevicesRequest) -> Result[list[UsbDeviceResponse], ErrorMsg]:
        _: GetUsbDevicesRequestDict = request.convert()
        try:
            device_entities: list[UsbDevice] = self.usb_device_provider.get_all()
            if len(device_entities) == 0:
                return Result.err(NO_USB_DEVICES_FOUND_MESSAGE)

            responses: list[UsbDeviceResponse] = UsbDeviceResponse.from_entities(device_entities)
            return Result.ok(responses)
        except UsbDeviceProviderError as e:
            logger.exception("UsbDeviceProvider raised an error: %s", e.message, exc_info=False)
            return Result.err(e.message)
