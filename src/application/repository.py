"""Application repositories, as described by Clean Architecture."""

from __future__ import annotations

import logging
from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger


logger: Logger = logging.getLogger("application.repository")


class BaseRepository(ABC):
    """Base repository class, implementing Clean Architecture patterns."""


# ---------- Project Specific ---------- #
