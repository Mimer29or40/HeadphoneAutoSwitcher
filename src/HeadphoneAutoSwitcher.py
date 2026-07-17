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
from abc import ABC
from abc import abstractmethod
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
from queue import Empty
from queue import Full
from queue import Queue
from subprocess import CalledProcessError
from subprocess import CompletedProcess
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
    from re import Pattern

app_name: str = "HeadphoneAutoSwitcher"
app_description: str = "Automatically switches the sound to Headphones when they are powered on."
app_version: str = "2.0.0"

logger: Logger = logging.getLogger()

# ----- Paths to files needed by the service ----- #
SOUND_VOLUME_VIEW_PATH: Path = Path("SoundVolumeView.exe")
CONFIG_PATH: Path = Path(f"{app_name}.json")
HANDLER_DB_PATH: Path = Path("handler_db.json")


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

    if not SOUND_VOLUME_VIEW_PATH.is_file():
        raise FileNotFoundError("SoundVolumeView.exe not found")

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


class DeviceData(NamedTuple):
    """The data received from a device."""

    time: float
    packet: str


class DeviceListener:
    """Listens to USB devices."""

    @override
    def __init__(self, vendor_id: str, product_id: str, max_queue: int = 100) -> None:
        self.vendor_id: str = vendor_id
        self.product_id: str = product_id
        self.max_queue: int = max_queue

        self.devices: list[HidDevice] = []
        self.data: Queue[DeviceData] = Queue(self.max_queue)

    def _data_handler_(self, raw_packet: list[int]) -> None:
        """Data handler function called on device listener threads."""
        packet: DeviceData = DeviceData(time.perf_counter(), ",".join(map(str, raw_packet)))
        try:
            self.data.put_nowait(packet)
        except Full:
            with contextlib.suppress(Empty):
                self.data.get_nowait()
            self.data.put_nowait(packet)

    def load(self) -> None:
        """Load configured devices."""
        self.devices.clear()

        filter: HidDeviceFilter = HidDeviceFilter(vendor_id=int(self.vendor_id, 0), product_id=int(self.product_id, 0))
        device: HidDevice
        for device in filter.get_devices():
            self.devices.append(device)
            logger.info("Loading: %s[%s]", device.product_name, device.instance_id)

    def open(self) -> None:
        """Open loaded devices."""
        self.close()

        device: HidDevice
        for device in self.devices:
            try:
                device.open()
                device.set_raw_data_handler(self._data_handler_)
            except Exception as e:  # noqa: BLE001
                logger.warning("Unable to open device: %s", device.product_name, exc_info=e)

    def close(self) -> None:
        """Closes all loaded devices."""
        device: HidDevice
        for device in self.devices:
            with contextlib.suppress(BaseException):
                device.close()

        self.data.shutdown()
        self.data: Queue[DeviceData] = Queue(self.max_queue)


type ConnectionState = bool | None


