"""Tests for _ca.domain."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

import pytest

from test__ca.conftest import DUMMY_ERROR_MSG
from test__ca.conftest import DummyApplication
from test__ca.conftest import DummyEntity
from test__ca.conftest import DummyOutcome
from test__ca.conftest import DummyPort
from test__ca.conftest import DummyRepository
from test__ca.conftest import DummyRequest
from test__ca.conftest import DummyResponse
from test__ca.conftest import DummyService
from test__ca.conftest import DummyUseCase

if TYPE_CHECKING:
    from _ca.application import BaseApplication
    from _ca.application import BaseOutcome
    from _ca.application import BasePort
    from _ca.application import BaseRepository
    from _ca.application import BaseRequest
    from _ca.application import BaseResponse
    from _ca.domain import ErrorMsg


@pytest.mark.unit
class TestBaseApplication:
    """Tests for BaseApplication."""

    @pytest.fixture
    def application_obj(self) -> BaseApplication:
        """Application fixture."""
        return DummyApplication()

    def test_name(self, application_obj: BaseApplication) -> None:
        """Verify that the Application has a name."""
        assert hasattr(application_obj, "name")
        assert isinstance(application_obj.name, str)

    def test_description(self, application_obj: BaseApplication) -> None:
        """Verify that the Application has a description."""
        assert hasattr(application_obj, "description")
        assert isinstance(application_obj.description, str)

    def test_version(self, application_obj: BaseApplication) -> None:
        """Verify that the Application has a version."""
        assert hasattr(application_obj, "version")
        assert isinstance(application_obj.version, str)


@pytest.mark.unit
class TestBaseRequest:
    """Tests for BaseRequest."""

    @pytest.fixture
    def request_obj(self) -> BaseRequest:
        """BaseRequest fixture."""
        return DummyRequest("VALUE")

    def test_convert(self, request_obj: BaseRequest) -> None:
        """Tests for BaseRequest.convert()."""
        # Act
        result: dict[str, Any] = request_obj.convert()

        # Assert
        assert isinstance(result, dict)


@pytest.mark.unit
class TestBaseResponse:
    """Tests for BaseResponse."""

    def test_from_entity(self) -> None:
        """Tests for BaseRequest.from_entity()."""
        # Arrange
        entity: DummyEntity = DummyEntity("VALUE")

        # Act
        result: BaseResponse = DummyResponse.from_entity(entity)

        # Assert
        assert isinstance(result, DummyResponse)


@pytest.mark.unit
class TestBaseOutcome:
    """Tests for BaseOutcome."""

    def test_str(self) -> None:
        """Tests for BaseOutcome.__str__()."""
        # Arrange
        value: Any = "VALUE"
        outcome: BaseOutcome = DummyOutcome(value)

        # Act
        result: str = str(outcome)

        # Assert
        assert isinstance(result, str)


@pytest.mark.unit
class TestBasePort:
    """Tests for BasePort."""

    def test_port(self) -> None:
        """Test for BasePort."""
        _: BasePort = DummyPort("VALUE")


@pytest.mark.unit
class TestBaseRepository:
    """Tests for BaseRepository."""

    def test_repository(self) -> None:
        """Test for BaseRepository."""
        _: BaseRepository = DummyRepository([])


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


if __name__ == "__main__":
    pytest.main()
