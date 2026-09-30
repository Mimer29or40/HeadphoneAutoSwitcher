"""Headphone Auto Switcher domain entity module."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ca.domain import BaseEntity
from ca.domain import ErrorMsg

if TYPE_CHECKING:
    from logging import Logger

    from has.domain.value import SoundDeviceType

logger: Logger = logging.getLogger("has.domain.entity")


@dataclass(eq=False, kw_only=True)
class SoundDevice(BaseEntity):  # TODO(Ryan): More fields
    """A sound device on the system."""

    name: str
    type: SoundDeviceType
    selected: bool


@dataclass(eq=False, kw_only=True)
class UsbDevice(BaseEntity):  # TODO(Ryan): More fields
    """A USB device on the system."""

    product_name: str
    product_id: int
    vendor_name: str
    vendor_id: int


@dataclass(eq=False, kw_only=True)
class Validation(BaseEntity):
    """Validation result of the application configuration."""

    reasons: list[ErrorMsg]

    @property
    def is_valid(self) -> bool:
        """Return True, if the configuration is valid, False otherwise."""
        return len(self.reasons) == 0
