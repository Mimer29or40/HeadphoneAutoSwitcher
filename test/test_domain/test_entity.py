"""Tests for domain.value."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest

from test_domain.conftest import DummyEntity

if TYPE_CHECKING:
    from domain.entity import BaseEntity


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


# ---------- Project Specific ---------- #


if __name__ == "__main__":
    pytest.main()
