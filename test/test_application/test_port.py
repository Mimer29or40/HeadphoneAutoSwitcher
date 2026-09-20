"""Tests for application.port."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from test_application.conftest import DummyPort

if TYPE_CHECKING:
    from application.port import BasePort


@pytest.mark.unit
class TestBasePort:
    """Tests for BasePort."""

    def test_port(self) -> None:
        """Test for BasePort."""
        _: BasePort = DummyPort("VALUE")


# ---------- Project Specific ---------- #


if __name__ == "__main__":
    pytest.main()
