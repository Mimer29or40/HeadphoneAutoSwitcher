"""Headphone Auto Switcher domain service module."""

from __future__ import annotations

import logging
from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any

from ca.domain import BaseEntity
from ca.domain import BaseService
from ca.utils import log_call
from has.domain.entity import SoundDevice
from has.domain.entity import UsbDevice

if TYPE_CHECKING:
    from logging import Logger
    from uuid import UUID

    from has.domain.value import UsbDevicePacket

logger: Logger = logging.getLogger("has.domain.service")


class _DeviceProviderMixIn[T: BaseEntity, RAW](ABC):
    @abstractmethod
    def get_raw_devices(self) -> list[RAW]: ...

    @abstractmethod
    def get_uuid(self, raw_device: RAW) -> UUID | None: ...

    @abstractmethod
    def create_device(self, device_id: UUID, raw_device: RAW) -> T: ...

    @log_call(type="method", level=logging.INFO)
    def get_one(self, device_id: UUID) -> T | None:
        raw_devices: list[RAW] = self.get_raw_devices()

        raw_device: RAW
        for raw_device in raw_devices:
            raw_device_id: UUID | None = self.get_uuid(raw_device)
            if raw_device_id == device_id:
                device: T = self.create_device(device_id, raw_device)
                return device
        return None

    @log_call(type="method", level=logging.INFO)
    def get_all(self) -> list[T]:
        raw_devices: list[RAW] = self.get_raw_devices()

        devices: list[T] = []
        raw_device: RAW
        for raw_device in raw_devices:
            device_id: UUID | None = self.get_uuid(raw_device)
            if device_id is None:
                continue

            device: T = self.create_device(device_id, raw_device)
            devices.append(device)
        return devices


class SoundDeviceProvider(BaseService, _DeviceProviderMixIn[SoundDevice, Any], ABC):
    """Provider service of SoundDevices."""


class UsbDeviceProvider(BaseService, _DeviceProviderMixIn[UsbDevice, Any], ABC):
    """Provider service of UsbDevices."""

    # TODO(Ryan): get_all(vendor_id: int = None, product_id: int = None)


class UsbDevicePacketListener(ABC):
    """Listens to UsbDevices."""

    @abstractmethod
    def start(self, vendor_id: int, product_id: int) -> None:
        """Start listening for UsbDevicesPacket."""
        # TODO(Ryan): Explicitly pass UsbDevice list to listen to

    @abstractmethod
    def stop(self) -> None:
        """Stop listening for UsbDevicePackets."""

    @abstractmethod
    def get(self, block: bool = True, timeout: float | None = None) -> UsbDevicePacket | None:
        """Get a UsbDevicePacket from the Listener."""
