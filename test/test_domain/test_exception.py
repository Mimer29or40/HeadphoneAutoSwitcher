"""Tests for domain.exception."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from test_domain.conftest import DUMMY_ERROR_MSG
from test_domain.conftest import DummyError

if TYPE_CHECKING:
    from domain.exception import BaseError
    from domain.exception import ErrorMsg


@pytest.mark.unit
class TestBaseError:
    """Tests for BaseError."""

    def test_message(self) -> None:
        """Tests for BaseError.message."""
        # Arrange
        error_msg: ErrorMsg = DUMMY_ERROR_MSG

        # Act
        result: BaseError = DummyError(error_msg)

        # Assert
        assert result.message == error_msg


# ---------- Project Specific ---------- #


if __name__ == "__main__":
    pytest.main()
