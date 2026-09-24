"""Domain services, as described by Clean Architecture."""

from __future__ import annotations

import logging
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING

from _ca.domain import BaseService

if TYPE_CHECKING:
    from logging import Logger
    from uuid import UUID

    from domain.entity import SoundDevice
    from domain.entity import UsbDevice
    from domain.value import UsbDevicePacket


logger: Logger = logging.getLogger("domain.service")


class SoundDeviceProvider(BaseService, ABC):
    """Service provider for getting SoundDevices."""

    @abstractmethod
    def find(self, device_id: UUID) -> SoundDevice | None:
        """Find a SoundDevice by its UUID, if available on the system."""

    @abstractmethod
    def find_all(self) -> list[SoundDevice]:
        """Get a list of all SoundDevices on the system."""


class UsbDeviceProvider(BaseService, ABC):
    """Service provider for getting UsbDevices."""

    @abstractmethod
    def find(self, device_id: UUID) -> UsbDevice | None:
        """Find a UsbDevice by its UUID, if available on the system."""

    @abstractmethod
    def find_all(self) -> list[UsbDevice]:
        """Get a list of all UsbDevices on the system."""


class UsbDeviceListener(BaseService, ABC):
    """Service to listen to UsbDevices for communication packets."""

    @abstractmethod
    def start(self, vendor_id: int, product_id: int) -> None:
        """Start listening to UsbDevices."""

    @abstractmethod
    def stop(self) -> None:
        """Stop listening to UsbDevices."""

    @abstractmethod
    def get_packet(self, block: bool = True, timeout: float | None = None) -> UsbDevicePacket:
        """Get a packet from the Listener."""
