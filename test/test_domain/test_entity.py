"""Tests for domain.value."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from domain.entity import SoundDevice
    from domain.entity import UsbDevice


@pytest.mark.unit
class TestSoundDevice:
    """Tests for SoundDevice."""

    def test_dummy(self, sound_device: SoundDevice) -> None:
        """Dummy test."""
        _: SoundDevice = sound_device


@pytest.mark.unit
class TestUsbDevice:
    """Tests for UsbDevice."""

    def test_dummy(self, usb_device: UsbDevice) -> None:
        """Dummy test."""
        _: UsbDevice = usb_device


if __name__ == "__main__":
    pytest.main()
