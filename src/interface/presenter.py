"""Interface presenters, as described by Clean Architecture."""

from __future__ import annotations

import logging
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

from ca.interface import BasePresenter

if TYPE_CHECKING:
    from logging import Logger

    from application.dto import SoundDeviceResponse
    from interface.view_model import SoundDeviceViewModel


logger: Logger = logging.getLogger("interface.presenter")


class SoundDevicePresenter(BasePresenter, ABC):
    """Presenter for SoundDevices."""

    @abstractmethod
    def present_sound_device(self, sound_device: SoundDeviceResponse) -> SoundDeviceViewModel:
        """Convert response to view model."""

    def present_sound_devices(self, sound_devices: list[SoundDeviceResponse]) -> list[SoundDeviceViewModel]:
        """Convert response to view model."""
        return [self.present_sound_device(sound_device) for sound_device in sound_devices]
