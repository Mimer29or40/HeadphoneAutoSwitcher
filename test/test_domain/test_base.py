"""Tests for domain.base."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

import pytest

from domain.base import Result
from domain.base import ResultErr
from domain.base import ResultOk

if TYPE_CHECKING:
    pass


@pytest.mark.unit
class TestResult:
    """Tests for Result."""

    class TestIsOk:
        """Tests for Result.is_ok()."""

        def test_ok(self) -> None:
            """Test for Result.is_ok() with an ok result."""
            # Arrange
            result: Result = Result.ok(None)

            # Act
            results: bool = Result.is_ok(result)

            # Assert
            assert results is True

        def test_err(self) -> None:
            """Test for Result.is_ok() with an err result."""
            # Arrange
            result: Result = Result.err(None)

            # Act
            results: bool = Result.is_ok(result)

            # Assert
            assert results is False

    class TestIsErr:
        """Tests for Result.is_err()."""

        def test_ok(self) -> None:
            """Test for Result.is_err() with an ok result."""
            # Arrange
            result: Result = Result.ok(None)

            # Act
            results: bool = Result.is_err(result)

            # Assert
            assert results is False

        def test_err(self) -> None:
            """Test for Result.is_err() with an err result."""
            # Arrange
            result: Result = Result.err(None)

            # Act
            results: bool = Result.is_err(result)

            # Assert
            assert results is True

    def test_ok(self) -> None:
        """Test for Result.ok()."""
        # Arrange
        value: Any = object()

        # Act
        result: Result = Result.ok(value)

        # Assert
        assert isinstance(result, ResultOk)
        assert result.value is value

    def test_err(self) -> None:
        """Test for Result.err()."""
        # Arrange
        value: Any = object()

        # Act
        result: Result = Result.err(value)

        # Assert
        assert isinstance(result, ResultErr)
        assert result.value is value


# ---------- Project Specific ---------- #


if __name__ == "__main__":
    pytest.main()
