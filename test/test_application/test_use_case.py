"""Tests for application.use_case."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from test_domain.conftest import DUMMY_ERROR_MSG
from test_domain.conftest import DummyService

from test_application.conftest import DummyPort
from test_application.conftest import DummyRepository
from test_application.conftest import DummyResponse
from test_application.conftest import DummyUseCase

if TYPE_CHECKING:
    from domain.exception import ErrorMsg


@pytest.mark.unit
class TestBaseUseCases:
    """Tests for BaseUseCases."""

    @pytest.fixture
    def use_case_obj(self) -> DummyUseCase:
        """UseCase fixture."""
        service: DummyService = DummyService()
        port: DummyPort = DummyPort("RESPONSE")
        repository: DummyRepository = DummyRepository([])
        response: DummyResponse = DummyResponse("RESPONSE")
        error_msg: ErrorMsg = DUMMY_ERROR_MSG

        return DummyUseCase(
            service=service,
            port=port,
            repository=repository,
            response=response,
            error_msg=error_msg,
        )

    def test_register_service(self, use_case_obj: DummyUseCase) -> None:
        """Test dynamically registering services at runtime."""
        # Arrange
        service_name: str = DummyUseCase.optional_service_name
        service: object = DummyUseCase.optional_service

        # Act
        use_case_obj.register_service(service_name, service)

        # Assert
        assert service_name in use_case_obj._optional_services  # noqa: SLF001
        assert use_case_obj._optional_services.get(service_name) is service  # noqa: SLF001

    def test_unregister_service(self, use_case_obj: DummyUseCase) -> None:
        """Test dynamically registering services at runtime."""
        # Arrange
        service_name: str = DummyUseCase.optional_service_name
        service: object = DummyUseCase.optional_service
        use_case_obj.register_service(service_name, service)

        # Act
        use_case_obj.unregister_service(service_name)

        # Assert
        assert service_name not in use_case_obj._optional_services  # noqa: SLF001


# ---------- Project Specific ---------- #


if __name__ == "__main__":
    pytest.main()
