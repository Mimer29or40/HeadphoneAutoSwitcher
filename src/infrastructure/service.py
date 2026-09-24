"""Infrastructure services, as described by Clean Architecture."""

from __future__ import annotations

import contextlib
import logging
import re
import subprocess
import tempfile
from codecs import BOM_UTF16_LE
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from queue import Empty
from queue import Full
from queue import Queue
from subprocess import CompletedProcess
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from typing import override
from uuid import UUID

from pywinusb.hid import HidDevice
from pywinusb.hid import HidDeviceFilter

from _ca.domain import ErrorMsg
from domain.entity import SoundDevice
from domain.entity import UsbDevice
from domain.exception import SoundDeviceProviderError
from domain.exception import UsbDeviceProviderError
from domain.service import SoundDeviceProvider
from domain.service import UsbDeviceListener
from domain.service import UsbDeviceProvider
from domain.value import SoundDeviceType
from domain.value import UsbDevicePacket

if TYPE_CHECKING:
    from logging import Logger


logger: Logger = logging.getLogger("infrastructure.service")


UUID_PATTERN: re.Pattern[str] = re.compile(
    r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
    flags=re.IGNORECASE,
)


def _extract_uuid(value: str) -> UUID | None:  # pragma: no cover
    uuid_match: re.Match[str] | None = UUID_PATTERN.search(value)
    if uuid_match is None:
        logger.debug("Bad registry key: %s", value)
        return None
    uuid: UUID = UUID(uuid_match.group(1))
    return uuid


type SoundDeviceRow = list[str]

SOUND_VOLUME_VIEW_NOT_FOUND_ERROR: ErrorMsg = ErrorMsg("SoundVolumeView: executable not found")
SOUND_VOLUME_VIEW_NON_ZERO_RETURN: ErrorMsg = ErrorMsg("SoundVolumeView: non-zero exit code")

DEFAULT_SOUND_VOLUME_VIEW_PATH: Path = Path("SoundVolumeView.exe")
DEFAULT_SOUND_VOLUME_VIEW_OUTPUT_FILE: Path = Path(tempfile.gettempdir()) / "SoundVolumeView-Output.txt"


