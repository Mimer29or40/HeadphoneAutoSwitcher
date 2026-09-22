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
from application.dto import SoundDeviceResponse
from domain.exception import SoundDeviceProviderError

if TYPE_CHECKING:
    from logging import Logger

    from domain.entity import SoundDevice
    from domain.service import SoundDeviceProvider


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
