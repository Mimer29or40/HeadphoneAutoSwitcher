"""Tests for application.repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from test_application.conftest import DummyRepository

if TYPE_CHECKING:
    from application.repository import BaseRepository


@pytest.mark.unit
class TestBaseRepository:
    """Tests for BaseRepository."""

    def test_repository(self) -> None:
        """Test for BaseRepository."""
        _: BaseRepository = DummyRepository([])


# ---------- Project Specific ---------- #


if __name__ == "__main__":
    pytest.main()
