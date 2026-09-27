"""Clean architecture utility module."""

from __future__ import annotations

import logging
from abc import ABC
from collections.abc import Callable
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Literal
from typing import TypeIs
from typing import final
from typing import overload

if TYPE_CHECKING:
    from logging import Logger

logger: Logger = logging.getLogger("utils")


TRACE: int = logging.DEBUG // 2
logging.addLevelName(TRACE, "TRACE")

type FuncCall[**P, R] = Callable[P, R]
type FuncDecorator[**P, R] = Callable[[FuncCall[P, R]], FuncCall[P, R]]
type DecoratorType[**P, R] = FuncCall[P, R] | FuncDecorator[P, R]

LOG_CALL_DEFAULT_LEVEL: int = TRACE
LOG_CALL_SENTINEL: Any = object()


@overload
def log_call[**P, R](method: FuncCall[P, R] | None = None, /) -> FuncCall[P, R]: ...


@overload
def log_call[**P, R](
    *,
    type: Literal["method", "class", "static"] = "static",
    level: int = LOG_CALL_SENTINEL,
    arg_func: Literal["class", "str", "repr"] = "class",
) -> FuncDecorator[P, R]: ...


def log_call[**P, R](
    method: FuncCall[P, R] | None = None,
    /,
    type: Literal["method", "class", "static"] = "static",
    level: int = LOG_CALL_SENTINEL,
    arg_func: Literal["class", "str", "repr"] = "class",
) -> DecoratorType[P, R]:
    """Log a method call at the level specified."""

    def decorator(func: FuncCall[P, R]) -> FuncCall[P, R]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            nonlocal level
            if level is LOG_CALL_SENTINEL:
                level = LOG_CALL_DEFAULT_LEVEL

            func_logger: Logger = logging.getLogger(func.__module__)
            if func_logger.isEnabledFor(level):
                func_name: str = func.__qualname__  # ty:ignore[unresolved-attribute]

                _arg_func: Callable[[Any], str] = {"class": type_name, "str": str, "repr": repr}[arg_func]

                arguments: list[str]
                match type:
                    case "method":
                        # Ignore self
                        arguments = [_arg_func(arg) for arg in args[1:]]
                    case "class":
                        # type(cls)
                        arguments = [type_name(args[0]), *map(_arg_func, args[1:])]
                    case "static":
                        # Everything goes
                        arguments = [_arg_func(arg) for arg in args]

                arguments.extend(f"{k}={_arg_func(v)}" for k, v in kwargs.items())

                func_logger.log(level, "%s(%s)", func_name, ", ".join(arguments))
            return func(*args, **kwargs)

        return wrapper

    if method is None:
        return decorator
    return decorator(method)


def type_name(obj: Any, *, brackets: bool = True) -> str:
    """Get the name of a type as a pretty string."""
    cls: type = type(obj)

    cls_str: str
    if issubclass(cls, Iterable) and cls is not str:
        obj_list: list = list(obj)
        cls_list: list[str] = list(dict.fromkeys(type_name(sub_obj, brackets=False) for sub_obj in obj_list))
        cls_str = f"{cls.__name__}[{' | '.join(cls_list)}]({len(obj_list)})"
    else:
        cls_str = cls.__name__

    if brackets:
        cls_str = f"<{cls_str}>"
    return cls_str


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
