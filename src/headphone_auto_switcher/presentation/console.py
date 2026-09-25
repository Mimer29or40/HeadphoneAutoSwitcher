"""Headphone Auto Switcher console presentation module."""

from __future__ import annotations

import logging.config
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

logger: Logger = logging.getLogger("has.presentation.console")
