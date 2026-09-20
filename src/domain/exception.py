"""Exceptions used by the application."""

from __future__ import annotations

import logging
from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import override

if TYPE_CHECKING:
    from logging import Logger


logger: Logger = logging.getLogger("domain.exception")


@dataclass(frozen=True, slots=True)
class ErrorMsg:
    """Exception raised when an error occurs."""

    message: str
    code: str | None = None


class BaseError(BaseException, ABC):
    """Base error class, implementing Clean Architecture patterns."""

    @override
    def __init__(self, message: ErrorMsg) -> None:
        super().__init__(message)

        self.message: ErrorMsg = message


# ---------- Project Specific ---------- #
