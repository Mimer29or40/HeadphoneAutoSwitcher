"""Headphone Auto Switcher console presentation module."""

from __future__ import annotations

import logging.config
from typing import TYPE_CHECKING
from typing import override

from ca.utils import log_call
from has.interface.presenter import SoundDevicePresenter
from has.interface.presenter import UsbDevicePresenter
from has.interface.presenter import ValidationPresenter
from has.interface.view_model import SoundDeviceViewModel
from has.interface.view_model import UsbDeviceViewModel
from has.interface.view_model import ValidationViewModel

if TYPE_CHECKING:
    from logging import Logger

    from has.application.dto import SoundDeviceResponse
    from has.application.dto import UsbDeviceResponse
    from has.application.dto import ValidationResponse

logger: Logger = logging.getLogger("has.presentation.console")


class ConsoleSoundDevicePresenter(SoundDevicePresenter):
    """SoundDevicePresenter for a console environment."""

    @classmethod
    @override
    @log_call(type="class")
    def present(cls, response: SoundDeviceResponse) -> SoundDeviceViewModel:
        return SoundDeviceViewModel(
            id=response.id,
            name=response.name,
            type=response.type,
            selected="Selected" if response.selected else "",
        )


class ConsoleUsbDevicePresenter(UsbDevicePresenter):
    """UsbDevicePresenter for a console environment."""

    @classmethod
    @override
    @log_call(type="class")
    def present(cls, response: UsbDeviceResponse) -> UsbDeviceViewModel:
        return UsbDeviceViewModel(
            id=response.id,
            product=f"{response.product_name} ({response.product_id})",
            vendor=f"{response.vendor_name} ({response.vendor_id})",
        )


class ConsoleValidationPresenter(ValidationPresenter):
    """ValidationPresenter for a console environment."""

    @classmethod
    @override
    @log_call(type="class")
    def present(cls, response: ValidationResponse) -> ValidationViewModel:
        return ValidationViewModel(
            id=response.id,
            is_valid="Valid" if response.is_valid else "Invalid",
            reasons=response.reasons,
        )
