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
from has.application.use_case import ListenUseCase
from has.application.use_case import RunUseCase
from has.application.use_case import ValidationUseCase
from has.interface.controller import SoundDeviceController
from has.interface.controller import SwitcherController
from has.interface.controller import UsbDeviceController

if TYPE_CHECKING:
    from logging import Logger

    from has.application.config import Config
    from has.application.config import ConfigValidator
    from has.domain.service import SoundDeviceProvider
    from has.domain.service import UsbDevicePacketListener
    from has.domain.service import UsbDeviceProvider
    from has.interface.presenter import SoundDevicePresenter
    from has.interface.presenter import UsbDevicePresenter
    from has.interface.presenter import ValidationPresenter

logger: Logger = logging.getLogger("ca.infrastructure.application")


@dataclass(frozen=True, slots=True)
class HASApplication(BaseApplication):
    """Headphone Auto Switcher application container."""

    # Config
    config: Config
    config_validator: ConfigValidator

    # Services
    sound_device_provider: SoundDeviceProvider
    usb_device_provider: UsbDeviceProvider
    usb_device_packet_listener: UsbDevicePacketListener

    # Presenters
    sound_device_presenter: SoundDevicePresenter
    usb_device_presenter: UsbDevicePresenter
    validation_presenter: ValidationPresenter

    # Controllers
    sound_device_controller: SoundDeviceController = field(init=False, repr=False)
    usb_device_controller: UsbDeviceController = field(init=False, repr=False)
    switcher_controller: SwitcherController = field(init=False, repr=False)

    @override
    def __post_init__(self) -> None:
        # Create UseCases
        get_sound_devices_use_case: GetSoundDevicesUseCase = GetSoundDevicesUseCase(
            sound_device_provider=self.sound_device_provider,
        )

        get_usb_devices_use_case: GetUsbDevicesUseCase = GetUsbDevicesUseCase(
            usb_device_provider=self.usb_device_provider,
        )

        validation_use_case: ValidationUseCase = ValidationUseCase(
            config=self.config,
            config_validator=self.config_validator,
            usb_device_provider=self.usb_device_provider,
        )
        listen_use_case: ListenUseCase = ListenUseCase(
            config=self.config,
            usb_device_packet_listener=self.usb_device_packet_listener,
        )
        run_use_case: RunUseCase = RunUseCase(
            config=self.config,
            usb_device_packet_listener=self.usb_device_packet_listener,
        )

        # Wire Controllers
        sound_device_controller: SoundDeviceController = SoundDeviceController(
            get_sound_devices_use_case=get_sound_devices_use_case,
            presenter=self.sound_device_presenter,
        )
        object.__setattr__(self, "sound_device_controller", sound_device_controller)

        usb_device_controller: UsbDeviceController = UsbDeviceController(
            get_usb_devices_use_case=get_usb_devices_use_case,
            presenter=self.usb_device_presenter,
        )
        object.__setattr__(self, "usb_device_controller", usb_device_controller)

        switcher_controller: SwitcherController = SwitcherController(
            validation_use_case=validation_use_case,
            listen_use_case=listen_use_case,
            run_use_case=run_use_case,
            presenter=self.validation_presenter,
        )
        object.__setattr__(self, "switcher_controller", switcher_controller)


@dataclass(frozen=True, slots=True)
class HASApplicationFactory(BaseApplicationFactory[HASApplication], ABC):
    """Headphone Auto Switcher application information."""

    name: str = "Headphone Auto Switcher"
    description: str = "Automatically switches the SoundDevice to/from configured Headphones when powered on/off."
    version: str = "3.0.0a1"
