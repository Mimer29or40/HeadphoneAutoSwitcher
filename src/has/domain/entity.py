"""Headphone Auto Switcher domain entity module."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ca.domain import BaseEntity

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
