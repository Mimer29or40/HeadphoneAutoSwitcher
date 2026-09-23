"""Tests for application.use_case."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from conftest import DUMMY_SOUND_DEVICE_PROVIDER_ERROR_MSG
from conftest import make_parametrize

from _ca.utils import Result
from application.dto import GetSoundDevicesRequest
from application.dto import SoundDeviceResponse
from application.use_case import NO_SOUND_DEVICES_FOUND_ERROR_MSG
from application.use_case import GetSoundDevicesUseCase

if TYPE_CHECKING:
    from _ca.domain import ErrorMsg


class TestGetSoundDevicesUseCase:
    """Tests for GetSoundDevicesUseCase."""

    @pytest.mark.unit
    def test_ok(self, get_sound_devices_use_case: GetSoundDevicesUseCase) -> None:
        """Test for GetSoundDevicesUseCase.execute() when the result is ok."""
        # Arrange
        request: GetSoundDevicesRequest = GetSoundDevicesRequest()

        # Act
        result: Result[list[SoundDeviceResponse], ErrorMsg] = get_sound_devices_use_case.execute(request)

        # Assert
        assert Result.is_ok(result)
        assert isinstance(result.value, list)
        assert isinstance(result.value[0], SoundDeviceResponse)

    @pytest.mark.unit
    @pytest.mark.parametrize(**make_parametrize("sound_devices", []))
    def test_no_devices_found(self, get_sound_devices_use_case: GetSoundDevicesUseCase) -> None:
        """Test for GetSoundDevicesUseCase.execute() when no SoundDevices are found."""
        # Arrange
        request: GetSoundDevicesRequest = GetSoundDevicesRequest()

        # Act
        result: Result[list[SoundDeviceResponse], ErrorMsg] = get_sound_devices_use_case.execute(request)

        # Assert
        assert Result.is_err(result)
        assert result.value == NO_SOUND_DEVICES_FOUND_ERROR_MSG

    @pytest.mark.unit
    @pytest.mark.parametrize(**make_parametrize("sound_device_provider_should_raise", True))
    def test_err(self, get_sound_devices_use_case: GetSoundDevicesUseCase) -> None:
        """Test for GetSoundDevicesUseCase.execute() when a SoundDeviceProviderError is raised."""
        # Arrange
        request: GetSoundDevicesRequest = GetSoundDevicesRequest()

        # Act
        result: Result[list[SoundDeviceResponse], ErrorMsg] = get_sound_devices_use_case.execute(request)

        # Assert
        assert Result.is_err(result)
        assert result.value == DUMMY_SOUND_DEVICE_PROVIDER_ERROR_MSG


if __name__ == "__main__":
    pytest.main()
