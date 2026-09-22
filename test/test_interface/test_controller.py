"""Tests for interface.controller."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from conftest import make_parametrize

from _ca.interface import ErrorViewModel
from _ca.utils import Result
from interface.view_model import SoundDeviceViewModel

if TYPE_CHECKING:
    from interface.controller import SoundDeviceController


class TestSoundDeviceController:
    """Tests for SoundDeviceController."""

    @pytest.mark.unit
    class TestHandleGetSoundDevices:
        """Tests for SoundDevicePresenter.handle_get_sound_devices()."""

        def test_ok(self, sound_device_controller: SoundDeviceController) -> None:
            """Test for SoundDevicePresenter.handle_get_sound_devices() with an ok result."""
            # Act
            result: Result[list[SoundDeviceViewModel], ErrorViewModel] = (
                sound_device_controller.handle_get_sound_devices()
            )

            # Arrange
            assert Result.is_ok(result)
            assert isinstance(result.value, list)
            assert isinstance(result.value[0], SoundDeviceViewModel)

        @pytest.mark.parametrize(**make_parametrize("sound_devices", []))
        def test_err(self, sound_device_controller: SoundDeviceController) -> None:
            """Test for SoundDevicePresenter.handle_get_sound_devices() with an err result."""
            # Act
            result: Result[list[SoundDeviceViewModel], ErrorViewModel] = (
                sound_device_controller.handle_get_sound_devices()
            )

            # Arrange
            assert Result.is_err(result)
            assert isinstance(result.value, ErrorViewModel)


if __name__ == "__main__":
    pytest.main()
