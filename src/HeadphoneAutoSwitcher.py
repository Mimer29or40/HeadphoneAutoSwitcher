"""Headphone Auto Switcher.

Config file to define headphone details
Define default device
"""

from __future__ import annotations

import contextlib
import json
import logging
import re
import subprocess
import sys
import time
from codecs import BOM_UTF16_LE
from contextlib import AbstractContextManager
from pathlib import Path
from re import Match
from subprocess import CalledProcessError
from subprocess import CompletedProcess
from threading import Lock
from typing import TYPE_CHECKING
from typing import NamedTuple
from typing import Self
from typing import override

from pywinusb.hid import HidDevice
from pywinusb.hid import HidDeviceFilter
from simpcli import SUCCESS
from simpcli import Manager

if TYPE_CHECKING:  # pragma: no cover
    from logging import Logger
    from types import TracebackType

    from simpcli import Result


class SoundDevice(NamedTuple):  # noqa: D101
    direction: str
    name: str
    default: str


__version__: str = "1.0.0"

logger: Logger = logging.getLogger()

SOUND_VOLUME_VIEW_PATH: Path = Path("SoundVolumeView.exe")
CONFIG_PATH: Path = Path("HeadphoneAutoSwitcher.json")

DEFAULT_CONFIG: dict[str, str] = {
    "Headphone Vendor ID": "",
    "Headphone Product ID": "",
    "Capture Device": "",
    "Render Device": "",
}

HEARTBEAT_PATTERNS: dict[tuple[int, int], str] = {
    (0x1B1C, 0x2A08): r"^1,1,6.*",  # CORSAIR VOID WIRELESS v2 Gaming Headset
}


manager: Manager = Manager(prog=__name__, version=__version__)

CONFIG_ERRORS: str = "CONFIG_ERRORS"
UNSUPPORTED_HEADPHONES: str = "UNSUPPORTED_HEADPHONES"
NO_DEVICES_FOUND: str = "NO_DEVICES_FOUND"
NO_SOUND_VOLUME_VIEW_EXE: Result = "NO_SOUND_VOLUME_VIEW_EXE"
SOUND_VOLUME_VIEW_FAILED: Result = "SOUND_VOLUME_VIEW_FAILED"


@manager.command()
def listen() -> Result:
    """Listen for headphone connection state changes."""
    if not CONFIG_PATH.is_file():
        CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=4))

    config: dict[str, str] = json.loads(CONFIG_PATH.read_text())

    vendor_id: str = config.get("Headphone Vendor ID", "")
    product_id: str = config.get("Headphone Product ID", "")
    capture_device: str = config.get("Capture Device", "")
    render_device: str = config.get("Render Device", "")

    config_errors: list[str] = []
    if vendor_id == "":
        config_errors.append("Headphone Vendor ID is required.")
    if product_id == "":
        config_errors.append("Headphone Product ID is required.")
    if capture_device == "":
        config_errors.append("Capture Device is required.")
    if render_device == "":
        config_errors.append("Render Device is required.")
    if len(config_errors) > 0:
        logger.critical("Config has errors: %s", config_errors)
        return CONFIG_ERRORS

    vendor_id: int = int(vendor_id, 0)
    product_id: int = int(product_id, 0)

    if (vendor_id, product_id) not in HEARTBEAT_PATTERNS:
        logger.critical("Headphone not supported: Vendor (0x%04X) Product (0x%04X)", vendor_id, product_id)
        return UNSUPPORTED_HEADPHONES

    state: State
    with State(vendor_id, product_id, capture_device, render_device) as state:
        if len(state.devices) == 0:
            logger.critical("No devices found.")
            return NO_DEVICES_FOUND

        state.listen()

    return 0


@manager.command()
def sound() -> Result:
    """List all sound devices."""
    if not SOUND_VOLUME_VIEW_PATH.is_file():
        logger.critical("SoundVolumeView.exe not found in current directory.")
        return NO_SOUND_VOLUME_VIEW_EXE

    devices: list[SoundDevice] = get_sound_devices()
    devices = [SoundDevice("Direction", "Name", "Default"), *sorted(set(devices))]

    output_table(devices)

    return SUCCESS


@manager.command()
def usb() -> Result:
    """List all USB devices."""
    devices: list[tuple[str, str, str, str]] = []

    filter: HidDeviceFilter = HidDeviceFilter()
    device: HidDevice
    for device in filter.get_devices():
        vendor: str = f"{device.vendor_name} (0x{device.vendor_id:04X})"
        product: str = f"{device.product_name} (0x{device.product_id:04X})"
        version: str = f"{device.version_number}"
        serial_number: str = f"{device.serial_number}"

        devices.append((vendor, product, version, serial_number))

    devices = [("Vendor", "Product", "Version", "Serial Number"), *sorted(set(devices))]

    output_table(devices)

    return SUCCESS


