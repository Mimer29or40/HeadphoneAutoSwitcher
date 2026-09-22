"""Tests for infrastructure.application."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from application.use_case import GetSoundDevicesUseCase
from interface.controller import SoundDeviceController

if TYPE_CHECKING:
    from infrastructure.application import Application


class TestApplication:
    """Tests for Application."""

    @pytest.mark.unit
    def test_post_init(self, application: Application) -> None:
        """Tests Application.post_init()."""
        # Assert
        assert isinstance(application.get_sound_devices_use_case, GetSoundDevicesUseCase)
        assert isinstance(application.sound_device_controller, SoundDeviceController)


if __name__ == "__main__":
    pytest.main()