class DeviceHandler(ABC):
    """Handle USB data."""

    @abstractmethod
    @override
    def __init__(self, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def is_connected(self, listener: DeviceListener) -> ConnectionState:
        """Check if device is connected."""


class Heartbeat(DeviceHandler):
    """Devices that periodically send data packets."""

    @override
    def __init__(self, timeout: float) -> None:
        self.timeout: float = timeout
        self._state: bool = False

    @override
    def is_connected(self, listener: DeviceListener) -> ConnectionState:
        last_state: bool = self._state
        try:
            listener.data.get(timeout=self.timeout)
            self._state = True
        except Empty:
            self._state = False
        return self._state if last_state != self._state else None


class OnOff(DeviceHandler):
    """Devices that send data packets on power on and off."""

    @override
    def __init__(self, on_pattern: str, off_pattern: str) -> None:
        self.on_pattern: Pattern[str] = re.compile(on_pattern)
        self.off_pattern: Pattern[str] = re.compile(off_pattern)

    @override
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(on_pattern={self.on_pattern!r}, off_pattern={self.off_pattern!r})"

    @override
    def is_connected(self, listener: DeviceListener) -> ConnectionState:
        with contextlib.suppress(Empty):
            data: DeviceData = listener.data.get(block=False)
            if self.on_pattern.match(data.packet) is not None:
                return True
            if self.off_pattern.match(data.packet) is not None:
                return False
        return None


def get_device_handler(file_path: Path, vendor_id: str, product_id: str) -> DeviceHandler:
    """Get a DeviceHandler from the file with the vendor_id and product_id."""
    device_db: dict[str, Any] = json.loads(file_path.read_text())

    version: int = device_db["version"]
    if version != 1:
        raise RuntimeError("version must be set to 1")

    handler_map: dict[str, dict[str, Any]] = device_db["handlers"]

    hand_name: str
    hand_props: dict[str, Any]
    for hand_name, hand_props in handler_map.items():
        hand_vid: str = hand_props.pop("vendor_id")
        hand_pid: str = hand_props.pop("product_id")

        if hand_vid != vendor_id or hand_pid != product_id:
            continue

        logger.info("Loading device handler: %s (%s,%s)", hand_name, hand_vid, hand_pid)

        hand_type: str = hand_props.pop("type")
        hand_cls: type[DeviceHandler] = {"heartbeat": Heartbeat, "on/off": OnOff}[hand_type]

        return hand_cls(**hand_props)

    raise KeyError(f"no DeviceHandler found for ({vendor_id},{product_id})")


class HeadphoneAutoSwitcher:
    """Headphone Auto Switcher."""

    @override
    def __init__(self, config: Config) -> None:
        self.capture_device: str = config.capture_device
        self.render_device: str = config.render_device

        self.listener: DeviceListener = DeviceListener(config.vendor_id, config.product_id)
        self.handler: DeviceHandler = get_device_handler(HANDLER_DB_PATH, config.vendor_id, config.product_id)

        self.running: bool = False
        self.prev_capture_device: str = ""
        self.prev_render_device: str = ""

    def start(self) -> None:
        """Start the auto switcher."""
        try:
            self.listener.load()
            self.listener.open()

            self.running = True
            while self.running:  # Main loop we sit in once all systems are go for launch
                connected: ConnectionState = self.handler.is_connected(self.listener)

                # Check for a state change and process accordingly
                if connected is not None:
                    if connected:
                        self.set_headphones()
                    else:
                        self.set_previous()
        finally:  # Stop signal received or something has failed
            self.listener.close()

    def stop(self) -> None:
        """Stop the auto switcher."""
        self.running = False

    def set_headphones(self) -> None:
        """Set the headphones as the sound device."""
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


# ---------- Command Stuff ---------- #


type CommandResult = int | str


def cmd_sound() -> CommandResult:
    """List all sound devices."""
    devices: list[SoundDevice] = get_sound_devices()
    devices = [SoundDevice("Direction", "Name", "Default"), *sorted(set(devices))]

    output_table(devices)

    return 0


def cmd_usb() -> CommandResult:
    """List all USB devices."""
    devices: list[UsbDevice] = get_usb_devices()
    devices = [UsbDevice("Vendor", "Product", "Version", "Serial Number"), *sorted(set(devices))]

    output_table(devices)

    return 0


def cmd_validate() -> CommandResult:
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

    try:
        handler: DeviceHandler = get_device_handler(HANDLER_DB_PATH, vendor_id, product_id)
        logger.info("Handler found: %s", handler)
    except KeyError:
        logger.critical("Headphone not supported: Vendor (%s) Product (%s)", vendor_id, product_id)
        return "UNSUPPORTED_HEADPHONES"

    listener: DeviceListener = DeviceListener(config.vendor_id, config.product_id)

    listener.load()
    device_count: int = len(listener.devices)

    if device_count == 0:
        logger.critical("No devices found: Vendor (%s) Product (%s)", vendor_id, product_id)
        return "NO_DEVICES_FOUND"

    logger.info("Config validated!")

    return 0


def cmd_listen() -> CommandResult:
    """Listen to the configured device received data."""
    config: Config = Config.load_from_file(CONFIG_PATH, [])
    listener: DeviceListener = DeviceListener(config.vendor_id, config.product_id)
    try:
        listener.load()
        listener.open()
        while True:
            data: DeviceData = listener.data.get()
            logger.info("Received data: %s, %s", *data)
    except KeyboardInterrupt:
        pass
    finally:
        listener.close()

    return 0


def cmd_run() -> CommandResult:
    """Run the headphone switcher."""
    config: Config = Config.load_from_file(CONFIG_PATH, [])
    switcher: HeadphoneAutoSwitcher = HeadphoneAutoSwitcher(config)
    with contextlib.suppress(KeyboardInterrupt):
        switcher.start()
    return 0


def cmd_win_service(command_name: str | None, *args: Any) -> None:
    """Dispatch command to win32."""
    global Service  # ty:ignore[unresolved-global]
    import win32service  # noqa: PLC0415  # ty:ignore[unresolved-import]
    import win32serviceutil  # noqa: PLC0415

    # noinspection PyRedeclaration
    class Service(win32serviceutil.ServiceFramework):
        """HeadphoneAutoSwitcher service class."""

        _svc_name_: str = app_name
        _svc_display_name_: str = app_name
        _svc_description_: str = app_description
        _svc_deps_: Sequence[str] | None = None

        @override
        def __init__(self, args: Sequence[str]) -> None:
            super().__init__(args)

            if getattr(sys, "frozen", False):
                exe_file: Path = Path(sys.executable).parent
                os.chdir(exe_file)

            config: Config = Config.load_from_file(CONFIG_PATH, [])
            self.switcher: HeadphoneAutoSwitcher = HeadphoneAutoSwitcher(config)
            self.ReportServiceStatus(win32service.SERVICE_START_PENDING)

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
        help="listen to the configured device data",
    )
    command_parser.add_parser(
        "run",
        help="run the headphone switcher",
    )

    _create_win_service_commands(parser, command_parser)

    return parser


def _create_win_service_commands(parser: ArgumentParser, command_parser: _SubParsersAction) -> None:
    """Re-Create win32serviceutil.HandleCommandLine commands so we can provide ones."""
    argument_group: _ArgumentGroup
    argument_group = parser.add_argument_group("options for 'install' and 'update' commands only")
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


def main(*args: Any) -> CommandResult:
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
                cmd_sound()
            case "usb":
                cmd_usb()
            case "validate":
                cmd_validate()
            case "listen":
                cmd_listen()
            case "run":
                cmd_run()
            case _:
                cmd_win_service(command_name, *args)
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
    result: CommandResult = main(*args)
    sys.exit(result)


if __name__ == "__main__":
    handle_main()
