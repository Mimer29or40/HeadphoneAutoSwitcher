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
from typing import Any
from typing import ClassVar
from typing import override
from uuid import UUID

from domain.entity import SoundDevice
from domain.exception import ErrorMsg
from domain.exception import SoundDeviceProviderError
from domain.service import SoundDeviceProvider

if TYPE_CHECKING:
    from logging import Logger


logger: Logger = logging.getLogger("infrastructure.service")


# ---------- Project Specific ---------- #


type Row = list[str]

SOUND_VOLUME_VIEW_NOT_FOUND_ERROR: ErrorMsg = ErrorMsg("SoundVolumeView executable not found")
_SENTINEL: Any = object()


@dataclass(frozen=True, slots=True)
class SoundVolumeView(SoundDeviceProvider):
    """SoundDeviceProvider with SoundVolumeView."""

    sound_volume_view_path: Path = _SENTINEL
    output_file: Path = _SENTINEL

    def __post_init__(self) -> None:
        """Fill in the blanks."""
        if self.sound_volume_view_path is _SENTINEL:
            sound_volume_view_path: Path = Path("SoundVolumeView.exe")
            object.__setattr__(self, "sound_volume_view_path", sound_volume_view_path)

        if self.output_file is _SENTINEL:
            output_file: Path = Path(tempfile.gettempdir()) / "SoundVolumeView-Output.txt"
            object.__setattr__(self, "output_file", output_file)

    def _query(self) -> list[str]:
        try:
            result: CompletedProcess[bytes] = subprocess.run(  # noqa: S603
                [str(self.sound_volume_view_path), "/stab", str(self.output_file)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if not self.output_file.is_file():
                raise RuntimeError(f"SoundVolumeView.exe exit code: 0x{result.returncode:08X}")

            # If the file is encoded in BOM_UTF16_LE, we remove those bits before decoding
            raw_query: bytes = self.output_file.read_bytes().removeprefix(BOM_UTF16_LE)
            return raw_query.decode("utf-16le").splitlines()
        except FileNotFoundError:
            raise SoundDeviceProviderError(SOUND_VOLUME_VIEW_NOT_FOUND_ERROR) from None
        finally:
            self.output_file.unlink(missing_ok=True)

    def _query_device_rows(self) -> list[Row]:
        device_rows: list[Row] = []

        query: list[str] = self._query()

        line: str
        for line in query[1:]:  # Drop Header Row
            row: Row = line.split("\t")

            type: str = row[self.COLUMN_TYPE]
            if type != "Device":
                continue

            device_rows.append(row)

        return device_rows

    def _extract_uuid(self, row: Row) -> UUID | None:
        registry_key: str = row[self.COLUMN_REGISTRY_KEY]
        uuid_match: re.Match[str] | None = self.UUID_PATTERN.search(registry_key)
        if uuid_match is None:
            logger.debug("Bad registry key: %s", registry_key)
            return None
        uuid: UUID = UUID(uuid_match.group(1))
        return uuid

    @override
    def find(self, device_id: UUID) -> SoundDevice | None:
        pass

    @override
    def get_all(self) -> list[SoundDevice]:
        query: list[Row] = self._query_device_rows()

        sound_devices: list[SoundDevice] = []
        row: Row
        for row in query:
            device_id: UUID | None = self._extract_uuid(row)
            if device_id is None:
                continue

            direction: str = row[self.COLUMN_DIRECTION]
            device_name: str = row[self.COLUMN_DEVICE_NAME]
            default: str = row[self.COLUMN_DEFAULT]

            device: SoundDevice = SoundDevice(
                type=direction,
                name=device_name,
                default=default,
            )
            device.id = device_id
            logger.debug("Loaded SoundDevice: %s", device)

            sound_devices.append(device)

        return sound_devices

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

    UUID_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
        flags=re.IGNORECASE,
    )
