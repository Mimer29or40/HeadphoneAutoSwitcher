"""Infrastructure for console environments, as described by Clean Architecture."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import override

from _ca.infrastructure import LogConfigProvider
from interface.presenter import SoundDevicePresenter
from interface.presenter import UsbDevicePresenter
from interface.view_model import SoundDeviceViewModel
from interface.view_model import UsbDeviceViewModel

if TYPE_CHECKING:
    from logging import Logger

    from application.dto import SoundDeviceResponse
    from application.dto import UsbDeviceResponse

logger: Logger = logging.getLogger("infrastructure.console")


DEFAULT_CONSOLE_LOG_FORMAT: dict[str, Any] = {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}


@dataclass(frozen=True, slots=True)
class ConsoleLogConfigProvider(LogConfigProvider):
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


class ConsoleSoundDevicePresenter(SoundDevicePresenter):
    """SoundDevicePresenter for the console."""

    @override
    def present_sound_device(self, response: SoundDeviceResponse) -> SoundDeviceViewModel:
        return SoundDeviceViewModel(
            id=response.id,
            type=response.type,
            name=response.name,
            selected="Selected" if response.selected else "",
        )


class ConsoleUsbDevicePresenter(UsbDevicePresenter):
    """UsbDevicePresenter for the console."""

    @override
    def present_usb_device(self, response: UsbDeviceResponse) -> UsbDeviceViewModel:
        return UsbDeviceViewModel(
            id=response.id,
            serial_number=response.serial_number,
            vendor=f"{response.vendor_name} (0x{response.vendor_id:04X})",
            product=f"{response.product_name} (0x{response.product_id:04X})",
            version_number=str(response.version_number),
        )
