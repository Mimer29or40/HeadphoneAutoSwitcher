"""HeadphoneAutoSwitcher.

Config file to define headphone details
Define default device
"""

from __future__ import annotations

import contextlib
import json
import logging
import logging.config
import os
import re
import subprocess
import sys
import time
from argparse import REMAINDER
from argparse import ArgumentError
from argparse import ArgumentParser
from argparse import Namespace
from codecs import BOM_UTF16_LE
from dataclasses import Field
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import fields
from pathlib import Path
from re import Match
from subprocess import CalledProcessError
from subprocess import CompletedProcess
from threading import Lock
from typing import TYPE_CHECKING
from typing import Any
from typing import NamedTuple
from typing import NoReturn
from typing import Self
from typing import override

from pywinusb.hid import HidDevice
from pywinusb.hid import HidDeviceFilter

if TYPE_CHECKING:  # pragma: no cover
    from argparse import _ArgumentGroup
    from argparse import _SubParsersAction
    from collections.abc import Sequence
    from logging import Logger

app_name: str = "HeadphoneAutoSwitcher"
app_description: str = "Automatically switches the sound to Headphones when they are powered on."
app_version: str = "1.0.0"

logger: Logger = logging.getLogger()

# ----- Tunable parameter ----- #
CHECK_INTERVAL: float = 0.1  # seconds
TIMEOUT: float = 1.5  # seconds

# ----- Lookup table of heartbeat patterns ----- #
HEARTBEAT_PATTERNS: dict[tuple[str, str], str] = {
    ("0x1B1C", "0x2A08"): r"^1,1,6.*",  # CORSAIR VOID WIRELESS v2 Gaming Headset
}

# ----- Paths to files needed by the service ----- #
SOUND_VOLUME_VIEW_PATH: Path = Path("SoundVolumeView.exe")
CONFIG_PATH: Path = Path(f"{app_name}.json")


type CommandResult = int | str


class SoundDevice(NamedTuple):
    """A sound device loaded from SoundVolumeView."""

    direction: str
    name: str
    default: str


class UsbDevice(NamedTuple):
    """A USB device loaded from HidDeviceFilter."""

    vendor: str
    product: str
    version: str
    serial_number: str


def get_sound_devices() -> list[SoundDevice]:
    """Get sound devices."""
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


def get_usb_devices() -> list[UsbDevice]:
    """Get USB devices."""
    devices: list[UsbDevice] = []

    filter: HidDeviceFilter = HidDeviceFilter()
    device: HidDevice
    for device in filter.get_devices():
        vendor: str = f"{device.vendor_name} (0x{device.vendor_id:04X})"
        product: str = f"{device.product_name} (0x{device.product_id:04X})"
        version: str = f"{device.version_number}"
        serial_number: str = f"{device.serial_number}"

        devices.append(UsbDevice(vendor, product, version, serial_number))

    return devices


@dataclass(frozen=True, kw_only=True)
class Config:
    """HeadphoneAutoSwitcher config data structure."""

    vendor_id: str = ""
    product_id: str = ""
    capture_device: str = ""
    render_device: str = ""

    def save_to_file(self, file: Path) -> None:
        """Save the config to file."""
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(json.dumps(asdict(self), indent=4))

    @classmethod
    def load_from_file(cls, file_path: Path, errors: list[str]) -> Self:
        """Load config from file."""
        loaded: dict[str, str] = json.loads(file_path.read_text())

        values: dict[str, str] = {}
        f: Field
        for f in fields(cls):
            if f.name not in loaded:
                errors.append(f"{f.name} is required.")
            elif loaded[f.name] == "":
                errors.append(f"{f.name} is blank.")
            values[f.name] = loaded[f.name]

        return cls(**values)


