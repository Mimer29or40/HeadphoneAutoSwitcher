"""Tests for domain.service."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from domain.entity import SoundDevice

if TYPE_CHECKING:
    from uuid import UUID

    from domain.service import SoundDeviceProvider


class TestSoundDeviceProvider:
    """Tests for SoundDeviceProvider."""

    @pytest.mark.unit
    class TestFind:
        """Tests for SoundDeviceProvider.find()."""

        def test_found(self, sound_devices: list[SoundDevice], sound_volume_view: SoundDeviceProvider) -> None:
            """Test for SoundDeviceProvider.find() when a SoundDevice is found."""
            # Arrange
            expected: SoundDevice = sound_devices[0]
            device_id: UUID = expected.id

            # Act
            result: SoundDevice | None = sound_volume_view.find(device_id)

            # Assert
            assert result == expected

        def test_not_found(self, sound_volume_view: SoundDeviceProvider) -> None:
            """Test for SoundDeviceProvider.find() when a SoundDevice is not found."""
            # Arrange
            expected: SoundDevice = SoundDevice(type="type", name="name", default="default")
            device_id: UUID = expected.id

            # Act
            result: SoundDevice | None = sound_volume_view.find(device_id)

            # Assert
            assert result is None

    @pytest.mark.unit
    def test_find_all(self, sound_devices: list[SoundDevice], sound_volume_view: SoundDeviceProvider) -> None:
        """Test for SoundDeviceProvider.find_all()."""
        # Act
        result: list[SoundDevice] = sound_volume_view.find_all()

        # Assert
        assert result == sound_devices


if __name__ == "__main__":
    pytest.main()
