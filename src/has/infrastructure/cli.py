"""Headphone Auto Switcher command line interface infrastructure framework implementation."""

from __future__ import annotations

import logging.config
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import override

from ca.infrastructure import LogConfigProvider
from has.application.config import Config
from has.application.config import ConfigValidator
from has.infrastructure.application import HASApplication
from has.infrastructure.application import HASApplicationFactory

if TYPE_CHECKING:
    from logging import Logger

    from ca.application import BaseConfigProvider
    from has.domain.service import SoundDeviceProvider
    from has.domain.service import UsbDevicePacketListener
    from has.domain.service import UsbDeviceProvider
    from has.interface.presenter import SoundDevicePresenter
    from has.interface.presenter import UsbDevicePresenter
    from has.interface.presenter import ValidationPresenter

logger: Logger = logging.getLogger("has.infrastructure.cli")


DEFAULT_CONSOLE_LOG_FORMAT: dict[str, Any] = {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}


@dataclass(frozen=True, slots=True)
class CLILogConfigProvider(LogConfigProvider):
    """Console logging configuration."""

    level: str = "WARNING"
    format: dict[str, Any] | None = None

    @override
    def get(self) -> dict[str, Any]:
        """Get the logging configuration."""
        format: dict[str, Any] | None = self.format
        if format is None:
            format = DEFAULT_CONSOLE_LOG_FORMAT

        return {
            "version": 1,
            "incremental": False,
            "disable_existing_loggers": False,
            "formatters": {"standard": format},
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": self.level,
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {"level": self.level, "handlers": ["console"]},
        }


@dataclass(frozen=True, slots=True)
class CLIHASApplicationFactory(HASApplicationFactory):
    """Headphone Auto Switcher command line interface application factory."""

    @override
    def create(self) -> HASApplication:
        # Create application with dependencies
        from ca.application import JsonConfigProvider
        from has.infrastructure._pywinusb import PyWinUsbListener
        from has.infrastructure._pywinusb import PyWinUsbProvider
        from has.infrastructure._pydantic import PydanticValidator
        from has.infrastructure._sound_volume_view import SoundVolumeView
        from has.infrastructure.presentation.console import ConsoleSoundDevicePresenter
        from has.infrastructure.presentation.console import ConsoleUsbDevicePresenter
        from has.infrastructure.presentation.console import ConsoleValidationPresenter

        # Config
        config_file: Path = Path.cwd() / "HeadphoneAutoSwitcher.json"
        config_provider: BaseConfigProvider[Config] = JsonConfigProvider(
            config_cls=Config,
            file=config_file,
        )
        config: Config = config_provider.get()
        config_validator: ConfigValidator = PydanticValidator()

        # Services
        sound_device_provider: SoundDeviceProvider = SoundVolumeView()
        usb_device_provider: UsbDeviceProvider = PyWinUsbProvider()
        usb_device_packet_listener: UsbDevicePacketListener = PyWinUsbListener()

        # Presenters
        sound_device_presenter: SoundDevicePresenter = ConsoleSoundDevicePresenter()
        usb_device_presenter: UsbDevicePresenter = ConsoleUsbDevicePresenter()
        validation_presenter: ValidationPresenter = ConsoleValidationPresenter()

        app: HASApplication = HASApplication(
            config=config,
            config_validator=config_validator,
            sound_device_provider=sound_device_provider,
            usb_device_provider=usb_device_provider,
            usb_device_packet_listener=usb_device_packet_listener,
            sound_device_presenter=sound_device_presenter,
            usb_device_presenter=usb_device_presenter,
            validation_presenter=validation_presenter,
        )
        return app
