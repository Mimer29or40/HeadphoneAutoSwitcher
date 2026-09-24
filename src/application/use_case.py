"""Use cases used by the application, as described by Clean Architecture."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import override

from _ca.application import BaseUseCase
from _ca.domain import ErrorMsg
from _ca.utils import Result
from application.dto import GetSoundDevicesRequest
from application.dto import GetUsbDevicesRequest
from application.dto import ListenToDevicesRequest
from application.dto import SoundDeviceResponse
from application.dto import UsbDeviceResponse
from domain.exception import SoundDeviceProviderError
from domain.exception import UsbDeviceProviderError
from domain.service import UsbDeviceListener
from domain.value import UsbDevicePacket

if TYPE_CHECKING:
    from logging import Logger

    from domain.entity import SoundDevice
    from domain.entity import UsbDevice
    from domain.service import SoundDeviceProvider
    from domain.service import UsbDeviceProvider


logger: Logger = logging.getLogger(__name__)


NO_SOUND_DEVICES_FOUND_ERROR_MSG: ErrorMsg = ErrorMsg("No sound devices found.")


@dataclass(frozen=True, slots=True)
class GetSoundDevicesUseCase(BaseUseCase):
    """UseCase to get a list of available SoundDevices on the system."""

    sound_device_provider: SoundDeviceProvider

    @override
    def execute(self, request: GetSoundDevicesRequest) -> Result[list[SoundDeviceResponse], ErrorMsg]:
        _: dict[str, Any] = request.convert()
        try:
            devices: list[SoundDevice] = self.sound_device_provider.find_all()
            if len(devices) == 0:
                return Result.err(NO_SOUND_DEVICES_FOUND_ERROR_MSG)

            responses: list[SoundDeviceResponse] = [SoundDeviceResponse.from_entity(d) for d in devices]
            return Result.ok(responses)
        except SoundDeviceProviderError as e:
            logger.exception("SoundDeviceProvider raised an error: %s", e.message, exc_info=False)
            return Result.err(e.message)


NO_USB_DEVICES_FOUND_ERROR_MSG: ErrorMsg = ErrorMsg("No usb devices found.")


@dataclass(frozen=True, slots=True)
class GetUsbDevicesUseCase(BaseUseCase):
    """UseCase to get a list of available UsbDevices on the system."""

    usb_device_provider: UsbDeviceProvider

    @override
    def execute(self, request: GetUsbDevicesRequest) -> Result[list[UsbDeviceResponse], ErrorMsg]:
        _: dict[str, Any] = request.convert()
        try:
            devices: list[UsbDevice] = self.usb_device_provider.find_all()
            if len(devices) == 0:
                return Result.err(NO_USB_DEVICES_FOUND_ERROR_MSG)

            responses: list[UsbDeviceResponse] = [UsbDeviceResponse.from_entity(d) for d in devices]
            return Result.ok(responses)
        except UsbDeviceProviderError as e:
            logger.exception("UsbDeviceProvider raised an error: %s", e.message, exc_info=False)
            return Result.err(e.message)


@dataclass(frozen=True, slots=True)
class ListenToDevicesUseCase(BaseUseCase):
    """UseCase to listen to the configured UsbDevice."""

    usb_device_listener: UsbDeviceListener

    @override
    def execute(self, request: ListenToDevicesRequest) -> Result[None, ErrorMsg]:
        request_dict: dict[str, Any] = request.convert()
        vendor_id: int = request_dict["vendor_id"]
        product_id: int = request_dict["product_id"]

        try:
            self.usb_device_listener.start(vendor_id, product_id)
            while True:
                packet: UsbDevicePacket = self.usb_device_listener.get_packet()
                click.echo(f"Packet Received: {packet}")
                time.sleep(0.1)
        finally:
            self.usb_device_listener.stop()

        # try:
        #     devices: list[UsbDevice] = self.usb_device_provider.find_all()
        #     if len(devices) == 0:
        #         return Result.err(NO_USB_DEVICES_FOUND_ERROR_MSG)
        #
        #     responses: list[UsbDeviceResponse] = [UsbDeviceResponse.from_entity(d) for d in devices]
        #     return Result.ok(responses)
        # except UsbDeviceProviderError as e:
        #     logger.exception("UsbDeviceProvider raised an error: %s", e.message, exc_info=False)
        #     return Result.err(e.message)