class HeadphoneAutoSwitcher:
    """Headphone Auto Switcher."""

    @override
    def __init__(self, config: Config | None) -> None:
        if getattr(sys, "frozen", False):
            exe_file: Path = Path(sys.executable).parent
            os.chdir(exe_file)

        if config is None:
            config = Config.load_from_file(CONFIG_PATH, [])
        self.config: Config = config

        self.running: bool = False
        self.lock: Lock = Lock()
        self.heartbeat: float = 0.0
        self.connected: bool = False
        self.prev_capture_device: str = ""
        self.prev_render_device: str = ""

        self.devices: list[HidDevice] = []

    def open(self) -> None:
        """Open configured devices."""
        self.close()

        filter: HidDeviceFilter = HidDeviceFilter(
            vendor_id=int(self.config.vendor_id, 0),
            product_id=int(self.config.product_id, 0),
        )
        device: HidDevice
        for device in filter.get_devices():
            try:
                device.open()
                device.set_raw_data_handler(self._data_handler_)
                self.devices.append(device)
                logger.info("Opening: %s[%s]", device.product_name, device.instance_id)
            except Exception as e:  # noqa: BLE001
                logger.warning("Unable to open device: %s", device.product_name, exc_info=e)

    def close(self) -> None:
        """Closes all loaded devices."""
        device: HidDevice
        for device in self.devices:
            with contextlib.suppress(BaseException):
                device.close()
        self.devices.clear()

    def start(self) -> None:
        """Start the auto switcher."""
        try:
            self.open()

            self.running = True
            while self.running:  # Main loop we sit in once all systems are go for launch
                with self.lock:  # Acquire the lock to get prev_heartbeat because it is set in other threads
                    last_connected: bool = self.connected
                    self.connected = time.perf_counter() - self.heartbeat < TIMEOUT

                # Check for a state change and process accordingly
                if last_connected != self.connected:
                    if self.connected:
                        self.set_headphones()
                    else:
                        self.set_previous()

                time.sleep(CHECK_INTERVAL)
        finally:  # Stop signal received or something has failed
            self.close()

    def stop(self) -> None:
        """Stop the auto switcher."""
        self.running = False

    def _data_handler_(self, packet: list[str]) -> None:
        """Data handler function called on device listener threads."""
        pattern: str = HEARTBEAT_PATTERNS[self.config.vendor_id, self.config.product_id]

        packet_string: str = ",".join(map(str, packet))
        match: Match[str] | None = re.fullmatch(pattern, packet_string)

        if match is None:  # Not a heartbeat packet
            return

        with self.lock:
            self.heartbeat = time.perf_counter()

    def set_headphones(self) -> None:
        """Set the headphones as the sound device."""
        sound_device: SoundDevice
        for sound_device in get_sound_devices():
            match sound_device.default:
                case "Capture":
                    self.prev_capture_device = sound_device.name
                case "Render":
                    self.prev_render_device = sound_device.name

        self.set_default_device("capture", self.config.capture_device)
        self.set_default_device("render", self.config.render_device)

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


def sound() -> CommandResult:
    """List all sound devices."""
    devices: list[SoundDevice] = get_sound_devices()
    devices = [SoundDevice("Direction", "Name", "Default"), *sorted(set(devices))]

    output_table(devices)

    return 0


def usb() -> CommandResult:
    """List all USB devices."""
    devices: list[UsbDevice] = get_usb_devices()
    devices = [UsbDevice("Vendor", "Product", "Version", "Serial Number"), *sorted(set(devices))]

    output_table(devices)

    return 0


def validate() -> CommandResult:
    """Validate the config."""
    if not CONFIG_PATH.is_file():
        Config().save_to_file(CONFIG_PATH)

    errors: list[str] = []
    config: Config = Config.load_from_file(CONFIG_PATH, errors)
    if len(errors) > 0:
        logger.exception("Config contains errors: %s", ", ".join(errors))
        return "CONFIG_ERRORS"

    vendor_id: str = "0x" + config.vendor_id.removeprefix("0x")
    product_id: str = "0x" + config.product_id.removeprefix("0x")

    if (vendor_id, product_id) not in HEARTBEAT_PATTERNS:
        logger.critical("Headphone not supported: Vendor (%s) Product (%s)", vendor_id, product_id)
        return "UNSUPPORTED_HEADPHONES"

    switcher: HeadphoneAutoSwitcher = HeadphoneAutoSwitcher(None)

    switcher.open()
    device_count: int = len(switcher.devices)
    switcher.close()

    if device_count == 0:
        logger.critical("No devices found: Vendor (%s) Product (%s)", vendor_id, product_id)
        return "NO_DEVICES_FOUND"

    logger.info("Config validated!")

    return 0


def listen() -> CommandResult:
    """Begin listening to devices."""
    switcher: HeadphoneAutoSwitcher = HeadphoneAutoSwitcher(None)
    with contextlib.suppress(KeyboardInterrupt):
        switcher.start()
    return 0


def win_service(command_name: str | None, *args: Any) -> None:
    """Dispatch command to win32."""
    global Service  # ty:ignore[unresolved-global]
    import win32service  # noqa: PLC0415  # ty:ignore[unresolved-import]
    import win32serviceutil  # noqa: PLC0415

    class Service(win32serviceutil.ServiceFramework):
        """HeadphoneAutoSwitcher service class."""

        _svc_name_: str = app_name
        _svc_display_name_: str = app_name
        _svc_description_: str = app_description
        _svc_deps_: Sequence[str] | None = None

        @override
        def __init__(self, args: Sequence[str]) -> None:
            super().__init__(args)

            self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
            self.switcher: HeadphoneAutoSwitcher = HeadphoneAutoSwitcher(None)

        @override
        def SvcRun(self) -> None:
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.switcher.start()
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)

        def SvcStop(self) -> None:  # noqa: N802
            """Trigger the service shutdown sequence."""
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            self.switcher.stop()

    if command_name is None:
        import servicemanager  # ty:ignore[unresolved-import]  # noqa: PLC0415

        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(Service)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(Service, argv=(sys.argv[0], *args))


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


