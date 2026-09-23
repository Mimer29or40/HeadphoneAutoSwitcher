"""Infrastructure services, as described by Clean Architecture."""

from __future__ import annotations

import logging
import re
import subprocess
import tempfile
from codecs import BOM_UTF16_LE
from dataclasses import dataclass
from pathlib import Path
from subprocess import CompletedProcess
from typing import TYPE_CHECKING
from typing import ClassVar
from typing import override
from uuid import UUID

from _ca.domain import ErrorMsg
from domain.entity import SoundDevice
from domain.exception import SoundDeviceProviderError
from domain.service import SoundDeviceProvider
from domain.value import SoundDeviceType

if TYPE_CHECKING:
    from logging import Logger


logger: Logger = logging.getLogger("infrastructure.service")


type Row = list[str]

SOUND_VOLUME_VIEW_NOT_FOUND_ERROR: ErrorMsg = ErrorMsg("SoundVolumeView: executable not found")
SOUND_VOLUME_VIEW_NON_ZERO_RETURN: ErrorMsg = ErrorMsg("SoundVolumeView: non-zero exit code")

DEFAULT_SOUND_VOLUME_VIEW_PATH: Path = Path("SoundVolumeView.exe")
DEFAULT_SOUND_VOLUME_VIEW_OUTPUT_FILE: Path = Path(tempfile.gettempdir()) / "SoundVolumeView-Output.txt"


@dataclass(frozen=True, slots=True)
class SoundVolumeView(SoundDeviceProvider):
    """SoundDeviceProvider with SoundVolumeView."""

    sound_volume_view_path: Path = DEFAULT_SOUND_VOLUME_VIEW_PATH
    output_file: Path = DEFAULT_SOUND_VOLUME_VIEW_OUTPUT_FILE

    @override
    def find(self, device_id: UUID) -> SoundDevice | None:
        query: list[Row] = self._query_device_rows()

        row: Row
        for row in query:
            extracted_id: UUID | None = self._extract_uuid(row)
            if extracted_id == device_id:
                device: SoundDevice = self._create_device(device_id, row)
                return device
        return None

    @override
    def find_all(self) -> list[SoundDevice]:
        query: list[Row] = self._query_device_rows()

        sound_devices: list[SoundDevice] = []
        row: Row
        for row in query:
            device_id: UUID | None = self._extract_uuid(row)
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

    def _query_device_rows(self) -> list[Row]:  # pragma: no cover
        query: list[str] = self._query()

        device_rows: list[Row] = []
        line: str
        for line in query[1:]:  # Drop Header Row
            row: Row = line.split("\t")

            type: str = row[self.COLUMN_TYPE]
            if type != "Device":
                continue

            device_rows.append(row)

        return device_rows

    def _extract_uuid(self, row: Row) -> UUID | None:  # pragma: no cover
        registry_key: str = row[self.COLUMN_REGISTRY_KEY]
        uuid_match: re.Match[str] | None = self.UUID_PATTERN.search(registry_key)
        if uuid_match is None:
            logger.debug("Bad registry key: %s", registry_key)
            return None
        uuid: UUID = UUID(uuid_match.group(1))
        return uuid

    def _create_device(self, device_id: UUID, row: Row) -> SoundDevice:  # pragma: no cover
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
    COLUMN_CHANNELS_PERCENT = 16
    COLUMN_ITEM_ID: ClassVar[int] = 17
    COLUMN_COMMAND_LINE_FRIENDLY_ID: ClassVar[int] = 18
    COLUMN_PROCESS_PATH: ClassVar[int] = 19
    COLUMN_PROCESS_ID: ClassVar[int] = 20
    COLUMN_WINDOW_TITLE: ClassVar[int] = 21
    COLUMN_REGISTRY_KEY: ClassVar[int] = 22
    COLUMN_SPEAKERS_CONFIG: ClassVar[int] = 23
    COLUMN_DEFAULT_FORMAT: ClassVar[int] = 24
    COLUMN_LAST: ClassVar[int] = COLUMN_DEFAULT_FORMAT

    UUID_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
        flags=re.IGNORECASE,
    )
