"""Tests for interface.presenter."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from test_domain.conftest import DUMMY_ERROR_MSG

from interface.view_model import ErrorViewModel
from test_interface.conftest import DummyPresenter

if TYPE_CHECKING:
    from domain.exception import ErrorMsg


@pytest.fixture
def presenter() -> DummyPresenter:
    """Presenter fixture."""
    return DummyPresenter()


@pytest.mark.unit
def test_present_error(presenter: DummyPresenter) -> None:
    """Test for BasePresenter.present_error()."""
    # Arrange
    error_msg: ErrorMsg = DUMMY_ERROR_MSG

    # Act
    result: ErrorViewModel = presenter.present_error(error_msg)

    # Assert
    assert isinstance(result, ErrorViewModel)
    assert result.message == error_msg.message
    assert result.code == error_msg.code


@pytest.mark.unit
def test_present_validation_error(presenter: DummyPresenter) -> None:
    """Test for BasePresenter.present_validation_error()."""
    # Arrange
    exception: ValueError = ValueError("Validation error")

    # Act
    result: ErrorViewModel = presenter.present_validation_error(exception)

    # Assert
    assert isinstance(result, ErrorViewModel)
    assert result.message == str(exception)
    assert result.code == "VE"


# ---------- Project Specific ---------- #


if __name__ == "__main__":
    pytest.main()
