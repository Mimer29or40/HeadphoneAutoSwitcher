"""Tests for interface.presenter."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from interface.view_model import SoundDeviceViewModel

if TYPE_CHECKING:
    from application.dto import SoundDeviceResponse
    from interface.presenter import SoundDevicePresenter


class TestSoundDevicePresenter:
    """Tests for SoundDevicePresenter."""

    @pytest.mark.unit
    def test_present_sound_device(
        self,
        sound_device_responses: list[SoundDeviceResponse],
        sound_device_presenter: SoundDevicePresenter,
    ) -> None:
        """Test for SoundDevicePresenter.present_sound_device()."""
        # Arrange
        response: SoundDeviceResponse = sound_device_responses[0]

        # Act
        view_model: SoundDeviceViewModel = sound_device_presenter.present_sound_device(response)

        # Arrange
        assert isinstance(view_model, SoundDeviceViewModel)

    @pytest.mark.unit
    def test_present_sound_devices(
        self,
        sound_device_responses: list[SoundDeviceResponse],
        sound_device_presenter: SoundDevicePresenter,
    ) -> None:
        """Test for SoundDevicePresenter.present_sound_devices()."""
        # Act
        view_model: list[SoundDeviceViewModel] = sound_device_presenter.present_sound_devices(sound_device_responses)

        # Arrange
        assert isinstance(view_model, list)
        assert isinstance(view_model[0], SoundDeviceViewModel)


if __name__ == "__main__":
    pytest.main()
