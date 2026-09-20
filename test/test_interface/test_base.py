"""Tests for interface.base."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    pass


@pytest.mark.unit
def test_base() -> None:
    """Test for interface.base."""
    import interface.base  # noqa: F401


# ---------- Project Specific ---------- #


if __name__ == "__main__":
    pytest.main()
