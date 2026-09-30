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
from has.application.dto import ListenRequest
from has.application.dto import RunRequest
from has.application.dto import SoundDeviceResponse
from has.application.dto import UsbDeviceResponse
from has.application.dto import ValidationRequest
from has.application.dto import ValidationResponse

if TYPE_CHECKING:
    from logging import Logger

    from ca.domain import ErrorMsg
    from has.application.use_case import GetSoundDevicesUseCase
    from has.application.use_case import GetUsbDevicesUseCase
    from has.application.use_case import ListenUseCase
    from has.application.use_case import RunUseCase
    from has.application.use_case import ValidationUseCase
    from has.domain.value import UsbDevicePacketCallback
    from has.interface.presenter import SoundDevicePresenter
    from has.interface.presenter import UsbDevicePresenter
    from has.interface.presenter import ValidationPresenter
    from has.interface.view_model import SoundDeviceViewModel
    from has.interface.view_model import UsbDeviceViewModel
    from has.interface.view_model import ValidationViewModel

logger: Logger = logging.getLogger("has.interface.controller")


@dataclass(frozen=True, slots=True)
class SoundDeviceController(BaseController):
    """Controller for SoundDevices."""

    # UseCases
    get_sound_devices_use_case: GetSoundDevicesUseCase

    # Presenter
    presenter: SoundDevicePresenter

    @log_call(type="method", level=logging.INFO)
    def handle_get_sound_devices(self) -> Result[list[SoundDeviceViewModel], ErrorViewModel]:
        """Handle getting SoundDevices."""
        # GetSoundDevicesRequest will never raise a ValueError so don't guard them
        request: GetSoundDevicesRequest = GetSoundDevicesRequest()
        result: Result[list[SoundDeviceResponse], ErrorMsg] = self.get_sound_devices_use_case.execute(request)

        if Result.is_ok(result):
            logger.info("UseCase success: get_sound_devices_use_case", extra={"context": {"ok": result.value}})

            responses: list[SoundDeviceResponse] = result.value
            success_vms: list[SoundDeviceViewModel] = self.presenter.present_many(responses)
            return Result.ok(success_vms)

        if Result.is_err(result):
            logger.info("UseCase failure: get_sound_devices_use_case", extra={"context": {"error": result.value}})

            message: ErrorMsg = result.value
            error_vm: ErrorViewModel = self.presenter.present_error(message)
            return Result.err(error_vm)

        assert_never(result)  # ty:ignore[type-assertion-failure]


@dataclass(frozen=True, slots=True)
class UsbDeviceController(BaseController):
    """Controller for UsbDevices."""

    # UseCases
    get_usb_devices_use_case: GetUsbDevicesUseCase

    # Presenter
    presenter: UsbDevicePresenter

    @log_call(type="method", level=logging.INFO)
    def handle_get_usb_devices(self) -> Result[list[UsbDeviceViewModel], ErrorViewModel]:
        """Handle getting UsbDevices."""
        # GetUsbDevicesRequest will never raise a ValueError so don't guard them
        request: GetUsbDevicesRequest = GetUsbDevicesRequest()
        result: Result[list[UsbDeviceResponse], ErrorMsg] = self.get_usb_devices_use_case.execute(request)

        if Result.is_ok(result):
            logger.info("UseCase success: get_usb_devices_use_case", extra={"context": {"ok": result.value}})

            responses: list[UsbDeviceResponse] = result.value
            success_vms: list[UsbDeviceViewModel] = self.presenter.present_many(responses)
            return Result.ok(success_vms)

        if Result.is_err(result):
            logger.info("UseCase failure: get_usb_devices_use_case", extra={"context": {"error": result.value}})

            message: ErrorMsg = result.value
            error_vm: ErrorViewModel = self.presenter.present_error(message)
            return Result.err(error_vm)

        assert_never(result)  # ty:ignore[type-assertion-failure]


@dataclass(frozen=True, slots=True)
class SwitcherController(BaseController):
    """Controller for the headphone switcher."""

    # UseCases
    validation_use_case: ValidationUseCase
    listen_use_case: ListenUseCase
    run_use_case: RunUseCase

    # Presenter
    presenter: ValidationPresenter

    @log_call(type="method", level=logging.INFO)
    def handle_validate(self) -> Result[ValidationViewModel, ErrorViewModel]:
        """Handle validating application configuration ."""
        # ValidationRequest will never raise a ValueError so don't guard them
        request: ValidationRequest = ValidationRequest()
        result: Result[ValidationResponse, ErrorMsg] = self.validation_use_case.execute(request)

        if Result.is_ok(result):
            logger.info("UseCase success: validation_use_case", extra={"context": {"ok": result.value}})

            response: ValidationResponse = result.value
            success_vm: ValidationViewModel = self.presenter.present(response)
            return Result.ok(success_vm)

        if Result.is_err(result):
            logger.info("UseCase failure: validation_use_case", extra={"context": {"error": result.value}})

            message: ErrorMsg = result.value
            error_vm: ErrorViewModel = self.presenter.present_error(message)
            return Result.err(error_vm)

        assert_never(result)  # ty:ignore[type-assertion-failure]

    @log_call(type="method", level=logging.INFO)
    def handle_listen(self, listener: UsbDevicePacketCallback) -> Result[None, ErrorViewModel]:
        """Handle listen to configured UsbDevice traffic."""
        try:
            request: ListenRequest = ListenRequest(listener=listener)
            result: Result[None, ErrorMsg] = self.listen_use_case.execute(request)
        except ValueError as e:
            error_value: ErrorViewModel = self.presenter.present_validation_error(e)
            return Result.err(error_value)

        if Result.is_ok(result):
            logger.info("UseCase success: listen_use_case", extra={"context": {"ok": result.value}})

            response: None = result.value
            return Result.ok(response)

        if Result.is_err(result):
            logger.info("UseCase failure: listen_use_case", extra={"context": {"error": result.value}})

            message: ErrorMsg = result.value
            error_vm: ErrorViewModel = self.presenter.present_error(message)
            return Result.err(error_vm)

        assert_never(result)  # ty:ignore[type-assertion-failure]

    @log_call(type="method", level=logging.INFO)
    def handle_run(self) -> Result[None, ErrorViewModel]:
        """Handle running the headphone switcher."""
        # RunRequest will never raise a ValueError so don't guard them
        request: RunRequest = RunRequest()
        result: Result[None, ErrorMsg] = self.run_use_case.execute(request)

        if Result.is_ok(result):
            logger.info("UseCase success: run_use_case", extra={"context": {"ok": result.value}})

            response: None = result.value
            return Result.ok(response)

        if Result.is_err(result):
            logger.info("UseCase failure: run_use_case", extra={"context": {"error": result.value}})

            message: ErrorMsg = result.value
            error_vm: ErrorViewModel = self.presenter.present_error(message)
            return Result.err(error_vm)

        assert_never(result)  # ty:ignore[type-assertion-failure]
