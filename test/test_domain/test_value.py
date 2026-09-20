"""Tests for domain.value."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from typing import TYPE_CHECKING

import pytest

from test_domain.conftest import DummyValue

if TYPE_CHECKING:
    from domain.value import BaseValue


@pytest.mark.unit
class TestBaseValue:
    """Tests for BaseValue."""

    @pytest.fixture
    def value_obj(self) -> BaseValue:
        """BaseValue fixture."""
        return DummyValue("VALUE")

    def test_unmodifiable(self, value_obj: BaseValue) -> None:
        """Test to verify that the value is not editable."""
        # Assert
        with pytest.raises(FrozenInstanceError):
            # noinspection dunder-slots
            value_obj.value = 1  # ty:ignore[invalid-assignment]


# ---------- Project Specific ---------- #


if __name__ == "__main__":
    pytest.main()