class State(AbstractContextManager):
    """The current state of the system."""

    check_interval: float = 0.1
    timeout: float = 1.5e9

    @override
    def __init__(self, vendor_id: int, product_id: int, capture_device: str, render_device: str) -> None:
        self.vendor_id: int = vendor_id
        self.product_id: int = product_id
        self.capture_device: str = capture_device
        self.render_device: str = render_device

        self.devices: list[HidDevice] = []

        self.lock: Lock = Lock()
        self.last_heartbeat: int = 0
        self.connected: bool = False

        self.prev_capture_device: str = ""
        self.prev_render_device: str = ""

    @override
    def __enter__(self) -> Self:
        self.load_devices()
        return self

    @override
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
        /,
    ) -> None:
        self.unload_devices()

    def load_devices(self) -> None:
        """Loads the devices using the vendor and product IDs."""
        self.unload_devices()

        filter: HidDeviceFilter = HidDeviceFilter(vendor_id=self.vendor_id, product_id=self.product_id)

        device: HidDevice
        for device in filter.get_devices():
            try:
                device.open()
                device.set_raw_data_handler(self._data_handler_)
                self.devices.append(device)
                logger.info("Listening on: %s", device.device_path)
            except Exception as e:  # noqa: BLE001
                logger.warning("Unable to open device:", exc_info=e)

    def unload_devices(self) -> None:
        """Unloads and loaded devices."""
        if len(self.devices) == 0:
            return

        device: HidDevice
        for device in self.devices:
            with contextlib.suppress(BaseException):
                device.close()

        self.devices.clear()

    def _data_handler_(self, data: list[str]) -> None:
        """Handles receiving data from the usb devices."""
        now: int = time.perf_counter_ns()
        with self.lock:
            if self.find_heartbeat(data):
                logger.debug("Device heartbeat")
                self.last_heartbeat = now

    def find_heartbeat(self, data: list[str]) -> bool:
        """Determine if the data received was a heartbeat."""
        string: str = ",".join(map(str, data))

        match: Match[str] | None = re.fullmatch(HEARTBEAT_PATTERNS[self.vendor_id, self.product_id], string)

        return match is not None

    def listen(self) -> None:
        """Listen for heartbeats."""
        # Load current input and output devices
        while True:
            try:
                with self.lock:
                    last_connected: bool = self.connected
                    self.connected = time.perf_counter_ns() - self.last_heartbeat < self.timeout
                    if last_connected != self.connected:
                        if self.connected:
                            self.set_headphones()
                        else:
                            self.set_previous()
                time.sleep(self.check_interval)
            except KeyboardInterrupt:
                break

    def set_headphones(self) -> None:
        """Set the configured headphones as the sound device."""
        sound_device: SoundDevice
        for sound_device in get_sound_devices():
            match sound_device.default:
                case "Capture":
                    self.prev_capture_device = sound_device.name
                case "Render":
                    self.prev_render_device = sound_device.name

        self.set_default_device("capture", self.capture_device)
        self.set_default_device("render", self.render_device)

    def set_previous(self) -> None:
        """Set the previous device as the sound device."""
        if self.prev_capture_device != "":
            self.set_default_device("capture", self.prev_capture_device)
        if self.prev_render_device != "":
            self.set_default_device("render", self.prev_render_device)

    @staticmethod
    def set_default_device(dev_type: str, name: str) -> None:
        """Set the default device."""
        try:
            subprocess.run(  # noqa: S603
                [str(SOUND_VOLUME_VIEW_PATH), "/SetDefault", name, "1"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            subprocess.run(  # noqa: S603
                [str(SOUND_VOLUME_VIEW_PATH), "/SetDefault", name, "2"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.info("Set %s device: %s", dev_type, name)
        except CalledProcessError as e:
            logger.exception("Failed to set %s device: %s", dev_type, name, exc_info=e)


def get_sound_devices() -> list[SoundDevice]:
    """Get sound devices using SoundVolumeView."""
    devices: list[SoundDevice] = []

    device_file: Path = Path("devices.txt")

    result: CompletedProcess[bytes] = subprocess.run(  # noqa: S603
        [str(SOUND_VOLUME_VIEW_PATH), "/stab", str(device_file)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if not device_file.is_file():
        raise RuntimeError(f"SoundVolumeView.exe exit code: 0x{result.returncode:08X}")

    try:
        # If the file is encoded in BOM_UTF16_LE, we remove those bits before decoding
        raw_contents: bytes = device_file.read_bytes().removeprefix(BOM_UTF16_LE)
        contents: list[str] = raw_contents.decode("utf-16le").splitlines()

        for line in contents[1:]:  # Skip header row
            row: list[str] = line.split("\t")

            type: str = row[1]
            if type != "Device":
                continue

            direction: str = row[2]
            name: str = row[3]
            default: str = row[4]
            # default_mult: str = row[5]
            # default_comm: str = row[6]

            devices.append(SoundDevice(direction, name, default))
    finally:
        device_file.unlink(missing_ok=True)

    return devices


def output_table[T: tuple](table: list[T]) -> None:
    """Output an aligned table of string values to stdout."""
    if len(table) == 0:
        return

    widths: list[int] = []
    for i in range(len(table[0])):
        width: int = 0
        for row in table:
            width = max(width, len(row[i]))
        widths.append(width)
    format: str = " | ".join(f"{{:>{w}}}" for w in widths)

    for row in table:
        sys.stdout.write(format.format(*row) + "\n")


if __name__ == "__main__":
    manager.handle_main()
