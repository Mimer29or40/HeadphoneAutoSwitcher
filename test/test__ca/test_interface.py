"""Tests for _ca.domain."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from _ca.interface import BaseViewModel
from _ca.interface import ErrorViewModel
from test__ca.conftest import DUMMY_ERROR_MSG
from test__ca.conftest import DummyController
from test__ca.conftest import DummyPort
from test__ca.conftest import DummyPresenter
from test__ca.conftest import DummyRepository
from test__ca.conftest import DummyResponse
from test__ca.conftest import DummyService
from test__ca.conftest import DummyUseCase
from test__ca.conftest import DummyViewModel

if TYPE_CHECKING:
    from _ca.domain import ErrorMsg
    from _ca.interface import BaseController
    from _ca.interface import BasePresenter


@pytest.mark.unit
class TestBaseController:
    """Tests for BaseController."""

    @pytest.fixture
    def controller_obj(self) -> BaseController:
        """Controller fixture."""
        service: DummyService = DummyService()
        port: DummyPort = DummyPort("RESPONSE")
        repository: DummyRepository = DummyRepository([])
        response: DummyResponse = DummyResponse("RESPONSE")
        error_msg: ErrorMsg = DUMMY_ERROR_MSG

        dummy_use_case: DummyUseCase = DummyUseCase(
            service=service,
            port=port,
            repository=repository,
            response=response,
            error_msg=error_msg,
        )
        dummy_presenter: DummyPresenter = DummyPresenter()

        return DummyController(
            dummy_use_case=dummy_use_case,
            dummy_presenter=dummy_presenter,
        )

    def test_controller(self, controller_obj: BaseController) -> None:
        """Test for BaseController."""
        _: BaseController = controller_obj


@pytest.mark.unit
class TestBasePresenter:
    """Tests for BasePresenter."""

    @pytest.fixture
    def presenter_obj(self) -> BasePresenter:
        """Presenter fixture."""
        return DummyPresenter()

    def test_present_error(self, presenter_obj: DummyPresenter) -> None:
        """Test for BasePresenter.present_error()."""
        # Arrange
        error_msg: ErrorMsg = DUMMY_ERROR_MSG

        # Act
        result: ErrorViewModel = presenter_obj.present_error(error_msg)

        # Assert
        assert isinstance(result, ErrorViewModel)
        assert result.message == error_msg.message
        assert result.code == error_msg.code

    def test_present_validation_error(self, presenter_obj: DummyPresenter) -> None:
        """Test for BasePresenter.present_validation_error()."""
        # Arrange
        exception: ValueError = ValueError("Validation error")

        # Act
        result: ErrorViewModel = presenter_obj.present_validation_error(exception)

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
