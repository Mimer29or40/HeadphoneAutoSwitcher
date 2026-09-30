"""Headphone Auto Switcher application config module."""

from __future__ import annotations

import logging
from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ca.application import BaseConfig
from ca.application import BaseConfigProvider
from ca.application import BaseConfigValidator

if TYPE_CHECKING:
    from logging import Logger

logger: Logger = logging.getLogger("has.application.config")


@dataclass(frozen=True, slots=True)
class Config(BaseConfig):
    """HeadphoneAutoSwitcher config data structure."""

    vendor_id: str
    product_id: str
    capture_device: str
    render_device: str


class ConfigProvider(BaseConfigProvider[Config], ABC):
    """HeadphoneAutoSwitcher config provider class."""


class ConfigValidator(BaseConfigValidator[Config], ABC):
    """HeadphoneAutoSwitcher config validator class."""
