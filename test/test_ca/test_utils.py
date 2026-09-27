"""Tests for ca.utils."""

from __future__ import annotations

import logging
import re
from collections.abc import Callable
from typing import TYPE_CHECKING
from typing import Any
from typing import Literal

import pytest
from conftest import make_parametrize

from ca.utils import TRACE
from ca.utils import Result
from ca.utils import ResultErr
from ca.utils import ResultOk
from ca.utils import log_call
from ca.utils import type_name

if TYPE_CHECKING:
    pass


LOG_CALL_PATTERN: re.Pattern[str] = re.compile(r"^(.*?)\((.*?)\)$")


class TestLogCall:
    """Tests for log_call()."""

    @pytest.mark.unit
    def test_global_default(self) -> None:  # TODO(Ryan): Do this
        """Test to verify that changing the global default value works."""

    @pytest.mark.unit
    def test_no_bracket_return(self) -> None:
        """Test for the return type of log_call() when no bracket are provided."""
        # Act

        @log_call
        def func() -> None:
            pass

        # Assert
        assert isinstance(func, Callable)

    @pytest.mark.unit
    @pytest.mark.parametrize(**make_parametrize("type", "method", "class", "static"))
    def test_type(self, caplog: pytest.LogCaptureFixture, type: Literal["method", "class", "static"]) -> None:
        """Test for log_call(type=Literal["method", "class", "static"])."""
        # Arrange

        @log_call(type=type)
        def func(_: int, __: int, ___: int) -> None:
            pass

        arg0: int = 1
        arg1: int = 1
        arg2: int = 1

        # Act
        with caplog.at_level(level=TRACE):
            func(arg0, arg1, arg2)

        # Assert
        assert len(caplog.messages) == 1, "log_call not called"
        message: str = caplog.messages[0]
        match: re.Match[str] | None = LOG_CALL_PATTERN.match(message)
        assert match is not None, "incorrect message"

        arguments: list[str] = match.group(2).split(", ")
        match type:
            case "method":
                assert len(arguments) == 2, "incorrect number of arguments"
            case "class" | "static":
                assert len(arguments) == 3, "incorrect number of arguments"

    @pytest.mark.unit
    @pytest.mark.parametrize(
        **make_parametrize(
            "level",
            logging.CRITICAL,
            logging.ERROR,
            logging.WARNING,
            logging.INFO,
            logging.DEBUG,
            TRACE,
        )
    )
    def test_level(self, caplog: pytest.LogCaptureFixture, level: int) -> None:
        """Test for log_call(type=Literal["method", "class", "static"])."""
        # Arrange

        @log_call(level=level)
        def func(_: int, __: int, ___: int) -> None:
            pass

        arg0: int = 1
        arg1: int = 1
        arg2: int = 1

        # Act
        with caplog.at_level(level=level):
            func(arg0, arg1, arg2)

        # Assert
        assert len(caplog.messages) == 1, "log_call not called"

    @pytest.mark.unit
    @pytest.mark.parametrize(**make_parametrize("arg_func", "class", "str", "repr"))
    def test_arg_func(self, caplog: pytest.LogCaptureFixture, arg_func: Literal["class", "str", "repr"]) -> None:
        """Test for log_call(type=Literal["method", "class", "static"])."""
        # Arrange

        @log_call(arg_func=arg_func)
        def func(_: int, __: int, ___: int) -> None:
            pass

        arg0: int = 1
        arg1: int = 1
        arg2: int = 1

        # Act
        with caplog.at_level(level=TRACE):
            func(arg0, arg1, arg2)

        # Assert
        assert len(caplog.messages) == 1, "log_call not called"
        message: str = caplog.messages[0]
        match: re.Match[str] | None = LOG_CALL_PATTERN.match(message)
        assert match is not None, "incorrect message"

        arguments: list[str] = match.group(2).split(", ")
        match arg_func:
            case "class":
                assert arguments == ["<int>", "<int>", "<int>"]
            case "str" | "repr":
                assert arguments == ["1", "1", "1"]


class TestTypeName:
    """Tests for type_name()."""

    @pytest.mark.unit
    @pytest.mark.parametrize(**make_parametrize("brackets", False, True))
    def test_brackets(self, brackets: bool) -> None:
        """Test for type_name(brackets=bool)."""
        # Arrange
        obj: Any = 1

        # Act
        result: str = type_name(obj, brackets=brackets)

        # Assert
        assert result == ("<int>" if brackets else "int")

    @pytest.mark.unit
    def test_iterable(self) -> None:
        """Test for type_name(obj=Iterable[T]())."""
        # Arrange
        obj: Any = ["1", "2", "3"]

        # Act
        result: str = type_name(obj)

        # Assert
        assert result == "<list[str](3)>"

    @pytest.mark.unit
    def test_iterable_uvw(self) -> None:
        """Test for type_name(obj=Iterable[U | V | W]())."""
        # Arrange
        obj: Any = [1, 2.0, "three"]

        # Act
        result: str = type_name(obj)

        # Assert
        assert result == "<list[int | float | str](3)>"

    @pytest.mark.unit
    def test_iterable_deep(self) -> None:
        """Test for type_name(obj=Iterable[Iterable[T]]())."""
        # Arrange
        obj: Any = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]]

        # Act
        result: str = type_name(obj)

        # Assert
        assert result == "<list[list[str](3)](3)>"

    @pytest.mark.unit
    def test_str(self) -> None:
        """Test for type_name(obj=str())."""
        # Arrange
        obj: Any = "string"

        # Act
        result: str = type_name(obj)

        # Assert
        assert result == "<str>"


class TestResult:
    """Tests for Result."""

    @pytest.mark.unit
    @pytest.mark.parametrize(
        **make_parametrize(
            ("result_obj", "expected"),
            (Result.ok(None), True),
            (Result.err(None), False),
        )
    )
    def test_is_ok(self, result_obj: Result, expected: bool) -> None:
        """Test for Result.is_ok(Result)."""
        # Act
        result: bool = Result.is_ok(result_obj)

        # Assert
        assert result == expected

    @pytest.mark.unit
    @pytest.mark.parametrize(
        **make_parametrize(
            ("result_obj", "expected"),
            (Result.ok(None), False),
            (Result.err(None), True),
        )
    )
    def test_is_err(self, result_obj: Result, expected: bool) -> None:
        """Test for Result.is_err(Result)."""
        # Act
        result: bool = Result.is_err(result_obj)

        # Assert
        assert result == expected

    @pytest.mark.unit
    def test_ok(self) -> None:
        """Test for Result.is_ok(Result)."""
        # Act
        value: Any = None

        # Act
        result: Result = Result.ok(value)

        # Assert
        assert isinstance(result, ResultOk)

    @pytest.mark.unit
    def test_err(self) -> None:
        """Test for Result.is_err(Result)."""
        # Act
        value: Any = None

        # Act
        result: Result = Result.err(value)

        # Assert
        assert isinstance(result, ResultErr)


if __name__ == "__main__":
    pytest.main()
