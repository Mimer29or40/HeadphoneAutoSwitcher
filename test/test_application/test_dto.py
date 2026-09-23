"""Tests for application.dto."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

import pytest

from application.dto import GetSoundDevicesRequest
from application.dto import SoundDeviceResponse

if TYPE_CHECKING:
    from _ca.application import BaseRequest
    from domain.entity import SoundDevice


class TestGetSoundDevicesRequest:
    """Tests for GetSoundDevicesRequest."""

    @pytest.mark.unit
    def test_post_init(self) -> None:
        """Test for GetSoundDevicesRequest.__post_init__()."""
        _: BaseRequest = GetSoundDevicesRequest()
        # No test. This request will never throw a ValueError

    @pytest.mark.unit
    def test_convert(self, get_sound_devices_request: GetSoundDevicesRequest) -> None:
        """Test for GetSoundDevicesRequest.convert()."""
        # Arrange
        request: BaseRequest = get_sound_devices_request

        # Act
        result: dict[str, Any] = request.convert()

        # Assert
        assert result == {}


class TestSoundDeviceResponse:
    """Tests for SoundDeviceResponse."""

    @pytest.mark.unit
    def test_from_entity(self, sound_device: SoundDevice) -> None:
        """Test for SoundDeviceResponse.from_entity()."""
        # Act
        response: SoundDeviceResponse = SoundDeviceResponse.from_entity(sound_device)

        # Assert
        assert response.type == sound_device.type.name.lower()
        assert response.name == sound_device.name
        assert response.selected == "Selected" if sound_device.selected else "Not Selected"


if __name__ == "__main__":
    pytest.main()
