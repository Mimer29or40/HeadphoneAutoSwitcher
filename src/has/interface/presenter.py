"""Headphone Auto Switcher interface presenter module."""

from __future__ import annotations

import logging
from abc import ABC
from typing import TYPE_CHECKING

from ca.interface import BasePresenter
from has.application.dto import SoundDeviceResponse
from has.application.dto import UsbDeviceResponse
from has.interface.view_model import SoundDeviceViewModel
from has.interface.view_model import UsbDeviceViewModel

if TYPE_CHECKING:
    from logging import Logger

logger: Logger = logging.getLogger("has.interface.presenter")


class SoundDevicePresenter(BasePresenter[SoundDeviceResponse, SoundDeviceViewModel], ABC):
    """Presenter for SoundDevices."""


class UsbDevicePresenter(BasePresenter[UsbDeviceResponse, UsbDeviceViewModel], ABC):
    """Presenter for UsbDevices."""
