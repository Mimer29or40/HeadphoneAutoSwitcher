"""Tests for infrastructure.service."""

from __future__ import annotations

from pathlib import Path
from subprocess import CompletedProcess
from typing import TYPE_CHECKING
from typing import Any

import pytest
from conftest import make_parametrize

from domain.exception import SoundDeviceProviderError
from domain.exception import UsbDeviceProviderError
from domain.value import SoundDeviceType
from infrastructure.service import SOUND_VOLUME_VIEW_NON_ZERO_RETURN
from infrastructure.service import SOUND_VOLUME_VIEW_NOT_FOUND_ERROR
from infrastructure.service import PyWinUsbProvider
from infrastructure.service import SoundDeviceRow
from infrastructure.service import SoundVolumeViewProvider
from infrastructure.service import UsbDeviceRow

if TYPE_CHECKING:
    from uuid import UUID

    from domain.entity import SoundDevice
    from domain.entity import UsbDevice


class TestSoundVolumeView:
    """Tests for SoundVolumeView."""

    @pytest.fixture
    def sound_volume_view_path(self, project_root_path: Path) -> Path:
        """SoundVolumeView path fixture."""
        return project_root_path / "SoundVolumeView.exe"

    @pytest.fixture
    def sound_device_provider(self, sound_volume_view_path: Path) -> SoundVolumeViewProvider:
        """SoundVolumeView fixture."""
        return SoundVolumeViewProvider(sound_volume_view_path=sound_volume_view_path)

    @pytest.fixture
    def substitute_query(
        self,
        unfreeze_monkeypatch: pytest.MonkeyPatch,
        sound_devices: list[SoundDevice],
        sound_device_provider: SoundVolumeViewProvider,
    ) -> None:
        """Substitute SoundVolumeView._query() to provide a test devices."""
        rows: list[SoundDeviceRow] = []
        device: SoundDevice
        for device in sound_devices:
            line: SoundDeviceRow = [""] * (SoundVolumeViewProvider.COLUMN_LAST + 1)

            line[SoundVolumeViewProvider.COLUMN_TYPE] = "Device"
            line[SoundVolumeViewProvider.COLUMN_DIRECTION] = {
                SoundDeviceType.INPUT: "Capture",
                SoundDeviceType.OUTPUT: "Render",
            }[device.type]
            line[SoundVolumeViewProvider.COLUMN_DEVICE_NAME] = device.name
            line[SoundVolumeViewProvider.COLUMN_DEFAULT] = "Default" if device.selected else ""
            line[SoundVolumeViewProvider.COLUMN_REGISTRY_KEY] = str(device.id)

            rows.append(line)

        def _query_device_rows() -> list[SoundDeviceRow]:
            return rows

        unfreeze_monkeypatch.setattr(sound_device_provider, "_query_device_rows", _query_device_rows)

    @pytest.mark.unit
    class TestErrors:
        """Tests for SoundVolumeView when it raises an SoundDeviceProviderError."""

        @pytest.mark.parametrize(**make_parametrize("sound_volume_view_path", Path("PATH/TO/EXECUTABLE.EXE")))
        def test_executable_not_found(self, sound_device_provider: SoundVolumeViewProvider) -> None:
            """Test to verify raising when the executable is not found."""
            # Assert
            with pytest.raises(SoundDeviceProviderError) as exc_info:
                sound_device_provider.find_all()

            assert isinstance(exc_info.value, SoundDeviceProviderError)
            assert exc_info.value.message == SOUND_VOLUME_VIEW_NOT_FOUND_ERROR

        def test_non_zero_exit_code(
            self,
            monkeypatch: pytest.MonkeyPatch,
            sound_device_provider: SoundVolumeViewProvider,
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

        def test_found(self, sound_devices: list[SoundDevice], sound_device_provider: SoundVolumeViewProvider) -> None:
            """Test for SoundVolumeView.find() when a SoundDevice is found."""
            # Arrange
            expected: SoundDevice = sound_devices[0]
            device_id: UUID = expected.id

            # Act
            result: SoundDevice | None = sound_device_provider.find(device_id)

            # Assert
            assert result == expected

        def test_not_found(self, sound_device: SoundDevice, sound_device_provider: SoundVolumeViewProvider) -> None:
            """Test for SoundVolumeView.find() when a SoundDevice is not found."""
            # Arrange
            device_id: UUID = sound_device.id

            # Act
            result: SoundDevice | None = sound_device_provider.find(device_id)

            # Assert
            assert result is None

    @pytest.mark.unit
    @pytest.mark.usefixtures("substitute_query")
    def test_find_all(self, sound_devices: list[SoundDevice], sound_device_provider: SoundVolumeViewProvider) -> None:
        """Test for SoundVolumeView.find_all()."""
        # Act
        result: list[SoundDevice] = sound_device_provider.find_all()

        # Assert
        assert result == sound_devices


class TestPyWinUsb:
    """Tests for PyWinUsb."""

    @pytest.fixture
    def usb_device_provider(self) -> PyWinUsbProvider:
        """PyWinUsb fixture."""
        return PyWinUsbProvider()

    @pytest.fixture
    def substitute_query(
        self,
        unfreeze_monkeypatch: pytest.MonkeyPatch,
        usb_devices: list[UsbDevice],
        usb_device_provider: PyWinUsbProvider,
    ) -> None:
        """Substitute PyWinUsb._query() to provide a test devices."""
        rows: list[UsbDeviceRow] = []
        device: UsbDevice
        for device in usb_devices:
            row: UsbDeviceRow = {
                PyWinUsbProvider.COLUMN_DEVICE_PATH: str(device.id),
                PyWinUsbProvider.COLUMN_SERIAL_NUMBER: device.serial_number,
                PyWinUsbProvider.COLUMN_VENDOR_NAME: device.vendor_name,
                PyWinUsbProvider.COLUMN_VENDOR_ID: device.vendor_id,
                PyWinUsbProvider.COLUMN_PRODUCT_NAME: device.product_name,
                PyWinUsbProvider.COLUMN_PRODUCT_ID: device.product_id,
                PyWinUsbProvider.COLUMN_VERSION_NUMBER: device.version_number,
            }

            rows.append(row)

        def _query_device_rows() -> list[UsbDeviceRow]:
            return rows

        unfreeze_monkeypatch.setattr(usb_device_provider, "_query_device_rows", _query_device_rows)

    @pytest.mark.unit
    class TestErrors:
        """Tests for PyWinUsb when it raises an UsbDeviceProviderError."""

    @pytest.mark.unit
    class TestFind:
        """Tests for PyWinUsb.find()."""

        @pytest.mark.usefixtures("substitute_query")
        def test_found(self, usb_devices: list[UsbDevice], usb_device_provider: PyWinUsbProvider) -> None:
            """Test for PyWinUsb.find() when a UsbDevice is found."""
            # Arrange
            expected: UsbDevice = usb_devices[0]
            device_id: UUID = expected.id

            # Act
            result: UsbDevice | None = usb_device_provider.find(device_id)

            # Assert
            assert result == expected

        def test_not_found(self, usb_device: UsbDevice, usb_device_provider: PyWinUsbProvider) -> None:
            """Test for PyWinUsb.find() when a UsbDevice is not found."""
            # Arrange
            device_id: UUID = usb_device.id

            # Act
            result: UsbDevice | None = usb_device_provider.find(device_id)

            # Assert
            assert result is None

    @pytest.mark.unit
    @pytest.mark.usefixtures("substitute_query")
    def test_find_all(self, usb_devices: list[UsbDevice], usb_device_provider: PyWinUsbProvider) -> None:
        """Test for PyWinUsb.find_all()."""
        # Act
        result: list[UsbDevice] = usb_device_provider.find_all()

        # Assert
        assert result == usb_devices


if __name__ == "__main__":
    pytest.main()
