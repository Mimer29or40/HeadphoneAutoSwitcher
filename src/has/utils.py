"""Headphone Auto Switcher utility module."""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from logging import Logger

logger: Logger = logging.getLogger("has.utils")


UUID_PATTERN: re.Pattern[str] = re.compile(
    r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
    flags=re.IGNORECASE,
)


def extract_uuid(string: str) -> UUID | None:
    """Extract a UUID from a string."""
    match: re.Match[str] | None = UUID_PATTERN.search(string)
    if match is None:
        return None
    hex: str = match.group(1)
    uuid: UUID = UUID(hex)
    return uuid
