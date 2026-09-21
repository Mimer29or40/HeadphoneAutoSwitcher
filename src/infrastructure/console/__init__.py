"""Infrastructure for console based interactions."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import override

from domain.base import Result
from infrastructure.application import Application
from infrastructure.logger import LogConfigProvider
from infrastructure.logger import configure_logging
from infrastructure.service import SoundVolumeView
from interface.presenter import SoundDevicePresenter
from interface.view_model import ErrorViewModel
from interface.view_model import SoundDeviceViewModel

if TYPE_CHECKING:
    from logging import Logger

    from application.dto import SoundDeviceResponse
    from domain.service import SoundDeviceProvider


logger: Logger = logging.getLogger("infrastructure.console")


type ConsoleResult = str | int | None


@dataclass(frozen=True, slots=True)
class DefaultLogConfigProvider(LogConfigProvider):
    """Default logging configuration."""

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
    def present_sound_device(self, sound_device: SoundDeviceResponse) -> SoundDeviceViewModel:
        return SoundDeviceViewModel(
            id=sound_device.id,
            direction=sound_device.type,
            name=sound_device.name,
            default=sound_device.default,
        )


def main(*_: Any) -> ConsoleResult:
    """Main entry point for the console application."""
    try:
        # Configure logging
        log_config_provider: DefaultLogConfigProvider = DefaultLogConfigProvider(level="DEBUG")
        configure_logging(log_config_provider)

        # Create application with dependencies
        sound_device_provider: SoundDeviceProvider = SoundVolumeView()
        sound_device_presenter: SoundDevicePresenter = ConsoleSoundDevicePresenter()

        app: Application = Application(
            sound_device_provider=sound_device_provider,
            sound_device_presenter=sound_device_presenter,
        )

        # Create and run appropriate CLI implementation  # TODO(Ryan): Do this
        result: Result[list[SoundDeviceViewModel], ErrorViewModel] = (
            app.sound_device_controller.handle_get_sound_devices()
        )

        if Result.is_ok(result):
            devices: list[SoundDeviceViewModel] = result.value

            device: SoundDeviceViewModel
            for device in devices:
                logger.info(device)
            return 0

        if Result.is_err(result):
            error_vm: ErrorViewModel = result.value
            logger.error(error_vm)
            return 1
    except KeyboardInterrupt:
        logger.critical("User interrupted")
        return "USER_INTERRUPT"
    except Exception as e:
        logger.exception("Unhandled exception:", exc_info=e)
        return -1
    return 0  # This will never happen


# ---------- Project Specific ---------- #
