"""Domain value objects, as described by Clean Architecture."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ca.domain import BaseEntity

if TYPE_CHECKING:
    from logging import Logger


logger: Logger = logging.getLogger("domain.entity")


@dataclass(eq=False)
class SoundDevice(BaseEntity):  # TODO(Ryan): More fields
    """Represents a sound device on the system."""

    type: str
    name: str
    default: str
