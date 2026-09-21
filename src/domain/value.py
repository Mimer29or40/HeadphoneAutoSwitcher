"""Domain value objects, as described by Clean Architecture."""

from __future__ import annotations

import logging
from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger


logger: Logger = logging.getLogger("domain.value")


@dataclass(frozen=True, slots=True)
class BaseValue(ABC):
    """Base value class, implementing Clean Architecture patterns."""


# ---------- Project Specific ---------- #

# TODO(Ryan): Make value classes
# class TitleStr(str):
#     __slots__ = ()
