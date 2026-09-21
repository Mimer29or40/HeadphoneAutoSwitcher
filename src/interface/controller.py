"""Interface controllers, as described by Clean Architecture."""

from __future__ import annotations

import logging
from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING

from application.dto import GetSoundDevicesRequest
from application.dto import SoundDeviceResponse
from domain.base import Result

if TYPE_CHECKING:
    from logging import Logger

    from application.use_case import GetSoundDevicesUseCase
    from domain.exception import ErrorMsg
    from interface.presenter import SoundDevicePresenter
    from interface.view_model import ErrorViewModel
    from interface.view_model import SoundDeviceViewModel


logger: Logger = logging.getLogger("interface.controller")


class BaseController(ABC):
    """Base controller class, implementing Clean Architecture patterns."""


# ---------- Project Specific ---------- #


class Controller(BaseController):
    """Base controller class, implementing Clean Architecture patterns."""


@dataclass(frozen=True, slots=True)
class SoundDeviceController(BaseController):
    """Controller for SoundDevices."""

    get_sound_devices_use_case: GetSoundDevicesUseCase
    sound_device_presenter: SoundDevicePresenter

    def handle_get_sound_devices(self) -> Result[list[SoundDeviceViewModel], ErrorViewModel]:
        """Handle getting sound devices."""
        logger.info("Handling use case: get_sound_devices_use_case", extra={"context": {}})

        try:
            request: GetSoundDevicesRequest = GetSoundDevicesRequest()
            result: Result[list[SoundDeviceResponse], ErrorMsg] = self.get_sound_devices_use_case.execute(request)
        except ValueError as e:
            validation_error_vm: ErrorViewModel = self.sound_device_presenter.present_validation_error(e)
            return Result.err(validation_error_vm)

        if Result.is_ok(result):
            logger.info("Use case success: get_sound_devices_use_case", extra={"context": {}})

            success_vm: list[SoundDeviceViewModel] = self.sound_device_presenter.present_sound_devices(result.value)
            return Result.ok(success_vm)

        if Result.is_err(result):
            logger.info("Use case failure: get_sound_devices_use_case", extra={"context": {"error": result.value}})

            error_vm: ErrorViewModel = self.sound_device_presenter.present_error(result.value)
            return Result.err(error_vm)

        raise RuntimeError  # This will never happen
