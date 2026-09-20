"""Tests for domain.service."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from test_domain.conftest import DummyService

if TYPE_CHECKING:
    from domain.service import BaseService


@pytest.mark.unit
class TestBaseService:
    """Tests for BaseService."""

    def test_service(self) -> None:
        """Test for BaseService."""
        _: BaseService = DummyService()

    _: BaseService = DummyService()


# ---------- Project Specific ---------- #


if __name__ == "__main__":
    pytest.main()
