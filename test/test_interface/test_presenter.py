"""Tests for interface.presenter."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from interface.view_model import SoundDeviceViewModel
from interface.view_model import UsbDeviceViewModel

if TYPE_CHECKING:
    from application.dto import SoundDeviceResponse
    from application.dto import UsbDeviceResponse
    from interface.presenter import SoundDevicePresenter
    from interface.presenter import UsbDevicePresenter


class TestSoundDevicePresenter:
    """Tests for SoundDevicePresenter."""

    @pytest.mark.unit
    def test_present_sound_device(
        self,
        sound_device_responses: list[SoundDeviceResponse],
        dummy_sound_device_presenter: SoundDevicePresenter,
    ) -> None:
        """Test for SoundDevicePresenter.present_sound_device()."""
        # Arrange
        response: SoundDeviceResponse = sound_device_responses[0]

        # Act
        view_model: SoundDeviceViewModel = dummy_sound_device_presenter.present_sound_device(response)

        # Arrange
        assert isinstance(view_model, SoundDeviceViewModel)

    @pytest.mark.unit
    def test_present_sound_devices(
        self,
        sound_device_responses: list[SoundDeviceResponse],
        dummy_sound_device_presenter: SoundDevicePresenter,
    ) -> None:
        """Test for SoundDevicePresenter.present_sound_devices()."""
        # Act
        view_model: list[SoundDeviceViewModel] = dummy_sound_device_presenter.present_sound_devices(sound_device_responses)

        # Arrange
        assert isinstance(view_model, list)
        assert isinstance(view_model[0], SoundDeviceViewModel)


class TestUsbDevicePresenter:
    """Tests for UsbDevicePresenter."""

    @pytest.mark.unit
    def test_present_usb_device(
        self,
        usb_device_responses: list[UsbDeviceResponse],
        dummy_usb_device_presenter: UsbDevicePresenter,
    ) -> None:
        """Test for UsbDevicePresenter.present_usb_device()."""
        # Arrange
        response: UsbDeviceResponse = usb_device_responses[0]

        # Act
        view_model: UsbDeviceViewModel = dummy_usb_device_presenter.present_usb_device(response)

        # Arrange
        assert isinstance(view_model, UsbDeviceViewModel)

    @pytest.mark.unit
    def test_present_usb_devices(
        self,
        usb_device_responses: list[UsbDeviceResponse],
        dummy_usb_device_presenter: UsbDevicePresenter,
    ) -> None:
        """Test for UsbDevicePresenter.present_usb_devices()."""
        # Act
        view_model: list[UsbDeviceViewModel] = dummy_usb_device_presenter.present_usb_devices(usb_device_responses)

        # Arrange
        assert isinstance(view_model, list)
        assert isinstance(view_model[0], UsbDeviceViewModel)


if __name__ == "__main__":
    pytest.main()
