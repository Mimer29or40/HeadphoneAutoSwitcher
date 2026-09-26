"""Headphone Auto Switcher interface controller module."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import assert_never

from ca.interface import BaseController
from ca.interface import ErrorViewModel
from ca.utils import Result
from ca.utils import log_call
from has.application.dto import GetSoundDevicesRequest
from has.application.dto import GetUsbDevicesRequest
from has.application.dto import SoundDeviceResponse
from has.application.dto import UsbDeviceResponse

if TYPE_CHECKING:
    from logging import Logger

    from ca.domain import ErrorMsg
    from has.application.use_case import GetSoundDevicesUseCase
    from has.application.use_case import GetUsbDevicesUseCase
    from has.interface.presenter import SoundDevicePresenter
    from has.interface.presenter import UsbDevicePresenter
    from has.interface.view_model import SoundDeviceViewModel
    from has.interface.view_model import UsbDeviceViewModel

logger: Logger = logging.getLogger("has.interface.controller")


@dataclass(frozen=True, slots=True)
class SoundDeviceController(BaseController):
    """Controller for SoundDevices."""

    get_sound_devices_use_case: GetSoundDevicesUseCase
    sound_device_presenter: SoundDevicePresenter

    @log_call(type="method", level=logging.INFO)
    def get_sound_devices(self) -> Result[list[SoundDeviceViewModel], ErrorViewModel]:
        """Handle getting SoundDevices."""
        # GetSoundDevicesRequest will never raise a ValueError so don't guard them
        request: GetSoundDevicesRequest = GetSoundDevicesRequest()
        result: Result[list[SoundDeviceResponse], ErrorMsg] = self.get_sound_devices_use_case.execute(request)

        if Result.is_ok(result):
            logger.info("UseCase success: get_sound_devices_use_case", extra={"context": {}})

            responses: list[SoundDeviceResponse] = result.value
            success_vms: list[SoundDeviceViewModel] = self.sound_device_presenter.present_many(responses)
            return Result.ok(success_vms)

        if Result.is_err(result):
            logger.info("UseCase failure: get_sound_devices_use_case", extra={"context": {"error": result.value}})

            message: ErrorMsg = result.value
            error_vm: ErrorViewModel = self.sound_device_presenter.present_error(message)
            return Result.err(error_vm)

        assert_never(result)  # ty:ignore[type-assertion-failure]


@dataclass(frozen=True, slots=True)
class UsbDeviceController(BaseController):
    """Controller for UsbDevices."""

    get_usb_devices_use_case: GetUsbDevicesUseCase
    usb_device_presenter: UsbDevicePresenter

    @log_call(type="method", level=logging.INFO)
    def get_usb_devices(self) -> Result[list[UsbDeviceViewModel], ErrorViewModel]:
        """Handle getting UsbDevices."""
        # GetUsbDevicesRequest will never raise a ValueError so don't guard them
        request: GetUsbDevicesRequest = GetUsbDevicesRequest()
        result: Result[list[UsbDeviceResponse], ErrorMsg] = self.get_usb_devices_use_case.execute(request)

        if Result.is_ok(result):
            logger.info("UseCase success: get_usb_devices_use_case", extra={"context": {}})

            responses: list[UsbDeviceResponse] = result.value
            success_vms: list[UsbDeviceViewModel] = self.usb_device_presenter.present_many(responses)
            return Result.ok(success_vms)

        if Result.is_err(result):
            logger.info("UseCase failure: get_usb_devices_use_case", extra={"context": {"error": result.value}})

            message: ErrorMsg = result.value
            error_vm: ErrorViewModel = self.usb_device_presenter.present_error(message)
            return Result.err(error_vm)

        assert_never(result)  # ty:ignore[type-assertion-failure]
