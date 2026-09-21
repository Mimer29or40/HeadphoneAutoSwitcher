"""Interface layer, as described by Clean Architecture."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger


logger: Logger = logging.getLogger("interface")
