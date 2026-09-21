"""Domain services, as described by Clean Architecture."""

from __future__ import annotations

import logging
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging import Logger
    from uuid import UUID

    from domain.entity import SoundDevice


logger: Logger = logging.getLogger("domain.service")


class BaseService(ABC):
    """Base service class, implementing Clean Architecture patterns."""


# ---------- Project Specific ---------- #


class SoundDeviceProvider(BaseService, ABC):
    """Service provider for getting SoundDevices."""

    @abstractmethod
    def find(self, device_id: UUID) -> SoundDevice | None:
        """Find a SoundDevice by its UUID, if available on the system."""

    @abstractmethod
    def get_all(self) -> list[SoundDevice]:
        """Get a list of all SoundDevices on the system."""
