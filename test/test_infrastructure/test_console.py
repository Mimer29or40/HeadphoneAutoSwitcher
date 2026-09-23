"""Tests for infrastructure.console."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

import pytest
from conftest import make_parametrize

from infrastructure.console import DEFAULT_CONSOLE_LOG_FORMAT
from infrastructure.console import ConsoleSoundDevicePresenter
from infrastructure.console import ConsoleUsbDevicePresenter

if TYPE_CHECKING:
    from application.dto import SoundDeviceResponse
    from application.dto import UsbDeviceResponse
    from infrastructure.console import ConsoleLogConfigProvider
    from interface.view_model import SoundDeviceViewModel
    from interface.view_model import UsbDeviceViewModel


class TestConsoleLogConfigProvider:
    """Tests for ConsoleLogConfigProvider."""

    class TestGet:
        """Tests for ConsoleLogConfigProvider.get()."""

        def test_level(
            self,
            console_log_config_provider_level: str,
            console_log_config_provider: ConsoleLogConfigProvider,
        ) -> None:
            """Test for ConsoleLogConfigProvider.get() for the level attribute."""
            # Act
            config: dict[str, Any] = console_log_config_provider.get()

            # Assert
            assert config["handlers"]["console"]["level"] == console_log_config_provider_level
            assert config["root"]["level"] == console_log_config_provider_level

    class TestFormat:
        """Tests for ConsoleLogConfigProvider.get() for the format attribute."""

        @pytest.mark.parametrize(**make_parametrize("console_log_config_provider_format", {"format": "%(message)s"}))
        def test_dict(
            self,
            console_log_config_provider_format: dict[str, Any] | None,
            console_log_config_provider: ConsoleLogConfigProvider,
        ) -> None:
            """Tests for ConsoleLogConfigProvider.get() for the format attribute with a dict."""
            # Act
            config: dict[str, Any] = console_log_config_provider.get()

            # Assert
            assert config["formatters"]["standard"] == console_log_config_provider_format

        def test_none(
            self,
            console_log_config_provider: ConsoleLogConfigProvider,
        ) -> None:
            """Tests for ConsoleLogConfigProvider.get() for the format attribute with None."""
            # Act
            config: dict[str, Any] = console_log_config_provider.get()

            # Assert
            assert config["formatters"]["standard"] == DEFAULT_CONSOLE_LOG_FORMAT


class TestConsoleSoundDevicePresenter:
    """Tests for ConsoleSoundDevicePresenter."""

    def test_present_sound_device(
        self,
        sound_device_responses: list[SoundDeviceResponse],
        console_sound_device_presenter: ConsoleSoundDevicePresenter,
    ) -> None:
        """Test for ConsoleSoundDevicePresenter.present_sound_device()."""
        # Arrange
        presenter: ConsoleSoundDevicePresenter = console_sound_device_presenter

        # Act
        view_models: list[SoundDeviceViewModel] = presenter.present_sound_devices(sound_device_responses)

        view_model: SoundDeviceViewModel
        response: SoundDeviceResponse
        for view_model, response in zip(view_models, sound_device_responses, strict=True):
            assert view_model.id == response.id
            assert view_model.type == response.type
            assert view_model.name == response.name
            assert view_model.selected == ("Selected" if response.selected else "")


class TestConsoleUsbDevicePresenter:
    """Tests for ConsoleUsbDevicePresenter."""

    def test_present_usb_device(
        self,
        usb_device_responses: list[UsbDeviceResponse],
        console_usb_device_presenter: ConsoleUsbDevicePresenter,
    ) -> None:
        """Test for ConsoleUsbDevicePresenter.present_usb_device()."""
        # Arrange
        presenter: ConsoleUsbDevicePresenter = console_usb_device_presenter

        # Act
        view_models: list[UsbDeviceViewModel] = presenter.present_usb_devices(usb_device_responses)

        view_model: UsbDeviceViewModel
        response: UsbDeviceResponse
        for view_model, response in zip(view_models, usb_device_responses, strict=True):
            assert view_model.id == response.id
            assert view_model.serial_number == response.serial_number
            assert view_model.vendor == f"{response.vendor_name} (0x{response.vendor_id:04X})"
            assert view_model.product == f"{response.product_name} (0x{response.product_id:04X})"
            assert view_model.version_number == str(response.version_number)


if __name__ == "__main__":
    pytest.main()
