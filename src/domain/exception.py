"""Exceptions used by the application."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from _ca.domain import BaseError

if TYPE_CHECKING:
    from logging import Logger


logger: Logger = logging.getLogger("domain.exception")


class SoundDeviceProviderError(BaseError):
    """Exception raised when a SoundDeviceProvider fails."""


class UsbDeviceProviderError(BaseError):
    """Exception raised when a UsbDeviceProvider fails."""
