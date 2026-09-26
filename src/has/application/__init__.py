"""Headphone Auto Switcher application module."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

logger: Logger = logging.getLogger("has.application")
