"""Headphone Auto Switcher bootstrap module."""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import TYPE_CHECKING
from typing import Any
from typing import Never
from typing import assert_never

import click

from ca.infrastructure import RESULT_FAILURE
from ca.infrastructure import RESULT_SUCCESS
from ca.infrastructure import BaseFramework
from ca.infrastructure import CommandFramework
from ca.infrastructure import FrameworkResult
from ca.utils import Result
from ca.utils import log_call

if TYPE_CHECKING:
    from collections.abc import Collection
    from logging import Logger

    from ca.interface import ErrorViewModel
    from has.domain.value import UsbDevicePacket
    from has.infrastructure.application import HASApplication
    from has.infrastructure.application import HASApplicationFactory
    from has.interface.view_model import SoundDeviceViewModel
    from has.interface.view_model import UsbDeviceViewModel
    from has.interface.view_model import ValidationViewModel

logger: Logger = logging.getLogger("has.bootstrap")


def cli_framework_main() -> Never:
    """Main entry point for the CLI Framework."""
    framework: BaseFramework = cli_framework()
    framework.main()


def cli_framework_run(*args: Any) -> FrameworkResult:
    """Run the CLI Framework."""
    framework: BaseFramework = cli_framework()
    return framework.run(*args)


def cli_framework() -> CommandFramework[HASApplication]:
    """Create the CLI Framework."""
    from has.infrastructure._click import ClickFramework
    from has.infrastructure.cli import CLIHASApplicationFactory

    # Create ApplicationFactory
    app_factory: HASApplicationFactory = CLIHASApplicationFactory()

    # Create Framework
    framework: CommandFramework[HASApplication] = ClickFramework(app_factory)

    # Register commands
    # TODO(Ryan): Command to track time between heartbeats
    framework.register_default(command_shell)
    framework.register("sound", command_sound)
    framework.register("usb", command_usb)
    framework.register("validate", command_validate)
    framework.register("listen", command_listen)
    framework.register("run", command_run)
    framework.register("shell", command_shell)

    return framework


def web_framework_main() -> Never:
    """Main entry point for the WEB Framework."""
    framework: BaseFramework = web_framework()
    framework.main()


def web_framework_run(*args: Any) -> FrameworkResult:
    """Run the WEB Framework."""
    framework: BaseFramework = web_framework()
    return framework.run(*args)


def web_framework() -> CommandFramework[HASApplication]:
    """Create the WEB Framework."""
    raise NotImplementedError


@log_call(type="static", arg_func="str")
def command_sound(app: HASApplication) -> FrameworkResult:
    """List the SoundDevices on the system."""
    result: Result[list[SoundDeviceViewModel], ErrorViewModel] = app.sound_device_controller.handle_get_sound_devices()

    if Result.is_ok(result):
        devices: list[SoundDeviceViewModel] = result.value

        table: list[list[str]] = [["Name", "Type", "Selected"]]
        table.extend(sorted([[d.name, d.type, d.selected] for d in devices]))

        _output_table(table)

        return RESULT_SUCCESS

    if Result.is_err(result):
        return _handle_error(result.value)

    assert_never(result)  # ty:ignore[type-assertion-failure]


@log_call(type="static", arg_func="str")
def command_usb(app: HASApplication) -> FrameworkResult:
    """List the UsbDevices on the system."""
    result: Result[list[UsbDeviceViewModel], ErrorViewModel] = app.usb_device_controller.handle_get_usb_devices()

    if Result.is_ok(result):
        devices: list[UsbDeviceViewModel] = result.value

        table: list[list[str]] = [["Vendor", "Product"]]
        table.extend(sorted([[d.vendor, d.product] for d in devices]))

        _output_table(table)

        return RESULT_SUCCESS

    if Result.is_err(result):
        return _handle_error(result.value)

    assert_never(result)  # ty:ignore[type-assertion-failure]


@log_call(type="static", arg_func="str")
def command_validate(app: HASApplication) -> FrameworkResult:
    """Validate the application configuration."""
    result: Result[ValidationViewModel, ErrorViewModel] = app.switcher_controller.handle_validate()

    if Result.is_ok(result):
        validation_result: ValidationViewModel = result.value

        if validation_result.is_valid:
            click.echo("Configuration is valid!")
            return RESULT_SUCCESS

        click.echo("Configuration is invalid!")
        reason: str
        for reason in validation_result.reasons:
            click.echo(f" - {reason}")
        return "VALIDATION_FAILED"

    if Result.is_err(result):
        return _handle_error(result.value)

    assert_never(result)  # ty:ignore[type-assertion-failure]


@log_call(type="static", arg_func="str")
def command_listen(app: HASApplication) -> FrameworkResult:
    """Listen to the traffic from the configured SoundDevice."""

    def receive(packet: UsbDevicePacket) -> None:
        click.echo(f"Packet received: {packet}")

    result: Result[None, ErrorViewModel] = app.switcher_controller.handle_listen(receive)

    if Result.is_ok(result):
        return RESULT_SUCCESS

    if Result.is_err(result):
        return _handle_error(result.value)

    assert_never(result)  # ty:ignore[type-assertion-failure]


@log_call(type="static", arg_func="str")
def command_run(app: HASApplication) -> FrameworkResult:
    """Run the application."""
    result: Result[None, ErrorViewModel] = app.switcher_controller.handle_run()

    if Result.is_ok(result):
        return RESULT_SUCCESS

    if Result.is_err(result):
        return _handle_error(result.value)

    assert_never(result)  # ty:ignore[type-assertion-failure]


@log_call(type="static", arg_func="str")
def command_shell(app: HASApplication) -> FrameworkResult:  # noqa: ARG001
    """Drop into an interactive application shell."""
    logger.warning("Not implemented.")
    return RESULT_FAILURE


def _handle_error(error_vm: ErrorViewModel) -> FrameworkResult:
    logger.error(error_vm)
    return RESULT_FAILURE


def _output_table(table: Collection[Collection[str]]) -> None:
    if len(table) == 0:
        return

    width_dict: dict[int, int] = defaultdict(int)
    row: Collection[str]
    for row in table:
        col_index: int
        value: str
        for col_index, value in enumerate(row):
            width_dict[col_index] = max(width_dict[col_index], len(value))

    column_widths: list[int] = [width_dict[col_index] for col_index in sorted(width_dict.keys())]

    row_format: str = " | ".join(f"{{:>{w}}}" for w in column_widths)
    row: Collection[str]
    for row in table:
        message: str = row_format.format(*row)
        click.echo(message)
