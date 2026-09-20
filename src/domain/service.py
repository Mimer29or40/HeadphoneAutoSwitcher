"""Domain services, as described by Clean Architecture."""

from __future__ import annotations

import logging
from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger


logger: Logger = logging.getLogger("domain.service")


class BaseService(ABC):
    """Base service class, implementing Clean Architecture patterns."""


# ---------- Project Specific ---------- #
