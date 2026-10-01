"""Clean architecture interface module."""

from __future__ import annotations

import logging.config
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import override

from ca.application import BaseResponse
from ca.utils import log_call

if TYPE_CHECKING:
    from collections.abc import Iterable
    from logging import Logger

    from ca.domain import ErrorMsg

logger: Logger = logging.getLogger("ca.interface")


# ---------- ViewModel ---------- #


class BaseViewModel(ABC):
    """Clean architecture base view model class."""


@dataclass(frozen=True, slots=True)
class ErrorViewModel(BaseViewModel):
    """Clean architecture base view model class."""

    message: str
    code: str | None


# ---------- Presenter ---------- #


class BasePresenter[RES: BaseResponse, VM: BaseViewModel](ABC):
    """Clean architecture base presenter class."""

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"

    @classmethod
    @abstractmethod
    def present(cls, response: RES) -> VM:
        """Create a ViewModel from a Response."""

    @classmethod
    @log_call(type="class")
    def present_many(cls, responses: Iterable[RES]) -> list[VM]:
        """Create multiple ViewModels from multiple Responses."""
        return [cls.present(response) for response in responses]

    @classmethod
    @log_call(type="class")
    def present_error(cls, message: ErrorMsg) -> ErrorViewModel:
        """Create an ErrorViewModel from an ErrorMsg."""
        return ErrorViewModel(message=message.message, code=message.code)

    @classmethod
    @log_call(type="class")
    def present_validation_error(cls, error: ValueError) -> ErrorViewModel:
        """Create an ErrorViewModel from a validation error."""
        return ErrorViewModel(message=str(error), code="VALIDATION_ERROR")


# ---------- Controller ---------- #


class BaseController(ABC):
    """Clean architecture base controller class."""
