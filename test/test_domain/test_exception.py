"""Tests for domain.exception."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from _ca.domain import ErrorMsg
from domain.exception import SoundDeviceProviderError

if TYPE_CHECKING:
    pass


@pytest.mark.unit
class TestSoundDeviceProviderError:
    """Tests for SoundDeviceProviderError."""

    def test_dummy(self) -> None:
        """Dummy test."""
        _: SoundDeviceProviderError = SoundDeviceProviderError(ErrorMsg("DUMMY"))


if __name__ == "__main__":
    pytest.main()
