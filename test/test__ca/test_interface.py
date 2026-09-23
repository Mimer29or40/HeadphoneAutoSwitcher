"""Tests for _ca.domain."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from _ca.interface import BaseViewModel
from _ca.interface import ErrorViewModel
from test__ca.conftest import DUMMY_ERROR_MSG
from test__ca.conftest import DummyPresenter
from test__ca.conftest import DummyViewModel

if TYPE_CHECKING:
    from _ca.domain import ErrorMsg
    from _ca.interface import BaseController


@pytest.mark.unit
class TestBaseController:
    """Tests for BaseController."""

    def test_controller(self, dummy_controller: BaseController) -> None:
        """Test for BaseController."""
        _: BaseController = dummy_controller


@pytest.mark.unit
class TestBasePresenter:
    """Tests for BasePresenter."""

    def test_present_error(self, dummy_presenter: DummyPresenter) -> None:
        """Test for BasePresenter.present_error()."""
        # Arrange
        error_msg: ErrorMsg = DUMMY_ERROR_MSG

        # Act
        result: ErrorViewModel = dummy_presenter.present_error(error_msg)

        # Assert
        assert isinstance(result, ErrorViewModel)
        assert result.message == error_msg.message
        assert result.code == error_msg.code

    def test_present_validation_error(self, dummy_presenter: DummyPresenter) -> None:
        """Test for BasePresenter.present_validation_error()."""
        # Arrange
        exception: ValueError = ValueError("Validation error")

        # Act
        result: ErrorViewModel = dummy_presenter.present_validation_error(exception)

        # Assert
        assert isinstance(result, ErrorViewModel)
        assert result.message == str(exception)
        assert result.code == "VE"


@pytest.mark.unit
class TestBaseViewModel:
    """Tests for BaseViewModel."""

    @pytest.fixture
    def view_model_obj(self) -> BaseViewModel:
        """ViewModel fixture."""
        return DummyViewModel("VALUE")

    def test_controller(self, view_model_obj: BaseViewModel) -> None:
        """Test for BaseViewModel."""
        _: BaseViewModel = view_model_obj


if __name__ == "__main__":
    pytest.main()
