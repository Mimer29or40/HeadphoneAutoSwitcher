"""Headphone Auto Switcher domain error module."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ca.domain import ServiceError

if TYPE_CHECKING:
    from logging import Logger

logger: Logger = logging.getLogger("has.domain.error")


class SoundDeviceProviderError(ServiceError):
    """Error raised when a SoundDeviceProvider fails."""


class UsbDeviceProviderError(ServiceError):
    """Error raised when a UsbDeviceProvider fails."""


class UsbDevicePacketListenerError(ServiceError):
    """Error raised when a UsbDeviceProvider fails."""
