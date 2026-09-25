"""Headphone Auto Switcher SoundVolumeView implementation."""

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
from headphone_auto_switcher.domain.entity import SoundDevice
from headphone_auto_switcher.domain.error import SoundVolumeProviderError
from headphone_auto_switcher.domain.service import SoundDeviceProvider
from headphone_auto_switcher.domain.value import SoundDeviceType
from headphone_auto_switcher.utils import extract_uuid

if TYPE_CHECKING:
    from logging import Logger
    from uuid import UUID

type Row = list[str]

logger: Logger = logging.getLogger("has.infrastructure.sound_volume_view")

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
    def get_one(self, device_id: UUID) -> SoundDevice | None:
        device_rows: list[Row] = self._get_device_rows()

        row: Row
        for row in device_rows:
            uuid: UUID | None = self._get_uuid(row)
            if uuid == device_id:
                device: SoundDevice = self._create_device(device_id, row)
                return device
        return None

    @override
    def get_all(self, device_id: UUID) -> list[SoundDevice]:
        device_rows: list[Row] = self._get_device_rows()

        devices: list[SoundDevice] = []
        row: Row
        for row in device_rows:
            uuid: UUID | None = self._get_uuid(row)
            if uuid is None:
                continue

            device: SoundDevice = self._create_device(device_id, row)
            devices.append(device)
        return devices

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
                raise SoundVolumeProviderError(SOUND_VOLUME_VIEW_NON_ZERO_EXIT_CODE)

            # The output file is encoded as utf-16le so we remove the starting bits and decode
            data: bytes = self.output_file.read_bytes().removeprefix(BOM_UTF16_LE)
            return data.decode("utf-16le")
        except OSError:
            raise SoundVolumeProviderError(SOUND_VOLUME_VIEW_EXECUTABLE_NOT_FOUND) from None
        finally:
            self.output_file.unlink(missing_ok=True)

    def _get_device_rows(self) -> list[Row]:
        data: str = self._call_executable()

        rows: list[Row] = []
        line: str
        for line in data.splitlines()[1:]:  # Skip header row
            row: Row = line.split("\t")

            row_type: str = row[COLUMN_TYPE]
            if row_type != "Device":
                continue

            rows.append(row)
        return rows

    @staticmethod
    def _create_device(device_id: UUID, row: Row) -> SoundDevice:
        device_type: SoundDeviceType = {
            "Capture": SoundDeviceType.INPUT,
            "Render": SoundDeviceType.OUTPUT,
        }[row[COLUMN_DIRECTION]]
        device_name: str = row[COLUMN_DEVICE_NAME]
        device_selected: bool = row[COLUMN_DEFAULT] != ""

        device: SoundDevice = SoundDevice(
            type=device_type,
            name=device_name,
            selected=device_selected,
        )
        device.id = device_id
        logger.debug("Created SoundDevice: %s", device)

        return device

    @staticmethod
    def _get_uuid(row: Row) -> UUID | None:
        registry_key: str = row[COLUMN_REGISTRY_KEY]
        uuid: UUID | None = extract_uuid(registry_key)
        if uuid is None:
            logger.debug("Bad Registry Key: '%s'", registry_key)
        return uuid


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
