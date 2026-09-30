"""Headphone Auto Switcher pywinusb implementation."""

from __future__ import annotations

import contextlib
import logging
import tempfile
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from queue import Empty
from queue import Full
from queue import Queue
from typing import TYPE_CHECKING
from typing import override

from pywinusb.hid.core import HidDeviceFilter

from ca.domain import ErrorMsg
from ca.utils import log_call
from has.domain.entity import UsbDevice
from has.domain.service import UsbDevicePacketListener
from has.domain.service import UsbDeviceProvider
from has.domain.value import UsbDevicePacket
from has.utils import extract_uuid

if TYPE_CHECKING:
    from logging import Logger
    from uuid import UUID

    from pywinusb.hid import HidDevice

# type RawUsbDevice = dict[str, Any]
type RawUsbDevice = HidDevice

logger: Logger = logging.getLogger("has.infrastructure._py_win_usb")

PY_WIN_USB_ERROR: ErrorMsg = ErrorMsg("pywinusb: error.")

SOUND_VOLUME_VIEW_EXECUTABLE_PATH: Path = Path("UsbVolumeView.exe")
SOUND_VOLUME_VIEW_OUTPUT_FILE_PATH: Path = Path(tempfile.gettempdir()) / "UsbVolumeView-Output.txt"


# TODO(Ryan): UUIDs are all the same?
@dataclass(frozen=True, slots=True)
class PyWinUsbProvider(UsbDeviceProvider):
    """UsbDeviceProvider using UsbVolumeView."""

    @override
    @log_call(type="method")
    def get_raw_devices(self) -> list[RawUsbDevice]:
        raw_devices: list[RawUsbDevice] = []

        filter: HidDeviceFilter = HidDeviceFilter()
        hid_device: HidDevice
        for hid_device in filter.get_devices():
            raw_device: RawUsbDevice = hid_device
            raw_devices.append(raw_device)
        return raw_devices

    @override
    @log_call(type="method")
    def get_uuid(self, raw_device: RawUsbDevice) -> UUID | None:
        device_path: str = raw_device.device_path  # TODO(Ryan): Use instance_id instead for UUID
        uuid: UUID | None = extract_uuid(device_path)
        if uuid is None:
            logger.debug("Bad Device Path: '%s'", device_path)
        return uuid

    @override
    @log_call(type="method")
    def create_device(self, device_id: UUID, raw_device: RawUsbDevice) -> UsbDevice:
        device_product_name: str = raw_device.product_name
        device_product_id: int = raw_device.product_id
        device_vendor_name: str = raw_device.vendor_name
        device_vendor_id: int = raw_device.vendor_id

        device: UsbDevice = UsbDevice(
            id=device_id,
            product_name=device_product_name,
            product_id=device_product_id,
            vendor_name=device_vendor_name,
            vendor_id=device_vendor_id,
        )
        return device


@dataclass(frozen=True, slots=True)
class PyWinUsbListener(UsbDevicePacketListener):
    """UsbDevicePacketListener using UsbVolumeView."""

    max_queue: int = 100
    devices: list[HidDevice] = field(default_factory=list, init=False)
    queue: Queue[UsbDevicePacket] | None = field(default=None, init=False)

    @override
    @log_call(type="method")
    def start(self, vendor_id: int, product_id: int) -> None:
        object.__setattr__(self, "queue", Queue(self.max_queue))

        filter: HidDeviceFilter = HidDeviceFilter(vendor_id=vendor_id, product_id=product_id)
        device: HidDevice
        for device in filter.get_devices():
            logger.info("Loading: %s[%s]", device.product_name, device.instance_id)
            try:
                device.open()
                device.set_raw_data_handler(self._data_handler_)
                self.devices.append(device)
            except Exception as e:  # noqa: BLE001
                logger.warning("Unable to open device: %s", device.product_name, exc_info=e)

    @override
    @log_call(type="method")
    def stop(self) -> None:
        device: HidDevice
        for device in self.devices:
            with contextlib.suppress(BaseException):
                device.close()
        self.devices.clear()

        if self.queue is not None:
            self.queue.shutdown()
            object.__setattr__(self, "queue", None)

    @override
    def get(self, block: bool = True, timeout: float | None = None) -> UsbDevicePacket | None:
        if self.queue is not None:
            return self.queue.get(block=block, timeout=timeout)
        return None

    def _data_handler_(self, data: list[int]) -> None:
        """Data handler function called on device listener threads."""
        if self.queue is None:
            return

        packet: UsbDevicePacket = UsbDevicePacket(data)
        try:
            self.queue.put_nowait(packet)
        except Full:
            with contextlib.suppress(Empty):
                self.queue.get_nowait()
            self.queue.put_nowait(packet)
