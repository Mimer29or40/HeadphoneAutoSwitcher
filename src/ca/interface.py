"""Interface layer, as described by Clean Architecture."""

from __future__ import annotations

import logging
from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger

    from ca.domain import ErrorMsg


logger: Logger = logging.getLogger("interface")


class BaseController(ABC):
    """Base controller class, implementing Clean Architecture patterns."""


class BasePresenter(ABC):
    """Base presenter class, implementing Clean Architecture patterns."""

    @staticmethod
    def present_error(error_msg: ErrorMsg) -> ErrorViewModel:
        """Create an ErrorViewModel from an ErrorMsg."""
        return ErrorViewModel(message=error_msg.message, code=error_msg.code)

    @staticmethod
    def present_validation_error(exception: ValueError) -> ErrorViewModel:
        """Create an ErrorViewModel for a validation error."""
        return ErrorViewModel(message=str(exception), code="VE")


class BaseViewModel(ABC):
    """Base view model class, implementing Clean Architecture patterns."""


@dataclass(frozen=True, slots=True)
class ErrorViewModel(BaseViewModel):
    """Represents an error with an optional error code."""

    message: str
    code: str | None = None
