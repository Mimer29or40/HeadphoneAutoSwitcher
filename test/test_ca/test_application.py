"""Tests for ca.application."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

import pytest

from test_ca._dummy import DummyEntityResponse

if TYPE_CHECKING:
    from ca.application import BaseApplication
    from ca.application import BaseApplicationFactory
    from ca.application import BasePort
    from ca.application import BaseRequest
    from ca.application import BaseRequestDict
    from ca.application import BaseResponse
    from ca.application import BaseUseCase
    from test_ca._dummy import DummyApplication
    from test_ca._dummy import DummyApplicationFactory
    from test_ca._dummy import DummyEntity
    from test_ca._dummy import DummyPort
    from test_ca._dummy import DummyRequest
    from test_ca._dummy import DummyRequestDict
    from test_ca._dummy import DummyUseCase


# ---------- Application ---------- #


class TestBaseApplication:
    """Tests for BaseApplication."""

    @pytest.mark.unit
    def test_dummy(self, dummy_application: DummyApplication) -> None:
        """Dummy test."""
        _: BaseApplication = dummy_application

    @pytest.mark.unit
    def test_post_init(self, dummy_application: DummyApplication) -> None:
        """Test for BaseApplication.__post_init__()."""  # TODO(Ryan): Implement
        # Arrange
        _: BaseApplication = dummy_application


class TestBaseApplicationFactory:
    """Tests for BaseApplicationFactory."""

    @pytest.mark.unit
    def test_name(self, dummy_application_factory: DummyApplicationFactory) -> None:
        """Test for BaseApplicationFactory.name."""
        # Arrange
        application_factory: BaseApplicationFactory = dummy_application_factory

        # Act
        result: str = application_factory.name

        # Arrange
        assert isinstance(result, str)

    @pytest.mark.unit
    def test_description(self, dummy_application_factory: DummyApplicationFactory) -> None:
        """Test for BaseApplicationFactory.description."""
        # Arrange
        application_factory: BaseApplicationFactory = dummy_application_factory

        # Act
        result: str = application_factory.description

        # Arrange
        assert isinstance(result, str)

    @pytest.mark.unit
    def test_version(self, dummy_application_factory: DummyApplicationFactory) -> None:
        """Test for BaseApplicationFactory.version."""
        # Arrange
        application_factory: BaseApplicationFactory = dummy_application_factory

        # Act
        result: str = application_factory.version

        # Arrange
        assert isinstance(result, str)

    @pytest.mark.unit
    def test_create(self, dummy_application_factory: DummyApplicationFactory) -> None:
        """Test for BaseApplicationFactory.create."""  # TODO(Ryan): Implement
        # Arrange
        _: BaseApplicationFactory = dummy_application_factory


# ---------- Data Transfer Object (DTO) ---------- #


class TestBaseRequestDict:
    """Tests for BaseRequestDict."""

    @pytest.mark.unit
    def test_dummy(self, dummy_request_dict: DummyRequestDict) -> None:
        """Dummy test."""
        # Arrange
        _: BaseRequestDict = dummy_request_dict


class TestBaseRequest:
    """Tests for BaseRequest."""

    @pytest.mark.unit
    def test_post_init(self, dummy_request: DummyRequest) -> None:
        """Test for BaseResponse.__post_init__()."""  # TODO(Ryan): Implement
        # Arrange
        _: BaseRequest = dummy_request

    @pytest.mark.unit
    def test_convert(self, dummy_request: DummyRequest) -> None:
        """Test for BaseResponse.convert()."""  # TODO(Ryan): Implement
        # Arrange
        _: BaseRequest = dummy_request


class TestBaseResponse:
    """Tests for BaseResponse."""

    @classmethod
    @pytest.mark.unit
    def test_from_entity(cls, dummy_entity: DummyEntity) -> None:
        """Test for BaseResponse.from_entity()."""
        # Act
        result: BaseResponse = DummyEntityResponse.from_entity(dummy_entity)

        # Assert
        assert result == DummyEntityResponse(value=str(dummy_entity.value.obj))

    @classmethod
    @pytest.mark.unit
    def test_from_entities(cls, dummy_entities: list[DummyEntity]) -> None:
        """Test for BaseResponse.from_entities()."""
        # Act
        result: list[DummyEntityResponse] = DummyEntityResponse.from_entities(dummy_entities)

        # Assert
        assert isinstance(result, list)
        assert result == [DummyEntityResponse(value=str(e.value.obj)) for e in dummy_entities]


# ---------- Port ---------- #


class TestBasePort:
    """Tests for BasePort."""

    @pytest.mark.unit
    def test_dummy(self, dummy_port: DummyPort) -> None:
        """Dummy test."""
        # Arrange
        _: BasePort = dummy_port


# ---------- Use Case ---------- #


class TestBaseUseCase:
    """Tests for BaseUseCase."""

    @pytest.mark.unit
    def test_dummy(self, dummy_use_case: DummyUseCase) -> None:
        """Dummy test."""
        # Arrange
        _: BaseUseCase = dummy_use_case

    @pytest.mark.unit
    def test_register(self, dummy_use_case: DummyUseCase) -> None:
        """Test for BaseUseCase.register() when successful."""
        # Arrange
        use_case: BaseUseCase = dummy_use_case

        extension_name: str = "extension"
        extension: Any = object()

        # Act
        use_case.register(extension_name, extension)

        # Assert
        assert extension_name in use_case.optional
        assert use_case.optional.get(extension_name) is extension

    @pytest.mark.unit
    def test_unregister(self, dummy_use_case: DummyUseCase) -> None:
        """Test for BaseUseCase.unregister() when successful."""
        # Arrange
        use_case: BaseUseCase = dummy_use_case

        extension_name: str = "extension"
        extension: Any = object()
        use_case.optional[extension_name] = extension

        # Act
        use_case.unregister(extension_name)

        # Assert
        assert extension_name not in use_case.optional

    @pytest.mark.unit
    def test_execute(self, dummy_use_case: DummyUseCase) -> None:
        """Test for BaseRequest.execute()."""  # TODO(Ryan): Implement
        # Arrange
        _: BaseUseCase = dummy_use_case


if __name__ == "__main__":
    pytest.main()
