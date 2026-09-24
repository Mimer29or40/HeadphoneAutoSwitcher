"""Domain value objects, as described by Clean Architecture."""

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


logger: Logger = logging.getLogger("domain.value")


class SoundDeviceType(Enum):
    """Sound device types."""

    UNKNOWN = auto()
    INPUT = auto()
    OUTPUT = auto()


@dataclass(frozen=True, slots=True)
class UsbDevicePacket:
    """Represents a single packet from a UsbDevice."""

    time: float = field(default_factory=monotonic, init=False)
    data: list[int]
