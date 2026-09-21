"""Interface view models, as described by Clean Architecture."""

from __future__ import annotations

import logging
from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger


logger: Logger = logging.getLogger("interface.view_model")


class BaseViewModel(ABC):
    """Base view model class, implementing Clean Architecture patterns."""


@dataclass(frozen=True)
class ErrorViewModel(BaseViewModel):
    """Represents an error with an optional error code."""

    message: str
    code: str | None = None


# ---------- Project Specific ---------- #


@dataclass(frozen=True, slots=True)
class SoundDeviceViewModel(BaseViewModel):
    """Represents a SoundDevice."""

    id: str
    type: str
    name: str
    default: str
