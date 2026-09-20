"""Tests for interface.controller."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from test_application.conftest import DummyPort
from test_application.conftest import DummyRepository
from test_application.conftest import DummyResponse
from test_application.conftest import DummyUseCase
from test_domain.conftest import DUMMY_ERROR_MSG
from test_domain.conftest import DummyService

from test_interface.conftest import DummyController
from test_interface.conftest import DummyPresenter

if TYPE_CHECKING:
    from domain.exception import ErrorMsg
    from interface.controller import BaseController


@pytest.mark.unit
def test_controller() -> None:
    """Test for interface.controller.BaseController."""
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

    _: BaseController = DummyController(
        dummy_use_case=dummy_use_case,
        dummy_presenter=dummy_presenter,
    )


# ---------- Project Specific ---------- #


if __name__ == "__main__":
    pytest.main()
