"""Clean architecture presentation module."""

from __future__ import annotations

import logging.config
from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

    from ca.domain import ErrorMsg

logger: Logger = logging.getLogger("ca.presentation")


# ---------- View Model ---------- #


class BaseViewModel(ABC):
    """Clean architecture base view model class."""


@dataclass(frozen=True, slots=True)
class ErrorViewModel(BaseViewModel):
    """Clean architecture base view model class."""

    message: str
    code: str | None


# ---------- Presenter ---------- #


class BasePresenter(ABC):
    """Clean architecture base presenter class."""

    @staticmethod
    def present_error(message: ErrorMsg) -> ErrorViewModel:
        """Create an ErrorViewModel from an ErrorMsg."""
        return ErrorViewModel(message=message.message, code=message.code)

    @staticmethod
    def present_validation_error(error: ValueError) -> ErrorViewModel:
        """Create an ErrorViewModel from a validation error."""
        return ErrorViewModel(message=str(error), code="VALIDATION_ERROR")