# noinspection DuplicatedCode
@dataclass(frozen=True, slots=True)
class SoundVolumeViewProvider(SoundDeviceProvider):
    """SoundDeviceProvider with SoundVolumeView."""

    sound_volume_view_path: Path = DEFAULT_SOUND_VOLUME_VIEW_PATH
    output_file: Path = DEFAULT_SOUND_VOLUME_VIEW_OUTPUT_FILE

    @override
    def find(self, device_id: UUID) -> SoundDevice | None:
        query: list[SoundDeviceRow] = self._query_device_rows()

        row: SoundDeviceRow
        for row in query:
            extracted_id: UUID | None = _extract_uuid(row[self.COLUMN_REGISTRY_KEY])
            if extracted_id == device_id:
                device: SoundDevice = self._create_device(device_id, row)
                return device
        return None

    @override
    def find_all(self) -> list[SoundDevice]:
        query: list[SoundDeviceRow] = self._query_device_rows()

        sound_devices: list[SoundDevice] = []
        row: SoundDeviceRow
        for row in query:
            device_id: UUID | None = _extract_uuid(row[self.COLUMN_REGISTRY_KEY])
            if device_id is None:  # pragma: no cover
                continue

            device: SoundDevice = self._create_device(device_id, row)
            sound_devices.append(device)

        return sound_devices

    def _query(self) -> list[str]:  # pragma: no cover
        try:
            commands: list[str] = [str(self.sound_volume_view_path), "/stab", str(self.output_file)]
            logger.debug("SoundVolumeView.exe: %s", commands)
            result: CompletedProcess[bytes] = subprocess.run(  # noqa: S603
                commands,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.debug("SoundVolumeView.exe exit code: 0x%08X", result.returncode)
            if not self.output_file.is_file():
                raise SoundDeviceProviderError(SOUND_VOLUME_VIEW_NON_ZERO_RETURN) from None

            # If the file is encoded in BOM_UTF16_LE, we remove those bits before decoding
            raw_query: bytes = self.output_file.read_bytes().removeprefix(BOM_UTF16_LE)
            return raw_query.decode("utf-16le").splitlines()
        except OSError:
            raise SoundDeviceProviderError(SOUND_VOLUME_VIEW_NOT_FOUND_ERROR) from None
        finally:
            self.output_file.unlink(missing_ok=True)

    def _query_device_rows(self) -> list[SoundDeviceRow]:  # pragma: no cover
        query: list[str] = self._query()

        device_rows: list[SoundDeviceRow] = []
        line: str
        for line in query[1:]:  # Drop Header Row
            row: SoundDeviceRow = line.split("\t")

            type: str = row[self.COLUMN_TYPE]
            if type != "Device":
                continue

            device_rows.append(row)

        return device_rows

    def _create_device(self, device_id: UUID, row: SoundDeviceRow) -> SoundDevice:  # pragma: no cover
        direction: SoundDeviceType = {
            "Capture": SoundDeviceType.INPUT,
            "Render": SoundDeviceType.OUTPUT,
        }[row[self.COLUMN_DIRECTION]]
        device_name: str = row[self.COLUMN_DEVICE_NAME]
        selected: bool = row[self.COLUMN_DEFAULT] != ""

        device: SoundDevice = SoundDevice(
            type=direction,
            name=device_name,
            selected=selected,
        )
        device.id = device_id
        logger.debug("Loaded SoundDevice: %s", device)
        return device

    COLUMN_NAME: ClassVar[int] = 0
    COLUMN_TYPE: ClassVar[int] = 1
    COLUMN_DIRECTION: ClassVar[int] = 2
    COLUMN_DEVICE_NAME: ClassVar[int] = 3
    COLUMN_DEFAULT: ClassVar[int] = 4
    COLUMN_DEFAULT_MULTIMEDIA: ClassVar[int] = 5
    COLUMN_DEFAULT_COMMUNICATIONS: ClassVar[int] = 6
    COLUMN_DEVICE_STATE: ClassVar[int] = 7
    COLUMN_MUTED: ClassVar[int] = 8
    COLUMN_VOLUME_DB: ClassVar[int] = 9
    COLUMN_VOLUME_PERCENT: ClassVar[int] = 10
    COLUMN_MIN_VOLUME_DB: ClassVar[int] = 11
    COLUMN_MAX_VOLUME_DB: ClassVar[int] = 12
    COLUMN_VOLUME_STEP: ClassVar[int] = 13
    COLUMN_CHANNELS_COUNT: ClassVar[int] = 14
    COLUMN_CHANNELS_DB: ClassVar[int] = 15
    COLUMN_CHANNELS_PERCENT: ClassVar[int] = 16
    COLUMN_ITEM_ID: ClassVar[int] = 17
    COLUMN_COMMAND_LINE_FRIENDLY_ID: ClassVar[int] = 18
    COLUMN_PROCESS_PATH: ClassVar[int] = 19
    COLUMN_PROCESS_ID: ClassVar[int] = 20
    COLUMN_WINDOW_TITLE: ClassVar[int] = 21
    COLUMN_REGISTRY_KEY: ClassVar[int] = 22
    COLUMN_SPEAKERS_CONFIG: ClassVar[int] = 23
    COLUMN_DEFAULT_FORMAT: ClassVar[int] = 24
    COLUMN_LAST: ClassVar[int] = COLUMN_DEFAULT_FORMAT


type UsbDeviceRow = dict[str, Any]

PY_WIN_USB_ERROR: ErrorMsg = ErrorMsg("pywinusb: error")


# noinspection DuplicatedCode
@dataclass(frozen=True, slots=True)
class PyWinUsbProvider(UsbDeviceProvider):
    """UsbDeviceProvider with pywinusb."""

    @override
    def find(self, device_id: UUID) -> UsbDevice | None:
        query: list[UsbDeviceRow] = self._query_device_rows()

        row: UsbDeviceRow
        for row in query:
            extracted_id: UUID | None = _extract_uuid(row[self.COLUMN_DEVICE_PATH])
            if extracted_id == device_id:
                device: UsbDevice = self._create_device(device_id, row)
                return device
        return None

    @override
    def find_all(self) -> list[UsbDevice]:
        query: list[UsbDeviceRow] = self._query_device_rows()

        sound_devices: list[UsbDevice] = []
        row: UsbDeviceRow
        for row in query:
            device_id: UUID | None = _extract_uuid(row[self.COLUMN_DEVICE_PATH])
            if device_id is None:  # pragma: no cover
                continue

            device: UsbDevice = self._create_device(device_id, row)
            sound_devices.append(device)

        return sound_devices

    @staticmethod
    def _query_device_rows() -> list[UsbDeviceRow]:  # pragma: no cover
        device_rows: list[UsbDeviceRow] = []
        filter: HidDeviceFilter = HidDeviceFilter()
        hid_device: HidDevice
        for hid_device in filter.get_devices():
            row: UsbDeviceRow = vars(hid_device)

            device_rows.append(row)
        return device_rows

    def _create_device(self, device_id: UUID, row: UsbDeviceRow) -> UsbDevice:  # pragma: no cover
        serial_number: str = row[self.COLUMN_SERIAL_NUMBER]
        vendor_name: str = row[self.COLUMN_VENDOR_NAME]
        vendor_id: int = row[self.COLUMN_VENDOR_ID]
        product_name: str = row[self.COLUMN_PRODUCT_NAME]
        product_id: int = row[self.COLUMN_PRODUCT_ID]
        version_number: int = row[self.COLUMN_VERSION_NUMBER]

        device: UsbDevice = UsbDevice(
            serial_number=serial_number,
            vendor_name=vendor_name,
            vendor_id=vendor_id,
            product_name=product_name,
            product_id=product_id,
            version_number=version_number,
        )
        device.id = device_id
        logger.debug("Loaded UsbDevice: %s", device)
        return device

    COLUMN_DEVICE_PATH: ClassVar[str] = "device_path"
    COLUMN_HID_CAPS: ClassVar[str] = "hid_caps"
    COLUMN_HID_HANDLE: ClassVar[str] = "hid_handle"
    COLUMN_INSTANCE_ID: ClassVar[str] = "instance_id"
    COLUMN_PARENT_INSTANCE_ID: ClassVar[str] = "parent_instance_id"
    COLUMN_PRODUCT_ID: ClassVar[str] = "product_id"
    COLUMN_PRODUCT_NAME: ClassVar[str] = "product_name"
    COLUMN_PTR_PREPARSED_DATA: ClassVar[str] = "ptr_preparsed_data"
    COLUMN_REPORT_SET: ClassVar[str] = "report_set"
    COLUMN_SERIAL_NUMBER: ClassVar[str] = "serial_number"
    COLUMN_USAGES_STORAGE: ClassVar[str] = "usages_storage"
    COLUMN_VENDOR_ID: ClassVar[str] = "vendor_id"
    COLUMN_VENDOR_NAME: ClassVar[str] = "vendor_name"
    COLUMN_VERSION_NUMBER: ClassVar[str] = "version_number"


@dataclass(frozen=True, slots=True)
class PyWinUsbListener(UsbDeviceListener):
    """Service to listen to UsbDevices for communication packets."""

    max_queue_size: int = 100

    _devices: list[HidDevice] = field(default_factory=list, init=False)
    _queue: Queue[UsbDevicePacket] = field(init=False)

    @override
    def start(self, vendor_id: int, product_id: int) -> None:
        """Start listening to UsbDevices."""
        logger.info("Loading UsbDevices: vendor_id=%04X product_id=%04X", vendor_id, product_id)

        self._create_queue()

        filter: HidDeviceFilter = HidDeviceFilter(vendor_id=vendor_id, product_id=product_id)
        device: HidDevice
        for device in filter.get_devices():
            logger.debug("Found UsbDevice: %s[%s]", device.product_name, device.instance_id)
            try:
                device.open()
                device.set_raw_data_handler(self._data_handler_)
                self._devices.append(device)
            except Exception as e:  # noqa: BLE001
                logger.warning("Unable to open device: %s", device.product_name, exc_info=e)

    @override
    def stop(self) -> None:
        """Stop listening to UsbDevices."""
        device: HidDevice
        for device in self._devices:
            with contextlib.suppress(BaseException):
                device.close()
        self._devices.clear()

        self._queue.shutdown()
        object.__delattr__(self, "_queue")

    @override
    def get_packet(self, block: bool = True, timeout: float | None = None) -> UsbDevicePacket:
        """Get a packet from the Listener."""
        return self._queue.get(block=block, timeout=timeout)

    def _create_queue(self) -> None:
        queue: Queue[UsbDevicePacket] = Queue(maxsize=self.max_queue_size)
        object.__setattr__(self, "_queue", queue)

    def _data_handler_(self, data: list[int]) -> None:
        """Data handler function called on device listener threads."""
        packet: UsbDevicePacket = UsbDevicePacket(data)
        try:
            self._queue.put_nowait(packet)
        except Full:
            with contextlib.suppress(Empty):
                self._queue.get_nowait()
            self._queue.put_nowait(packet)
