"""Tests for application.dto."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

import pytest

from application.dto import GetSoundDevicesRequest
from application.dto import SoundDeviceResponse
from domain.entity import SoundDevice

if TYPE_CHECKING:
    pass


class TestGetSoundDevicesRequest:
    """Tests for GetSoundDevicesRequest."""

    @pytest.mark.unit
    def test_post_init(self) -> None:
        """Test for GetSoundDevicesRequest.__post_init__()."""
        _: GetSoundDevicesRequest = GetSoundDevicesRequest()
        # No test. This request will never throw a ValueError

    @pytest.mark.unit
    def test_convert(self) -> None:
        """Test for GetSoundDevicesRequest.convert()."""
        # Arrange
        request: GetSoundDevicesRequest = GetSoundDevicesRequest()

        # Act
        result: dict[str, Any] = request.convert()

        # Assert
        assert result == {}


class TestSoundDeviceResponse:
    """Tests for SoundDeviceResponse."""

    @pytest.mark.unit
    def test_from_entity(self) -> None:
        """Test for SoundDeviceResponse.from_entity()."""
        # Arrange
        device: SoundDevice = SoundDevice(type="type", name="name", default="default")

        # Act
        response: SoundDeviceResponse = SoundDeviceResponse.from_entity(device)

        # Assert
        assert response.type == device.type
        assert response.name == device.name
        assert response.default == device.default


if __name__ == "__main__":
    pytest.main()
