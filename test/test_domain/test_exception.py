"""Tests for domain.exception."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from _ca.domain import ErrorMsg
from domain.exception import SoundDeviceProviderError
from domain.exception import UsbDeviceProviderError

if TYPE_CHECKING:
    pass


@pytest.mark.unit
class TestSoundDeviceProviderError:
    """Tests for SoundDeviceProviderError."""

    def test_dummy(self) -> None:
        """Dummy test."""
        _: SoundDeviceProviderError = SoundDeviceProviderError(ErrorMsg("DUMMY"))


@pytest.mark.unit
class TestUsbDeviceProviderError:
    """Tests for UsbDeviceProviderError."""

    def test_dummy(self) -> None:
        """Dummy test."""
        _: UsbDeviceProviderError = UsbDeviceProviderError(ErrorMsg("DUMMY"))


if __name__ == "__main__":
    pytest.main()
