"""Tests for infrastructure.service."""

from __future__ import annotations

from pathlib import Path
from subprocess import CompletedProcess
from typing import TYPE_CHECKING
from typing import Any

import pytest
from conftest import make_parametrize

from domain.entity import SoundDevice
from domain.exception import SoundDeviceProviderError
from infrastructure.service import SOUND_VOLUME_VIEW_NON_ZERO_RETURN
from infrastructure.service import SOUND_VOLUME_VIEW_NOT_FOUND_ERROR
from infrastructure.service import SoundVolumeView

if TYPE_CHECKING:
    from uuid import UUID


class TestSoundVolumeView:
    """Tests for SoundVolumeView."""

    @pytest.fixture
    def sound_volume_view_path(self, project_root_path: Path) -> Path:
        """SoundVolumeView path fixture."""
        return project_root_path / "SoundVolumeView.exe"

    @pytest.fixture
    def sound_device_provider(self, sound_volume_view_path: Path) -> SoundVolumeView:
        """SoundVolumeView fixture."""
        return SoundVolumeView(sound_volume_view_path=sound_volume_view_path)

    @pytest.fixture
    def substitute_query(
        self,
        unfreeze_monkeypatch: pytest.MonkeyPatch,
        sound_devices: list[SoundDevice],
        sound_device_provider: SoundVolumeView,
    ) -> None:
        """Substitute SoundVolumeView._query() to provide a test devices."""
        lines: list[str] = [
            (
                "Name	Type	Direction	Device Name	Default	Default Multimedia	Default Communications	"
                "Device State	Muted	Volume dB	Volume Percent	Min Volume dB	Max Volume dB	"
                "Volume Step	Channels Count	Channels dB	Channels  Percent	Item ID	Command-Line Friendly ID	"
                "Process Path	Process ID	Window Title	Registry Key	Speakers Config	Default Format	"
            ),
        ]
        device: SoundDevice
        for device in sound_devices:
            line: list[str] = [""] * (SoundVolumeView.COLUMN_LAST + 1)

            line[SoundVolumeView.COLUMN_TYPE] = "Device"
            line[SoundVolumeView.COLUMN_DIRECTION] = device.type
            line[SoundVolumeView.COLUMN_DEVICE_NAME] = device.name
            line[SoundVolumeView.COLUMN_DEFAULT] = device.default
            line[SoundVolumeView.COLUMN_REGISTRY_KEY] = str(device.id)

            lines.append("\t".join(line))

        def _query() -> list[str]:
            return lines

        unfreeze_monkeypatch.setattr(sound_device_provider, "_query", _query)

    @pytest.mark.unit
    class TestErrors:
        """Tests for SoundVolumeView when it raises an SoundDeviceProviderError."""

        @pytest.mark.parametrize(**make_parametrize("sound_volume_view_path", Path("PATH/TO/EXECUTABLE.EXE")))
        def test_executable_not_found(self, sound_device_provider: SoundVolumeView) -> None:
            """Test to verify raising when the executable is not found."""
            # Assert
            with pytest.raises(SoundDeviceProviderError) as exc_info:
                sound_device_provider.find_all()

            assert isinstance(exc_info.value, SoundDeviceProviderError)
            assert exc_info.value.message == SOUND_VOLUME_VIEW_NOT_FOUND_ERROR

        def test_non_zero_exit_code(
            self,
            monkeypatch: pytest.MonkeyPatch,
            sound_device_provider: SoundVolumeView,
        ) -> None:
            """Test to verify raising when the executable is not found."""
            # Arrange

            def run(*_: Any, **__: Any) -> CompletedProcess[bytes]:
                return CompletedProcess([], 1, None, None)

            monkeypatch.setattr("subprocess.run", run)

            # Assert
            with pytest.raises(SoundDeviceProviderError) as exc_info:
                sound_device_provider.find_all()

            assert isinstance(exc_info.value, SoundDeviceProviderError)
            assert exc_info.value.message == SOUND_VOLUME_VIEW_NON_ZERO_RETURN

    @pytest.mark.unit
    @pytest.mark.usefixtures("substitute_query")
    class TestFind:
        """Tests for SoundVolumeView.find()."""

        def test_found(self, sound_devices: list[SoundDevice], sound_device_provider: SoundVolumeView) -> None:
            """Test for SoundVolumeView.find() when a SoundDevice is found."""
            # Arrange
            expected: SoundDevice = sound_devices[0]
            device_id: UUID = expected.id

            # Act
            result: SoundDevice | None = sound_device_provider.find(device_id)

            # Assert
            assert result == expected

        def test_not_found(self, sound_device_provider: SoundVolumeView) -> None:
            """Test for SoundVolumeView.find() when a SoundDevice is not found."""
            # Arrange
            expected: SoundDevice = SoundDevice(type="type", name="name", default="default")
            device_id: UUID = expected.id

            # Act
            result: SoundDevice | None = sound_device_provider.find(device_id)

            # Assert
            assert result is None

    @pytest.mark.unit
    @pytest.mark.usefixtures("substitute_query")
    def test_find_all(self, sound_devices: list[SoundDevice], sound_device_provider: SoundVolumeView) -> None:
        """Test for SoundVolumeView.find_all()."""
        # Act
        result: list[SoundDevice] = sound_device_provider.find_all()

        # Assert
        assert result == sound_devices


if __name__ == "__main__":
    pytest.main()
