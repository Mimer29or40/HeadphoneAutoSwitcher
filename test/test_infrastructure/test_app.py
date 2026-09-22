"""Tests for infrastructure.app."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from application.use_case import GetSoundDevicesUseCase
from interface.controller import SoundDeviceController

if TYPE_CHECKING:
    from infrastructure.app import HeadphoneAutoSwitcherApplication


class TestHeadphoneAutoSwitcherApplication:
    """Tests for HeadphoneAutoSwitcherApplication."""

    @pytest.mark.unit
    def test_post_init(self, application: HeadphoneAutoSwitcherApplication) -> None:
        """Tests HeadphoneAutoSwitcherApplication.__post_init__()."""
        # Assert
        assert isinstance(application.get_sound_devices_use_case, GetSoundDevicesUseCase)
        assert isinstance(application.sound_device_controller, SoundDeviceController)


if __name__ == "__main__":
    pytest.main()
