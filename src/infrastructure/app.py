"""Infrastructure application, as described by Clean Architecture."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import override

from _ca.application import BaseApplication
from application.use_case import GetSoundDevicesUseCase
from application.use_case import GetUsbDevicesUseCase
from interface.controller import SoundDeviceController
from interface.controller import UsbDeviceController

if TYPE_CHECKING:
    from logging import Logger

    from domain.service import SoundDeviceProvider
    from domain.service import UsbDeviceProvider
    from interface.presenter import SoundDevicePresenter
    from interface.presenter import UsbDevicePresenter


logger: Logger = logging.getLogger("infrastructure.app")


@dataclass(frozen=True, kw_only=True, slots=True)
class HeadphoneAutoSwitcherApplication(BaseApplication):
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
    usb_device_provider: UsbDeviceProvider
    usb_device_presenter: UsbDevicePresenter

    # Use cases
    get_sound_devices_use_case: GetSoundDevicesUseCase = field(init=False)
    usb_devices_use_case: GetUsbDevicesUseCase = field(init=False)

    # Controllers
    sound_device_controller: SoundDeviceController = field(init=False)
    usb_device_controller: UsbDeviceController = field(init=False)

    @override
    def __post_init__(self) -> None:
        # Wire use cases
        get_sound_devices_use_case = GetSoundDevicesUseCase(
            sound_device_provider=self.sound_device_provider,
        )
        object.__setattr__(self, "get_sound_devices_use_case", get_sound_devices_use_case)

        get_usb_devices_use_case = GetUsbDevicesUseCase(
            usb_device_provider=self.usb_device_provider,
        )
        object.__setattr__(self, "get_usb_devices_use_case", get_usb_devices_use_case)

        # Wire controllers
        sound_device_controller = SoundDeviceController(
            get_sound_devices_use_case=get_sound_devices_use_case,
            sound_device_presenter=self.sound_device_presenter,
        )
        object.__setattr__(self, "sound_device_controller", sound_device_controller)

        usb_device_controller = UsbDeviceController(
            get_usb_devices_use_case=get_usb_devices_use_case,
            usb_device_presenter=self.usb_device_presenter,
        )
        object.__setattr__(self, "usb_device_controller", usb_device_controller)
