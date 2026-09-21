"""Use cases used by the application, as described by Clean Architecture."""

from __future__ import annotations

import logging
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import Any
from typing import override

from application.dto import BaseOutcome
from application.dto import BaseRequest
from application.dto import BaseResponse
from application.dto import GetSoundDevicesRequest
from application.dto import SoundDeviceResponse
from domain.base import Result
from domain.exception import ErrorMsg
from domain.exception import SoundDeviceProviderError

if TYPE_CHECKING:
    from logging import Logger

    from domain.entity import SoundDevice
    from domain.service import SoundDeviceProvider


logger: Logger = logging.getLogger(__name__)

type RequestType = BaseRequest
type ResponseType = BaseResponse | BaseOutcome | list[BaseResponse | BaseOutcome]


@dataclass(frozen=True, slots=True)
class BaseUseCase[REQ: RequestType, RES: ResponseType](ABC):
    """Base use case class, implementing Clean Architecture patterns."""

    _optional_services: dict[str, Any] = field(default_factory=dict, init=False)

    def register_service(self, name: str, service: Any) -> None:
        """Register an optional service with the use cases at runtime."""
        self._optional_services[name] = service

    def unregister_service(self, name: str) -> None:
        """Unregister an optional service with the use cases at runtime."""
        self._optional_services.pop(name)

    @abstractmethod
    def execute(self, request: REQ) -> Result[RES, ErrorMsg]:
        """Execute the use case with the provided request."""


# ---------- Project Specific ---------- #


NO_SOUND_DEVICES_FOUND_ERROR_MSG: ErrorMsg = ErrorMsg("No sound devices found.")


@dataclass(frozen=True, slots=True)
class GetSoundDevicesUseCase(BaseUseCase):
    """UseCase to get a list of available SoundDevices on the system."""

    sound_device_provider: SoundDeviceProvider

    @override
    def execute(self, request: GetSoundDevicesRequest) -> Result[list[SoundDeviceResponse], ErrorMsg]:
        _: dict[str, Any] = request.convert()
        try:
            devices: list[SoundDevice] = self.sound_device_provider.get_all()
            if len(devices) == 0:
                return Result.err(NO_SOUND_DEVICES_FOUND_ERROR_MSG)

            responses: list[SoundDeviceResponse] = [SoundDeviceResponse.from_entity(d) for d in devices]
            return Result.ok(responses)
        except SoundDeviceProviderError as e:
            logger.exception("SoundDeviceProvider raised an error: %s", e.message, exc_info=False)
            return Result.err(e.message)
