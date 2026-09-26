"""Headphone Auto Switcher Application."""

from __future__ import annotations

import logging
from importlib.metadata import version
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

logger: Logger = logging.getLogger("has")


__version__: str = version("has")
