"""Tests for domain.value."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from domain.entity import SoundDevice

if TYPE_CHECKING:
    pass


@pytest.mark.unit
class TestSoundDevice:
    """Tests for SoundDevice."""

    def test_dummy(self) -> None:
        """Dummy test."""
        _: SoundDevice = SoundDevice(type="type", name="name", default="default")


if __name__ == "__main__":
    pytest.main()
