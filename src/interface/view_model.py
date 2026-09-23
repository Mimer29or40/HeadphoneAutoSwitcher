"""Interface view models, as described by Clean Architecture."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from _ca.interface import BaseViewModel

if TYPE_CHECKING:
    from logging import Logger


logger: Logger = logging.getLogger("interface.view_model")


@dataclass(frozen=True, slots=True)
class SoundDeviceViewModel(BaseViewModel):
    """Represents a SoundDevice."""

    id: str
    type: str
    name: str
    selected: str
