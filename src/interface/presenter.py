"""Interface presenters, as described by Clean Architecture."""

from __future__ import annotations

import logging
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

from _ca.interface import BasePresenter

if TYPE_CHECKING:
    from logging import Logger

    from application.dto import SoundDeviceResponse
    from application.dto import UsbDeviceResponse
    from interface.view_model import SoundDeviceViewModel
    from interface.view_model import UsbDeviceViewModel


logger: Logger = logging.getLogger("interface.presenter")


class SoundDevicePresenter(BasePresenter, ABC):
    """Presenter for SoundDevices."""

    @abstractmethod
    def present_sound_device(self, response: SoundDeviceResponse) -> SoundDeviceViewModel:
        """Convert response to view model."""

    def present_sound_devices(self, responses: list[SoundDeviceResponse]) -> list[SoundDeviceViewModel]:
        """Convert response to view model."""
        return [self.present_sound_device(response) for response in responses]


class UsbDevicePresenter(BasePresenter, ABC):
    """Presenter for UsbDevices."""

    @abstractmethod
    def present_usb_device(self, response: UsbDeviceResponse) -> UsbDeviceViewModel:
        """Convert response to view model."""

    def present_usb_devices(self, responses: list[UsbDeviceResponse]) -> list[UsbDeviceViewModel]:
        """Convert response to view model."""
        return [self.present_usb_device(response) for response in responses]
