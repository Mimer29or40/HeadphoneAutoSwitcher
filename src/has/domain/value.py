"""Headphone Auto Switcher domain value module."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from enum import auto
from time import monotonic
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

logger: Logger = logging.getLogger("has.domain.value")


class SoundDeviceType(Enum):
    """Sound device type."""

    UNKNOWN = auto()
    INPUT = auto()
    OUTPUT = auto()


@dataclass(frozen=True, slots=True)
class UsbDevicePacket:
    """Usb device packet."""

    time: float = field(default_factory=monotonic, init=False)
    data: list[int]
