"""Tests for domain.service."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from uuid import UUID

    from domain.entity import SoundDevice
    from domain.entity import UsbDevice
    from domain.service import SoundDeviceProvider
    from domain.service import UsbDeviceProvider


class TestSoundDeviceProvider:
    """Tests for SoundDeviceProvider."""

    @pytest.mark.unit
    class TestFind:
        """Tests for SoundDeviceProvider.find()."""

        def test_found(self, sound_devices: list[SoundDevice], dummy_sound_device_provider: SoundDeviceProvider) -> None:
            """Test for SoundDeviceProvider.find() when a SoundDevice is found."""
            # Arrange
            expected: SoundDevice = sound_devices[0]
            device_id: UUID = expected.id

            # Act
            result: SoundDevice | None = dummy_sound_device_provider.find(device_id)

            # Assert
            assert result == expected

        def test_not_found(self, sound_device: SoundDevice, dummy_sound_device_provider: SoundDeviceProvider) -> None:
            """Test for SoundDeviceProvider.find() when a SoundDevice is not found."""
            # Arrange
            device_id: UUID = sound_device.id

            # Act
            result: SoundDevice | None = dummy_sound_device_provider.find(device_id)

            # Assert
            assert result is None

    @pytest.mark.unit
    def test_find_all(self, sound_devices: list[SoundDevice], dummy_sound_device_provider: SoundDeviceProvider) -> None:
        """Test for SoundDeviceProvider.find_all()."""
        # Act
        result: list[SoundDevice] = dummy_sound_device_provider.find_all()

        # Assert
        assert result == sound_devices


class TestUsbDeviceProvider:
    """Tests for UsbDeviceProvider."""

    @pytest.mark.unit
    class TestFind:
        """Tests for UsbDeviceProvider.find()."""

        def test_found(self, usb_devices: list[UsbDevice], dummy_usb_device_provider: UsbDeviceProvider) -> None:
            """Test for UsbDeviceProvider.find() when a UsbDevice is found."""
            # Arrange
            expected: UsbDevice = usb_devices[0]
            device_id: UUID = expected.id

            # Act
            result: UsbDevice | None = dummy_usb_device_provider.find(device_id)

            # Assert
            assert result == expected

        def test_not_found(self, usb_device: UsbDevice, dummy_usb_device_provider: UsbDeviceProvider) -> None:
            """Test for UsbDeviceProvider.find() when a UsbDevice is not found."""
            # Arrange
            device_id: UUID = usb_device.id

            # Act
            result: UsbDevice | None = dummy_usb_device_provider.find(device_id)

            # Assert
            assert result is None

    @pytest.mark.unit
    def test_find_all(self, usb_devices: list[UsbDevice], dummy_usb_device_provider: UsbDeviceProvider) -> None:
        """Test for UsbDeviceProvider.find_all()."""
        # Act
        result: list[UsbDevice] = dummy_usb_device_provider.find_all()

        # Assert
        assert result == usb_devices


if __name__ == "__main__":
    pytest.main()
