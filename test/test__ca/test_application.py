"""Tests for _ca.domain."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

import pytest

from test__ca.conftest import DummyApplication
from test__ca.conftest import DummyEntity
from test__ca.conftest import DummyOutcome
from test__ca.conftest import DummyPort
from test__ca.conftest import DummyRepository
from test__ca.conftest import DummyRequest
from test__ca.conftest import DummyResponse
from test__ca.conftest import DummyUseCase

if TYPE_CHECKING:
    from _ca.application import BaseApplication
    from _ca.application import BaseOutcome
    from _ca.application import BasePort
    from _ca.application import BaseRepository
    from _ca.application import BaseRequest
    from _ca.application import BaseResponse
    from _ca.application import BaseUseCase


@pytest.mark.unit
class TestBaseApplication:
    """Tests for BaseApplication."""

    def test_name(self, dummy_application: DummyApplication) -> None:
        """Verify that the Application has a name."""
        application: BaseApplication = dummy_application

        assert hasattr(application, "name")
        assert isinstance(application.name, str)

    def test_description(self, dummy_application: BaseApplication) -> None:
        """Verify that the Application has a description."""
        application: BaseApplication = dummy_application

        assert hasattr(application, "description")
        assert isinstance(application.description, str)

    def test_version(self, dummy_application: BaseApplication) -> None:
        """Verify that the Application has a version."""
        application: BaseApplication = dummy_application

        assert hasattr(application, "version")
        assert isinstance(application.version, str)


@pytest.mark.unit
class TestBaseRequest:
    """Tests for BaseRequest."""

    def test_convert(self, dummy_request: DummyRequest) -> None:
        """Tests for BaseRequest.convert()."""
        # Arrange
        request: BaseRequest = dummy_request

        # Act
        result: dict[str, Any] = request.convert()

        # Assert
        assert isinstance(result, dict)


@pytest.mark.unit
class TestBaseResponse:
    """Tests for BaseResponse."""

    def test_response(self, dummy_response: DummyResponse) -> None:
        """Test for BaseResponse."""
        _: BaseResponse = dummy_response

    def test_from_entity(self, dummy_entity: DummyEntity) -> None:
        """Tests for BaseRequest.from_entity()."""
        # Act
        result: BaseResponse = DummyResponse.from_entity(dummy_entity)

        # Assert
        assert isinstance(result, DummyResponse)


@pytest.mark.unit
class TestBaseOutcome:
    """Tests for BaseOutcome."""

    def test_str(self, dummy_outcome: DummyOutcome) -> None:
        """Tests for BaseOutcome.__str__()."""
        # Arrange
        outcome: BaseOutcome = dummy_outcome

        # Act
        result: str = str(outcome)

        # Assert
        assert isinstance(result, str)


@pytest.mark.unit
class TestBasePort:
    """Tests for BasePort."""

    def test_port(self, dummy_port: DummyPort) -> None:
        """Test for BasePort."""
        _: BasePort = dummy_port


@pytest.mark.unit
class TestBaseRepository:
    """Tests for BaseRepository."""

    def test_repository(self, dummy_repository: DummyRepository) -> None:
        """Test for BaseRepository."""
        _: BaseRepository = dummy_repository


@pytest.mark.unit
class TestBaseUseCases:
    """Tests for BaseUseCases."""

    def test_register_service(self, dummy_use_case: DummyUseCase) -> None:
        """Test for BaseUseCase.register_service()."""
        # Arrange
        use_case: BaseUseCase = dummy_use_case

        service_name: str = DummyUseCase.optional_service_name
        service: object = DummyUseCase.optional_service

        # Act
        use_case.register_service(service_name, service)

        # Assert
        assert service_name in use_case._optional_services  # noqa: SLF001
        assert use_case._optional_services.get(service_name) is service  # noqa: SLF001

    def test_unregister_service(self, dummy_use_case: DummyUseCase) -> None:
        """Test for BaseUseCase.unregister_service()."""
        # Arrange
        use_case: BaseUseCase = dummy_use_case

        service_name: str = DummyUseCase.optional_service_name
        service: object = DummyUseCase.optional_service

        use_case.register_service(service_name, service)

        # Act
        use_case.unregister_service(service_name)

        # Assert
        assert service_name not in use_case._optional_services  # noqa: SLF001


if __name__ == "__main__":
    pytest.main()
