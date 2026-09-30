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
from has.application.dto import ListenRequest
from has.application.dto import ListenRequestDict
from has.application.dto import RunRequest
from has.application.dto import RunRequestDict
from has.application.dto import SoundDeviceResponse
from has.application.dto import UsbDeviceResponse
from has.application.dto import ValidationRequest
from has.application.dto import ValidationRequestDict
from has.application.dto import ValidationResponse
from has.domain.entity import Validation
from has.domain.error import SoundDeviceProviderError
from has.domain.error import UsbDevicePacketListenerError
from has.domain.error import UsbDeviceProviderError
from has.utils import hex_string_to_int

if TYPE_CHECKING:
    from logging import Logger

    from has.application.config import Config
    from has.application.config import ConfigValidator
    from has.application.dto import GetSoundDevicesRequestDict
    from has.application.dto import GetUsbDevicesRequestDict
    from has.domain.entity import SoundDevice
    from has.domain.entity import UsbDevice
    from has.domain.service import SoundDeviceHandler
    from has.domain.service import SoundDeviceProvider
    from has.domain.service import UsbDevicePacketListener
    from has.domain.service import UsbDeviceProvider
    from has.domain.value import ConnectionState
    from has.domain.value import UsbDevicePacket
    from has.domain.value import UsbDevicePacketCallback

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
            logger.critical("SoundDeviceProvider raised an error: %s", e.message, exc_info=False)
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
            logger.critical("UsbDeviceProvider raised an error: %s", e.message, exc_info=False)
            return Result.err(e.message)


@dataclass(frozen=True, slots=True)
class ValidationUseCase(BaseUseCase):
    """UseCase to get the validation results for the application configuration."""

    config: Config
    config_validator: ConfigValidator

    usb_device_provider: UsbDeviceProvider

    @override
    @log_call(type="method", level=logging.INFO)
    def execute(self, request: ValidationRequest) -> Result[ValidationResponse, ErrorMsg]:
        _: ValidationRequestDict = request.convert()

        validation_errors: list[ErrorMsg] = []

        self.config_validator.validate(self.config)  # TODO(Ryan): Handle errors

        vendor_id: int = hex_string_to_int(self.config.vendor_id)
        product_id: int = hex_string_to_int(self.config.product_id)

        # try:)  # TODO(Ryan): Implement
        #     handler: DeviceHandler = get_device_handler(HANDLER_DB_PATH, vendor_id, product_id)
        #     logger.info("Handler found: %s", handler)
        # except KeyError:
        #     logger.critical("Headphone not supported: Vendor (%s) Product (%s)", vendor_id, product_id)
        #     return "UNSUPPORTED_HEADPHONES"

        try:
            # usb_device_entities: list[UsbDevice] = self.usb_device_provider(vendor_id=vendor_id, product_id=product_id)
            usb_device_entities: list[UsbDevice] = [
                usb_device
                for usb_device in self.usb_device_provider.get_all()
                if usb_device.vendor_id == vendor_id and usb_device.product_id == product_id
            ]

            usb_device_count: int = len(usb_device_entities)
            if usb_device_count == 0:
                validation_errors.append(NO_USB_DEVICES_FOUND_MESSAGE)
        except UsbDeviceProviderError as e:
            logger.critical("UsbDeviceProvider raised an error: %s", e.message, exc_info=False)
            validation_errors.append(e.message)

        validation_entity: Validation = Validation(reasons=validation_errors)
        response: ValidationResponse = ValidationResponse.from_entity(validation_entity)
        return Result.ok(response)


@dataclass(frozen=True, slots=True)
class ListenUseCase(BaseUseCase):
    """UseCase to get all UsbDevices available."""

    config: Config

    usb_device_packet_listener: UsbDevicePacketListener

    @override
    @log_call(type="method", level=logging.INFO)
    def execute(self, request: ListenRequest) -> Result[None, ErrorMsg]:
        request_dict: ListenRequestDict = request.convert()
        listener_callback: UsbDevicePacketCallback = request_dict.get("listener")

        vendor_id: int = hex_string_to_int(self.config.vendor_id)
        product_id: int = hex_string_to_int(self.config.product_id)

        # usb_device_entities: list[UsbDevice] = self.usb_device_provider(vendor_id=vendor_id, product_id=product_id)
        try:
            # TODO(Ryan): Explicitly pass UsbDevice list to listen to
            self.usb_device_packet_listener.start(vendor_id=vendor_id, product_id=product_id)

            packet: UsbDevicePacket | None
            while (packet := self.usb_device_packet_listener.get()) is not None:
                listener_callback(packet)
            return Result.ok(None)
        except UsbDevicePacketListenerError as e:
            logger.critical("UsbDevicePacketListener raised an error: %s", e.message, exc_info=False)
            return Result.err(e.message)
        finally:
            self.usb_device_packet_listener.stop()


@dataclass(frozen=True, slots=True)
class RunUseCase(BaseUseCase):
    """UseCase to run the headphone switcher."""

    config: Config

    # sound_device_handler: SoundDeviceHandler
    usb_device_packet_listener: UsbDevicePacketListener

    @override
    @log_call(type="method", level=logging.INFO)
    def execute(self, request: RunRequest) -> Result[None, ErrorMsg]:
        _: RunRequestDict = request.convert()

        vendor_id: int = hex_string_to_int(self.config.vendor_id)
        product_id: int = hex_string_to_int(self.config.product_id)

        # usb_device_entities: list[UsbDevice] = self.usb_device_provider(vendor_id=vendor_id, product_id=product_id)
        try:
            # TODO(Ryan): Explicitly pass UsbDevice list to listen to
            # self.usb_device_packet_listener.start(usb_device_entities)
            self.usb_device_packet_listener.start(vendor_id=vendor_id, product_id=product_id)

            packet: UsbDevicePacket | None
            while (packet := self.usb_device_packet_listener.get()) is not None:
                state: ConnectionState = self.sound_device_handler.is_connected(packet)

                # Check for a state change and process accordingly
                if state is not None:
                    if state:
                        self.set_headphones()
                    else:
                        self.set_previous()

            return Result.ok(None)
        except UsbDevicePacketListenerError as e:
            logger.critical("UsbDevicePacketListener raised an error: %s", e.message, exc_info=False)
            return Result.err(e.message)
        finally:
            self.usb_device_packet_listener.stop()

    @log_call(type="method", level=logging.INFO)
    def set_headphones(self) -> None:
        """Set the headphones as the sound device."""

    @log_call(type="method", level=logging.INFO)
    def set_previous(self) -> None:
        """Set the previous device as the sound device."""
