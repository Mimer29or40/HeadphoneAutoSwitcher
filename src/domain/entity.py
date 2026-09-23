"""Domain value objects, as described by Clean Architecture."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from _ca.domain import BaseEntity

if TYPE_CHECKING:
    from logging import Logger

    from domain.value import SoundDeviceType


logger: Logger = logging.getLogger("domain.entity")


@dataclass(eq=False)
class SoundDevice(BaseEntity):  # TODO(Ryan): More fields
    """Represents a sound device on the system."""

    type: SoundDeviceType
    name: str
    selected: bool


@dataclass(eq=False)
class UsbDevice(BaseEntity):  # TODO(Ryan): More fields
    """Represents a USB device on the system."""

    serial_number: str
    vendor_name: str
    vendor_id: int
    product_name: str
    product_id: int
    version_number: int
