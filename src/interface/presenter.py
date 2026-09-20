"""Interface presenters, as described by Clean Architecture."""

from __future__ import annotations

import logging
from abc import ABC
from typing import TYPE_CHECKING

from interface.view_model import ErrorViewModel

if TYPE_CHECKING:
    from logging import Logger

    from domain.exception import ErrorMsg


logger: Logger = logging.getLogger("interface.presenter")


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


# ---------- Project Specific ---------- #
