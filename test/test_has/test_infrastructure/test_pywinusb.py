"""Tests for ca.infrastructure._click."""

from __future__ import annotations

from queue import Queue
from typing import TYPE_CHECKING
from uuid import UUID

import pytest
from pywinusb.hid import HidDevice
from pywinusb.hid import HidDeviceFilter

from has.domain.entity import UsbDevice
from has.domain.value import UsbDevicePacket

if TYPE_CHECKING:
    from _dummy import DummyPyWinUsbListener
    from _dummy import DummyPyWinUsbProvider

    from has.infrastructure._pywinusb import PyWinUsbListener
    from has.infrastructure._pywinusb import PyWinUsbProvider
    from has.infrastructure._pywinusb import RawUsbDevice


def _get_raw_device() -> RawUsbDevice:
    filter: HidDeviceFilter = HidDeviceFilter()
    hid_device: HidDevice
    for hid_device in filter.get_devices():
        raw_device: RawUsbDevice = hid_device
        return raw_device
    pytest.fail("No HidDevices found.")


class TestPyWinUsbProvider:
    """Tests for PyWinUsbProvider."""

    # TODO(Ryan): Standard tests for UsbDeviceProvider

    def test_get_raw_devices(self, dummy_pywinusb_provider: DummyPyWinUsbProvider) -> None:
        """Test for PyWinUsbProvider.get_raw_devices()."""
        # Arrange
        provider: PyWinUsbProvider = dummy_pywinusb_provider

        # Act
        result: list[RawUsbDevice] = provider.get_raw_devices()
        print(result)
        device_classes: list[type] = list({type(r) for r in result})

        # Assert
        assert isinstance(result, list)
        assert device_classes == [HidDevice]

    class TestGetUUID:
        """Tests for PyWinUsbProvider.get_uuid()."""

        def test_uuid(self, dummy_id: UUID, dummy_pywinusb_provider: DummyPyWinUsbProvider) -> None:
            """Test for PyWinUsbProvider.get_uuid() returning a UUID."""
            # Arrange
            provider: PyWinUsbProvider = dummy_pywinusb_provider

            raw_device: RawUsbDevice = _get_raw_device()
            raw_device.device_path = f"\\\\?\\hid#vid_0000&pid_0000&mi_00&col00#0&0000000&0&0000#{{{dummy_id}}}"

            # Act
            result: UUID | None = provider.get_uuid(raw_device)

            # Assert
            assert isinstance(result, UUID)

        def test_none(self, dummy_pywinusb_provider: DummyPyWinUsbProvider) -> None:
            """Test for PyWinUsbProvider.get_uuid() returning None."""
            # Arrange
            provider: PyWinUsbProvider = dummy_pywinusb_provider

            raw_device: RawUsbDevice = _get_raw_device()
            raw_device.device_path = "INVALID PATH"

            # Act
            result: UUID | None = provider.get_uuid(raw_device)

            # Assert
            assert result is None

    def test_create_device(self, dummy_id: UUID, dummy_pywinusb_provider: DummyPyWinUsbProvider) -> None:
        """Test for PyWinUsbProvider.create_device()."""
        # Arrange
        provider: PyWinUsbProvider = dummy_pywinusb_provider

        raw_device: RawUsbDevice = _get_raw_device()
        raw_device.product_name = "Product Name"
        raw_device.product_id = 1001
        raw_device.vendor_name = "Vendor Name"
        raw_device.vendor_id = 100

        # Act
        result: UsbDevice = provider.create_device(dummy_id, raw_device)

        # Assert
        assert isinstance(result, UsbDevice)
        assert result.id == dummy_id
        assert result.product_name == raw_device.product_name
        assert result.product_id == raw_device.product_id
        assert result.vendor_name == raw_device.vendor_name
        assert result.vendor_id == raw_device.vendor_id


class TestPyWinUsbListener:
    """Tests for PyWinUsbListener."""

    # TODO(Ryan): Standard tests for UsbDeviceListener

    class TestHandleData:
        """Tests for PyWinUsbListener.handle_data()."""

        def test_no_queue(
            self,
            unfreeze_monkeypatch: pytest.MonkeyPatch,
            dummy_pywinusb_listener: DummyPyWinUsbListener,
        ) -> None:
            """Test for PyWinUsbListener.handle_data() with no queue."""
            # Arrange
            listener: PyWinUsbListener = dummy_pywinusb_listener
            unfreeze_monkeypatch.setattr(listener, "queue", None)

            data: list[int] = [1, 2, 3, 4]

            # Act
            listener.handle_data(data)

            # Assert
            assert listener.queue is None

        def test_put(
            self,
            unfreeze_monkeypatch: pytest.MonkeyPatch,
            dummy_pywinusb_listener: DummyPyWinUsbListener,
        ) -> None:
            """Test for PyWinUsbListener.handle_data()."""
            # Arrange
            listener: PyWinUsbListener = dummy_pywinusb_listener
            unfreeze_monkeypatch.setattr(listener, "queue", Queue())

            data: list[int] = [1, 2, 3, 4]

            # Act
            listener.handle_data(data)
            result: UsbDevicePacket = listener.queue.get_nowait()

            # Assert
            assert isinstance(result, UsbDevicePacket)
            assert result.data == data

        def test_full(
            self,
            unfreeze_monkeypatch: pytest.MonkeyPatch,
            dummy_pywinusb_listener: DummyPyWinUsbListener,
        ) -> None:
            """Test for PyWinUsbListener.handle_data() when the queue is full."""
            # Arrange
            listener: PyWinUsbListener = dummy_pywinusb_listener
            unfreeze_monkeypatch.setattr(listener, "queue", Queue(1))

            data0: list[int] = [1, 2, 3, 4]
            data1: list[int] = [5, 6, 7, 8]

            # Act
            listener.handle_data(data0)
            listener.handle_data(data1)
            result: UsbDevicePacket = listener.queue.get_nowait()

            # Assert
            assert isinstance(result, UsbDevicePacket)
            assert result.data == data1


if __name__ == "__main__":
    pytest.main()
