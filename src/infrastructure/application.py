"""Infrastructure application, as described by Clean Architecture."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import override

from _ca.application import BaseApplication
from application.use_case import GetSoundDevicesUseCase
from interface.controller import SoundDeviceController

if TYPE_CHECKING:
    from logging import Logger

    from domain.service import SoundDeviceProvider
    from interface.presenter import SoundDevicePresenter


logger: Logger = logging.getLogger("infrastructure.application")


@dataclass(frozen=True, kw_only=True, slots=True)
class Application(BaseApplication):
    """HeadphoneAutoSwitcher application container."""

    name: str = "Headphone Auto Switcher"
    description: str = (
        "Application that listens for wireless headphone to automatically "
        "switch to and from corresponding Windows sounds device."
    )
    version: str = "3.0.0a1"

    # Services
    sound_device_provider: SoundDeviceProvider
    sound_device_presenter: SoundDevicePresenter

    # Use cases
    get_sound_devices_use_case: GetSoundDevicesUseCase = field(init=False)

    # Controllers
    sound_device_controller: SoundDeviceController = field(init=False)

    @override
    def __post_init__(self) -> None:
        # Wire use cases
        get_sound_devices_use_case = GetSoundDevicesUseCase(
            sound_device_provider=self.sound_device_provider,
        )
        object.__setattr__(self, "get_sound_devices_use_case", get_sound_devices_use_case)

        # Wire controllers
        sound_device_controller = SoundDeviceController(
            get_sound_devices_use_case=get_sound_devices_use_case,
            sound_device_presenter=self.sound_device_presenter,
        )
        object.__setattr__(self, "sound_device_controller", sound_device_controller)
