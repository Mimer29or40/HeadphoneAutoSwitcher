"""Tests for interface.view_model."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from test_interface.conftest import DummyViewModel

if TYPE_CHECKING:
    from interface.view_model import BaseViewModel


@pytest.mark.unit
def test_view_model() -> None:
    """Test for interface.view_model.DummyViewModel."""
    _: BaseViewModel = DummyViewModel("VALUE")


# ---------- Project Specific ---------- #


if __name__ == "__main__":
    pytest.main()