def _create_command_parser() -> ArgumentParser:
    prog: str = f"{app_name}.exe" if getattr(sys, "frozen", False) else f"{app_name}.py"
    parser: ArgumentParser = ArgumentParser(prog=prog, description=app_description, exit_on_error=False)

    parser.add_argument("-v", "--version", action="version", version=app_version)

    command_parser: _SubParsersAction = parser.add_subparsers(
        title="commands",
        dest="command",
        metavar="command",
    )

    command_parser.add_parser(
        "sound",
        help="enumerate sound devices",
    )
    command_parser.add_parser(
        "usb",
        help="enumerate USB devices",
    )
    command_parser.add_parser(
        "validate",
        help="validate device configuration",
    )
    command_parser.add_parser(
        "listen",
        help="begin listening to devices",
    )

    _create_win_service_commands(parser, command_parser)

    return parser


def _create_win_service_commands(parser: ArgumentParser, command_parser: _SubParsersAction) -> None:
    """Re-Create win32serviceutil.HandleCommandLine commands so we can provide ones."""
    argument_group: _ArgumentGroup
    argument_group: _ArgumentGroup = parser.add_argument_group("options for 'install' and 'update' commands only")
    argument_group.add_argument(
        "--username",
        metavar="DOMAIN\\USERNAME",
        help="the username the service is to run under",
    )
    argument_group.add_argument(
        "--password",
        help="the password for the username",
    )
    argument_group.add_argument(
        "--startup",
        choices=["manual", "auto", "disabled", "delayed"],
        help="how the service starts, default = manual",
    )
    argument_group.add_argument(
        "--interactive",
        action="store_true",
        help="allow the service to interact with the desktop",
    )
    argument_group.add_argument(
        "--perfmonini",
        type=Path,
        metavar="FILE",
        help="file to use for registering performance monitor data",
    )
    argument_group.add_argument(
        "--perfmondll",
        type=Path,
        metavar="FILE",
        help="file to use when querying the service for performance data, default = perfmondata.dll",
    )

    argument_group = parser.add_argument_group("options for 'start' and 'stop' commands only")
    argument_group.add_argument(
        "--wait",
        type=int,
        default=0,
        metavar="SECONDS",
        help=(
            "wait for the service to actually start or stop. If you specify --wait with "
            "the 'stop' option, the service and all dependent services will be stopped, "
            "each waiting the specified period"
        ),
    )

    # Win32 Defined Commands
    command_parser.add_parser(
        "install",
        help="install the service",
    )
    command_parser.add_parser(
        "remove",
        help="remove the service",
    )
    command_parser.add_parser(
        "update",
        help="update the service",
    )
    command_parser.add_parser(
        "stop",
        help="stop the service",
    )

    sub_parser: ArgumentParser
    sub_parser = command_parser.add_parser(
        "start",
        help="start the service",
    )
    sub_parser.add_argument(
        "arguments",
        nargs=REMAINDER,
        help="arguments passed to service constructor",
    )

    sub_parser = command_parser.add_parser(
        "restart",
        help="stops, then starts the service",
    )
    sub_parser.add_argument(
        "arguments",
        nargs=REMAINDER,
        help="arguments passed to service constructor",
    )

    sub_parser = command_parser.add_parser(
        "debug",
        help="runs the service in debug mode",
    )
    sub_parser.add_argument(
        "arguments",
        nargs=REMAINDER,
        help="arguments passed to service constructor",
    )


def run(*args: Any) -> CommandResult:
    """Run command line with arguments."""
    logging.config.dictConfig(
        {
            "version": 1,
            "incremental": False,
            "disable_existing_loggers": False,
            "formatters": {"standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}},
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": "INFO",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {"level": "DEBUG", "handlers": ["console"]},
        }
    )

    exit_code: CommandResult = 0
    try:
        parser: ArgumentParser = _create_command_parser()
        parsed_args: Namespace = parser.parse_args(args)

        command_name: str | None = parsed_args.command
        match command_name:
            case "sound":
                sound()
            case "usb":
                usb()
            case "validate":
                validate()
            case "listen":
                listen()
            case _:
                win_service(command_name, *args)
    except ArgumentError as e:
        # Raised when ArgumentParser fails to parse the arguments.
        logger.exception("Argparse error:", exc_info=e)
        exit_code = 1
    except SystemExit:
        # ArgParser exited, either error or help/version
        exit_code = 0
    except BaseException as e:
        logger.exception("Unhandled exception:", exc_info=e)
        exit_code = -1

    return exit_code


def handle_main() -> NoReturn:
    """Handle main."""
    args: list[str] = sys.argv[1:]
    result: CommandResult = run(*args)
    sys.exit(result)


if __name__ == "__main__":
    handle_main()
