"""Headphone Auto Switcher application infrastructure module."""

from __future__ import annotations

import logging
from abc import ABC
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import override

from ca.application import BaseApplication
from ca.application import BaseApplicationFactory
from has.application.use_case import GetSoundDevicesUseCase
from has.application.use_case import GetUsbDevicesUseCase
from has.interface.controller import SoundDeviceController
from has.interface.controller import UsbDeviceController

if TYPE_CHECKING:
    from logging import Logger

    from has.domain.service import SoundDeviceProvider
    from has.domain.service import UsbDeviceProvider
    from has.interface.controller import RunController
    from has.interface.presenter import SoundDevicePresenter
    from has.interface.presenter import UsbDevicePresenter

logger: Logger = logging.getLogger("ca.infrastructure.application")


@dataclass(frozen=True, slots=True)
class HASApplication(BaseApplication):
    """Headphone Auto Switcher application container."""

    # Providers
    sound_device_provider: SoundDeviceProvider
    usb_device_provider: UsbDeviceProvider

    # Presenters
    sound_device_presenter: SoundDevicePresenter
    usb_device_presenter: UsbDevicePresenter

    # Controllers
    sound_device_controller: SoundDeviceController = field(init=False, repr=False)
    usb_device_controller: UsbDeviceController = field(init=False, repr=False)
    run_controller: RunController = field(init=False, repr=False)

    @override
    def __post_init__(self) -> None:
        # Create UseCases
        get_sound_devices_use_case: GetSoundDevicesUseCase = GetSoundDevicesUseCase(
            sound_device_provider=self.sound_device_provider,
        )

        get_usb_devices_use_case: GetUsbDevicesUseCase = GetUsbDevicesUseCase(
            usb_device_provider=self.usb_device_provider,
        )

        # Wire Controllers
        sound_device_controller: SoundDeviceController = SoundDeviceController(
            get_sound_devices_use_case=get_sound_devices_use_case,
            sound_device_presenter=self.sound_device_presenter,
        )
        object.__setattr__(self, "sound_device_controller", sound_device_controller)

        usb_device_controller: UsbDeviceController = UsbDeviceController(
            get_usb_devices_use_case=get_usb_devices_use_case,
            usb_device_presenter=self.usb_device_presenter,
        )
        object.__setattr__(self, "usb_device_controller", usb_device_controller)

        # run_controller: RunController = RunController()
        # object.__setattr__(self, "run_controller", run_controller)


@dataclass(frozen=True, slots=True)
class HASApplicationFactory(BaseApplicationFactory[HASApplication], ABC):
    """Headphone Auto Switcher application information."""

    name: str = "Headphone Auto Switcher"
    description: str = "Automatically switches the SoundDevice to/from configured Headphones when powered on/off."
    version: str = "3.0.0a1"
