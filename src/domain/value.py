"""Domain value objects, as described by Clean Architecture."""

from __future__ import annotations

import logging
from enum import Enum
from enum import auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger


logger: Logger = logging.getLogger("domain.value")


class SoundDeviceType(Enum):
    """Sound device types."""

    UNKNOWN = auto()
    INPUT = auto()
    OUTPUT = auto()
