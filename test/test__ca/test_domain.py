"""Tests for _ca.domain."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

from test__ca.conftest import DUMMY_ERROR_MSG
from test__ca.conftest import DummyEntity
from test__ca.conftest import DummyError
from test__ca.conftest import DummyService
from test__ca.conftest import DummyValue

if TYPE_CHECKING:
    from typing import Any
    from uuid import UUID

    from _ca.domain import BaseEntity
    from _ca.domain import BaseError
    from _ca.domain import BaseService
    from _ca.domain import BaseValue
    from _ca.domain import ErrorMsg


@pytest.mark.unit
class TestEntity:
    """Tests for Entity."""

    class TestEq:
        """Tests for Entity.__eq__()."""

        def test_equal(self) -> None:
            """Test for Entity.__eq__() with equal objects."""
            # Arrange
            obj1: BaseEntity = DummyEntity(None)
            obj2: Any = DummyEntity(None)
            assert obj1 != obj2

            id: UUID = uuid4()
            obj1.id = id
            obj2.id = id

            # Act
            result: bool = obj1 == obj2

            # Assert
            assert result is True

        def test_not_equal(self) -> None:
            """Test for Entity.__eq__() with unequal objects."""
            # Arrange
            obj1: BaseEntity = DummyEntity(None)
            obj2: Any = DummyEntity(None)
            assert obj1 != obj2

            # Act
            result: bool = obj1 == obj2

            # Assert
            assert result is False

        def test_not_implemented(self) -> None:
            """Test for Entity.__eq__() with a non Entity object."""
            # Arrange
            obj1: BaseEntity = DummyEntity(None)
            obj2: Any = object()

            # Act
            result: bool = obj1 == obj2

            # Assert
            assert result is False

    def test_hash(self) -> None:
        """Test for Entity.__hash__()."""
        # Arrange
        entity: DummyEntity = DummyEntity(None)
        id_hash: int = hash(entity.id)

        # Act
        result: int = hash(entity)

        # Assert
        assert result == id_hash


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


@pytest.mark.unit
class TestBaseService:
    """Tests for BaseService."""

    def test_service(self) -> None:
        """Test for BaseService."""
        _: BaseService = DummyService()


@pytest.mark.unit
class TestBaseValue:
    """Tests for BaseValue."""

    @pytest.fixture
    def value_obj(self) -> BaseValue:
        """BaseValue fixture."""
        return DummyValue("VALUE")

    def test_unmodifiable(self, value_obj: BaseValue) -> None:
        """Test to verify that the value is not editable."""
        # Act/Assert
        with pytest.raises(FrozenInstanceError):
            # noinspection dunder-slots
            value_obj.value = 1  # ty:ignore[invalid-assignment]


if __name__ == "__main__":
    pytest.main()
