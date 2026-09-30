"""Headphone Auto Switcher interface view model module."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ca.interface import BaseViewModel

if TYPE_CHECKING:
    from logging import Logger

logger: Logger = logging.getLogger("has.interface.view_model")


@dataclass(frozen=True, slots=True)
class SoundDeviceViewModel(BaseViewModel):
    """ViewModel for a SoundDevice."""

    id: str
    name: str
    type: str
    selected: str


@dataclass(frozen=True, slots=True)
class UsbDeviceViewModel(BaseViewModel):
    """ViewModel for a UsbDevice."""

    id: str
    product: str
    vendor: str


@dataclass(frozen=True, slots=True)
class ValidationViewModel(BaseViewModel):
    """ViewModel for a ValidationResult."""

    id: str
    is_valid: str
    reasons: list[str]
