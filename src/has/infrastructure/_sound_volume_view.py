"""Headphone Auto Switcher SoundVolumeView SoundDeviceProvider implementation."""

from __future__ import annotations

import logging
import subprocess
import tempfile
from codecs import BOM_UTF16_LE
from dataclasses import dataclass
from pathlib import Path
from subprocess import CompletedProcess
from typing import TYPE_CHECKING
from typing import Any
from typing import override

from ca.domain import ErrorMsg
from ca.utils import log_call
from has.domain.entity import SoundDevice
from has.domain.error import SoundDeviceProviderError
from has.domain.service import SoundDeviceProvider
from has.domain.value import SoundDeviceType
from has.utils import extract_uuid

if TYPE_CHECKING:
    from logging import Logger
    from uuid import UUID

type RawSoundDevice = list[str]

logger: Logger = logging.getLogger("has.infrastructure._sound_volume_view")

SOUND_VOLUME_VIEW_EXECUTABLE_NOT_FOUND: ErrorMsg = ErrorMsg("SoundVolumeView: Executable not found.")
SOUND_VOLUME_VIEW_NON_ZERO_EXIT_CODE: ErrorMsg = ErrorMsg("SoundVolumeView: Non-zer exit code.")

SOUND_VOLUME_VIEW_EXECUTABLE_PATH: Path = Path("SoundVolumeView.exe")
SOUND_VOLUME_VIEW_OUTPUT_FILE_PATH: Path = Path(tempfile.gettempdir()) / "SoundVolumeView-Output.txt"


@dataclass(frozen=True, slots=True)
class SoundVolumeView(SoundDeviceProvider):
    """SoundDeviceProvider using SoundVolumeView."""

    executable: Path = SOUND_VOLUME_VIEW_EXECUTABLE_PATH
    output_file: Path = SOUND_VOLUME_VIEW_OUTPUT_FILE_PATH

    @override
    @log_call(type="method")
    def get_raw_devices(self) -> list[RawSoundDevice]:
        data: str = self._call_executable()

        raw_devices: list[RawSoundDevice] = []
        line: str
        for line in data.splitlines()[1:]:  # Skip header row
            raw_device: RawSoundDevice = line.split("\t")

            raw_device_type: str = raw_device[COLUMN_TYPE]
            if raw_device_type != "Device":
                continue

            raw_devices.append(raw_device)
        return raw_devices

    @override
    def get_uuid(self, raw_device: RawSoundDevice) -> UUID | None:
        registry_key: str = raw_device[COLUMN_REGISTRY_KEY]
        uuid: UUID | None = extract_uuid(registry_key)
        if uuid is None:
            logger.debug("Bad Registry Key: '%s'", registry_key)
        return uuid

    @override
    def create_device(self, device_id: UUID, raw_device: RawSoundDevice) -> SoundDevice:
        device_type: SoundDeviceType = {
            "Capture": SoundDeviceType.INPUT,
            "Render": SoundDeviceType.OUTPUT,
        }[raw_device[COLUMN_DIRECTION]]
        device_name: str = raw_device[COLUMN_DEVICE_NAME]
        device_selected: bool = raw_device[COLUMN_DEFAULT] != ""

        device: SoundDevice = SoundDevice(
            id=device_id,
            type=device_type,
            name=device_name,
            selected=device_selected,
        )
        return device

    def _call_executable(self) -> str:
        try:
            command: list[Any] = [self.executable, "/stab", self.output_file]
            logger.debug("Executing: %s", command)

            result: CompletedProcess[bytes] = subprocess.run(  # noqa: S603
                list(map(str, command)),
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.debug("Exit code: %s", result.returncode)

            if not self.output_file.is_file():
                raise SoundDeviceProviderError(SOUND_VOLUME_VIEW_NON_ZERO_EXIT_CODE)

            # The output file is encoded as utf-16le so we remove the starting bits and decode
            data: bytes = self.output_file.read_bytes().removeprefix(BOM_UTF16_LE)
            return data.decode("utf-16le")
        except OSError:
            raise SoundDeviceProviderError(SOUND_VOLUME_VIEW_EXECUTABLE_NOT_FOUND) from None
        finally:
            self.output_file.unlink(missing_ok=True)


COLUMN_NAME: int = 0
COLUMN_TYPE: int = 1
COLUMN_DIRECTION: int = 2
COLUMN_DEVICE_NAME: int = 3
COLUMN_DEFAULT: int = 4
COLUMN_DEFAULT_MULTIMEDIA: int = 5
COLUMN_DEFAULT_COMMUNICATIONS: int = 6
COLUMN_DEVICE_STATE: int = 7
COLUMN_MUTED: int = 8
COLUMN_VOLUME_DB: int = 9
COLUMN_VOLUME_PERCENT: int = 10
COLUMN_MIN_VOLUME_DB: int = 11
COLUMN_MAX_VOLUME_DB: int = 12
COLUMN_VOLUME_STEP: int = 13
COLUMN_CHANNELS_COUNT: int = 14
COLUMN_CHANNELS_DB: int = 15
COLUMN_CHANNELS_PERCENT: int = 16
COLUMN_ITEM_ID: int = 17
COLUMN_COMMAND_LINE_FRIENDLY_ID: int = 18
COLUMN_PROCESS_PATH: int = 19
COLUMN_PROCESS_IO: int = 20
COLUMN_WINDOW_TITLE: int = 21
COLUMN_REGISTRY_KEY: int = 22
COLUMN_SPEAKER_CONFIG: int = 23
COLUMN_DEFAULT_FORMAT: int = 24

COLUMN_LAST: int = COLUMN_DEFAULT_FORMAT
