"""Tests for ca.domain."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING
from typing import Any

import pytest
from conftest import make_parametrize

from ca.domain import BaseError
from ca.domain import ErrorMsg
from ca.domain import ServiceError

if TYPE_CHECKING:
    from uuid import UUID

    from ca.domain import BaseEntity
    from ca.domain import BaseRepository
    from ca.domain import BaseService
    from ca.domain import BaseValue
    from test_ca._dummy import DummyEntity
    from test_ca._dummy import DummyRepository
    from test_ca._dummy import DummyService
    from test_ca._dummy import DummyValue


# ---------- Value ---------- #


class TestBaseValue:
    """Tests for BaseValue."""

    @pytest.mark.unit
    def test_dummy(self, dummy_value: DummyValue) -> None:
        """Dummy test."""
        # Arrange
        _: BaseValue = dummy_value


# ---------- Entity ---------- #


class TestBaseEntity:
    """Tests for BaseEntity."""

    class TestEq:
        """Tests for BaseEntity.__eq__()."""

        @pytest.mark.unit
        def test_equal(self, dummy_value: DummyValue, dummy_entity: DummyEntity) -> None:
            """Test for BaseEntity.__eq__() with equal entities."""
            # Arrange
            x: BaseEntity = replace(dummy_entity)
            y: BaseEntity = replace(dummy_entity, value=dummy_value)

            # Act
            result: bool = x == y

            # Assert
            assert result is True

        @pytest.mark.unit
        def test_not_equal(self, dummy_uuid: UUID, dummy_entity: DummyEntity) -> None:
            """Test for BaseEntity.__eq__() with unequal entities."""
            # Arrange
            x: BaseEntity = replace(dummy_entity)
            y: BaseEntity = replace(dummy_entity, id=dummy_uuid)

            # Act
            result: bool = x == y

            # Assert
            assert result is False

        @pytest.mark.unit
        def test_not_implemented(self, dummy_uuid: UUID, dummy_entity: DummyEntity) -> None:
            """Test for BaseEntity.__eq__() with the wrong type."""
            # Arrange
            x: BaseEntity = replace(dummy_entity)
            y: Any = dummy_uuid

            # Act
            result: bool = x.__eq__(y)

            # Assert
            assert result is NotImplemented

    @pytest.mark.unit
    def test_hash(self, dummy_entity: DummyEntity) -> None:
        """Test for BaseEntity.__hash__()."""
        # Arrange
        entity: BaseEntity = dummy_entity

        expected: int = hash(entity.id)

        # Act
        result: int = hash(entity)

        # Assert
        assert result == expected

    @pytest.mark.unit
    def test_post_init(self, dummy_entity: DummyEntity) -> None:
        """Test for BaseEntity.__post_init__()."""  # TODO(Ryan): Implement
        # Arrange
        _: BaseEntity = dummy_entity


# ---------- Error ---------- #


class TestErrorMsg:
    """Tests for ErrorMsg."""

    @pytest.mark.unit
    def test_dummy(self, dummy_error_message: ErrorMsg) -> None:
        """Dummy test."""
        # Arrange
        _: ErrorMsg = dummy_error_message


class TestBaseError:
    """Tests for BaseError."""

    @pytest.mark.unit
    def test_message(self, dummy_error_message: ErrorMsg) -> None:
        """Test for ServiceError.message."""
        # Arrange
        message: ErrorMsg = dummy_error_message

        # Act
        result: BaseError = ServiceError(message)

        # Assert
        assert result.message == message

    @pytest.mark.unit
    @pytest.mark.parametrize(**make_parametrize("subclass", *BaseError.__subclasses__()))
    def test_subclass(self, dummy_error_message: ErrorMsg, subclass: type[BaseError]) -> None:
        """Test for BaseError subclasses."""
        # Arrange
        message: ErrorMsg = dummy_error_message

        # Act
        result: BaseError = subclass(message)

        # Assert
        assert result.message == message


# ---------- Service ---------- #


class TestBaseService:
    """Tests for BaseService."""

    @pytest.mark.unit
    def test_dummy(self, dummy_service: DummyService) -> None:
        """Dummy test."""
        # Arrange
        _: BaseService = dummy_service


# ---------- Repository ---------- #


class TestBaseRepository:
    """Tests for BaseRepository."""

    @pytest.mark.unit
    def test_dummy(self, dummy_repository: DummyRepository) -> None:
        """Dummy test."""
        # Arrange
        _: BaseRepository = dummy_repository


if __name__ == "__main__":
    pytest.main()
