"""Tests for domain.value."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from domain.value import SoundDeviceType

if TYPE_CHECKING:
    pass


@pytest.mark.unit
class TestSoundDeviceType:
    """Tests for SoundDeviceType."""

    def test_dummy(self) -> None:
        """Dummy test."""
        _: SoundDeviceType = SoundDeviceType.UNKNOWN


if __name__ == "__main__":
    pytest.main()
