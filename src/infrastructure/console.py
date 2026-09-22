"""Infrastructure for console environments, as described by Clean Architecture."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import override

from _ca.infrastructure import LogConfigProvider
from interface.presenter import SoundDevicePresenter
from interface.view_model import SoundDeviceViewModel

if TYPE_CHECKING:
    from logging import Logger

    from application.dto import SoundDeviceResponse

logger: Logger = logging.getLogger("infrastructure.console")


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
            format = {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}

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
            default=response.default,
        )
