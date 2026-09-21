"""Clean architecture utilities."""

from __future__ import annotations

import logging
from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import TypeIs
from typing import final

if TYPE_CHECKING:
    from logging import Logger

logger: Logger = logging.getLogger(__name__)


class Result[T, E](ABC):
    """The result of an operation, holding a value if successful and another if failed."""

    value: T | E

    @staticmethod
    def is_ok[Ok, Err](result: Result[Ok, Err]) -> TypeIs[ResultOk[Ok]]:
        """Return True, if the result was successful, False, otherwise."""
        return isinstance(result, ResultOk)

    @staticmethod
    def is_err[Ok, Err](result: Result[Ok, Err]) -> TypeIs[ResultErr[Err]]:
        """Return True, if the result was successful, False, otherwise."""
        return isinstance(result, ResultErr)

    @final
    @classmethod
    def ok[Ok](cls, value: Ok) -> Result[Ok, Any]:
        """Create a result with a successful value."""
        return ResultOk(value)

    @final
    @classmethod
    def err[Err](cls, value: Err) -> Result[Any, Err]:
        """Create a result with a failed value."""
        return ResultErr(value)


@final
@dataclass(frozen=True, slots=True)
class ResultOk[Ok](Result[Ok, Any]):
    """The result of an operational success, holding a value."""

    value: Ok


@final
@dataclass(frozen=True, slots=True)
class ResultErr[Err](Result[Any, Err]):
    """The result of an operational failure, holding a value."""

    value: Err
