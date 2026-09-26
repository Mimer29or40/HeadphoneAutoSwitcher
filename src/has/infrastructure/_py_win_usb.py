"""Headphone Auto Switcher pywinusb UsbDeviceProvider implementation."""

from __future__ import annotations

import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import override

from pywinusb.hid.core import HidDeviceFilter

from ca.domain import ErrorMsg
from ca.utils import log_call
from has.domain.entity import UsbDevice
from has.domain.service import UsbDeviceProvider
from has.utils import extract_uuid

if TYPE_CHECKING:
    from logging import Logger
    from uuid import UUID

    from pywinusb.hid import HidDevice

type RawUsbDevice = dict[str, Any]

logger: Logger = logging.getLogger("has.infrastructure._py_win_usb")

PY_WIN_USB_ERROR: ErrorMsg = ErrorMsg("pywinusb: error.")

SOUND_VOLUME_VIEW_EXECUTABLE_PATH: Path = Path("UsbVolumeView.exe")
SOUND_VOLUME_VIEW_OUTPUT_FILE_PATH: Path = Path(tempfile.gettempdir()) / "UsbVolumeView-Output.txt"


# TODO(Ryan): UUIDs are all the same?
@dataclass(frozen=True, slots=True)
class PyWinUsb(UsbDeviceProvider):
    """UsbDeviceProvider using UsbVolumeView."""

    @override
    @log_call(type="method")
    def get_raw_devices(self) -> list[RawUsbDevice]:
        raw_devices: list[RawUsbDevice] = []

        filter: HidDeviceFilter = HidDeviceFilter()
        hid_device: HidDevice
        for hid_device in filter.get_devices():
            raw_device: RawUsbDevice = vars(hid_device)
            raw_devices.append(raw_device)
        return raw_devices

    @override
    def get_uuid(self, raw_device: RawUsbDevice) -> UUID | None:
        device_path: str = raw_device[COLUMN_DEVICE_PATH]
        uuid: UUID | None = extract_uuid(device_path)
        if uuid is None:
            logger.debug("Bad Device Path: '%s'", device_path)
        return uuid

    @override
    def create_device(self, device_id: UUID, raw_device: RawUsbDevice) -> UsbDevice:
        device_product_name: str = raw_device[COLUMN_PRODUCT_NAME]
        device_product_id: int = raw_device[COLUMN_PRODUCT_ID]
        device_vendor_name: str = raw_device[COLUMN_VENDOR_NAME]
        device_vendor_id: int = raw_device[COLUMN_VENDOR_ID]

        device: UsbDevice = UsbDevice(
            id=device_id,
            product_name=device_product_name,
            product_id=device_product_id,
            vendor_name=device_vendor_name,
            vendor_id=device_vendor_id,
        )
        return device


COLUMN_DEVICE_PATH: str = "device_path"
COLUMN_HID_CAPS: str = "hid_caps"
COLUMN_HID_HANDLE: str = "hid_handle"
COLUMN_INSTANCE_ID: str = "instance_id"
COLUMN_PARENT_INSTANCE_ID: str = "parent_instance_id"
COLUMN_PRODUCT_ID: str = "product_id"
COLUMN_PRODUCT_NAME: str = "product_name"
COLUMN_PTR_PREPARSED_DATA: str = "ptr_preparsed_data"
COLUMN_REPORT_SET: str = "report_set"
COLUMN_SERIAL_NUMBER: str = "serial_number"
COLUMN_USAGES_STORAGE: str = "usages_storage"
COLUMN_VENDOR_ID: str = "vendor_id"
COLUMN_VENDOR_NAME: str = "vendor_name"
COLUMN_VERSION_NUMBER: str = "version_number"

COLUMN_LAST: str = COLUMN_VERSION_NUMBER
