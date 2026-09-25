"""Clean architecture interface module."""

from __future__ import annotations

import logging.config
from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

logger: Logger = logging.getLogger("ca.interface")


# ---------- Controller ---------- #


class BaseController(ABC):
    """Clean architecture base controller class."""
