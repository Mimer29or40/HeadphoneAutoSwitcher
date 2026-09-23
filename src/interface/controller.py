"""Interface controllers, as described by Clean Architecture."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import assert_never

from _ca.interface import BaseController
from _ca.utils import Result
from application.dto import GetSoundDevicesRequest
from application.dto import GetUsbDevicesRequest
from application.dto import SoundDeviceResponse
from application.dto import UsbDeviceResponse

if TYPE_CHECKING:
    from logging import Logger

    from _ca.domain import ErrorMsg
    from _ca.interface import ErrorViewModel
    from application.use_case import GetSoundDevicesUseCase
    from application.use_case import GetUsbDevicesUseCase
    from interface.presenter import SoundDevicePresenter
    from interface.presenter import UsbDevicePresenter
    from interface.view_model import SoundDeviceViewModel
    from interface.view_model import UsbDeviceViewModel


logger: Logger = logging.getLogger("interface.controller")


@dataclass(frozen=True, slots=True)
class SoundDeviceController(BaseController):
    """Controller for SoundDevices."""

    get_sound_devices_use_case: GetSoundDevicesUseCase
    sound_device_presenter: SoundDevicePresenter

    def handle_get_sound_devices(self) -> Result[list[SoundDeviceViewModel], ErrorViewModel]:
        """Handle getting sound devices."""
        logger.info("Handling use case: get_sound_devices_use_case", extra={"context": {}})

        # GetSoundDevicesRequest will never raise a ValueError so don't guard from validation errors
        request: GetSoundDevicesRequest = GetSoundDevicesRequest()
        result: Result[list[SoundDeviceResponse], ErrorMsg] = self.get_sound_devices_use_case.execute(request)

        if Result.is_ok(result):
            logger.info("Use case success: get_sound_devices_use_case", extra={"context": {}})

            success_vm: list[SoundDeviceViewModel] = self.sound_device_presenter.present_sound_devices(result.value)
            return Result.ok(success_vm)

        if Result.is_err(result):
            logger.info("Use case failure: get_sound_devices_use_case", extra={"context": {"error": result.value}})

            error_vm: ErrorViewModel = self.sound_device_presenter.present_error(result.value)
            return Result.err(error_vm)

        assert_never(result)  # ty:ignore[type-assertion-failure]


@dataclass(frozen=True, slots=True)
class UsbDeviceController(BaseController):
    """Controller for UsbDevices."""

    get_usb_devices_use_case: GetUsbDevicesUseCase
    usb_device_presenter: UsbDevicePresenter

    def handle_get_usb_devices(self) -> Result[list[UsbDeviceViewModel], ErrorViewModel]:
        """Handle getting usb devices."""
        logger.info("Handling use case: get_usb_devices_use_case", extra={"context": {}})

        # GetUsbDevicesRequest will never raise a ValueError so don't guard from validation errors
        request: GetUsbDevicesRequest = GetUsbDevicesRequest()
        result: Result[list[UsbDeviceResponse], ErrorMsg] = self.get_usb_devices_use_case.execute(request)

        if Result.is_ok(result):
            logger.info("Use case success: get_usb_devices_use_case", extra={"context": {}})

            success_vm: list[UsbDeviceViewModel] = self.usb_device_presenter.present_usb_devices(result.value)
            return Result.ok(success_vm)

        if Result.is_err(result):
            logger.info("Use case failure: get_usb_devices_use_case", extra={"context": {"error": result.value}})

            error_vm: ErrorViewModel = self.usb_device_presenter.present_error(result.value)
            return Result.err(error_vm)

        assert_never(result)  # ty:ignore[type-assertion-failure]
