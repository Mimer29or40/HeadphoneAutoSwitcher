"""Infrastructure for command line based interactions."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import assert_never
from typing import override

import click
from click import ClickException

from _ca.infrastructure import FRAMEWORK_FAILURE
from _ca.infrastructure import FRAMEWORK_SUCCESS
from _ca.infrastructure import BaseFramework
from _ca.infrastructure import FrameworkResult
from _ca.infrastructure import configure_logging
from _ca.utils import Result
from infrastructure.app import HeadphoneAutoSwitcherApplication
from infrastructure.console import ConsoleLogConfigProvider
from infrastructure.console import ConsoleSoundDevicePresenter
from infrastructure.console import ConsoleUsbDevicePresenter
from infrastructure.service import PyWinUsb
from infrastructure.service import SoundVolumeView

if TYPE_CHECKING:
    from collections.abc import Sequence
    from logging import Logger

    from _ca.infrastructure import LogConfigProvider
    from _ca.interface import ErrorViewModel
    from domain.service import SoundDeviceProvider
    from domain.service import UsbDeviceProvider
    from interface.presenter import SoundDevicePresenter
    from interface.presenter import UsbDevicePresenter
    from interface.view_model import SoundDeviceViewModel
    from interface.view_model import UsbDeviceViewModel


logger: Logger = logging.getLogger("infrastructure.cli")


@dataclass(frozen=True, slots=True)
class CLIFramework(BaseFramework):
    """Command line interface framework."""

    app: HeadphoneAutoSwitcherApplication

    @override
    def run(self, *args: Any) -> FrameworkResult:
        result: FrameworkResult
        try:
            # Create and run appropriate CLI implementation
            cli: click.Group = self._create_commands()
            result = cli(args, standalone_mode=False)
            logger.debug("Command result: %s", result)
        except ClickException as e:
            logger.critical("Click Exception: %s", type(e).__name__, exc_info=False)
            result = e.message
        except KeyboardInterrupt:
            logger.critical("User interrupted")
            result = "USER_INTERRUPT"
        except Exception as e:
            logger.exception("Unhandled exception:", exc_info=e)
            result = FRAMEWORK_FAILURE
        return result

    def _create_commands(self) -> click.Group:

        @click.group(help=self.app.description, invoke_without_command=True)
        @click.version_option(version=self.app.version)
        @click.option(
            "--log-level",
            type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "SEVERE"], case_sensitive=False),
            default="WARNING",
            help="Set the console log level [default: WARNING]",
        )
        @click.pass_context
        def cli(ctx: click.Context, log_level: str) -> FrameworkResult:
            """Main CLI entry point."""
            # Configure logging
            log_config_provider: LogConfigProvider = ConsoleLogConfigProvider(level=log_level)
            configure_logging(log_config_provider)

            if ctx.invoked_subcommand is None:
                return self.command_shell()
            return None

        @cli.command()
        def sound() -> FrameworkResult:
            """Command 'sound'."""
            return self.command_sound()

        @cli.command()
        def usb() -> FrameworkResult:
            """Command 'usb'."""
            return self.command_usb()

        @cli.command()
        def validate() -> FrameworkResult:
            """Command 'validate'."""
            return self.command_validate()

        @cli.command()
        def listen() -> FrameworkResult:
            """Command 'listen'."""
            return self.command_listen()

        @cli.command()
        def run() -> FrameworkResult:
            """Command 'run'."""
            return self.command_run()

        return cli

    # noinspection method-may-be-static
    def command_shell(self) -> FrameworkResult:  # TODO(Ryan): Interactive shell
        """Drop into an interactive shell."""
        logger.warning("Not implemented.")
        return FRAMEWORK_FAILURE

    def command_sound(self) -> FrameworkResult:
        """Run the sound command."""
        result: Result[list[SoundDeviceViewModel], ErrorViewModel] = (
            self.app.sound_device_controller.handle_get_sound_devices()
        )

        if Result.is_ok(result):
            devices: list[SoundDeviceViewModel] = result.value

            rows: list[list[str]] = [["Name", "Type", "Selected"]]
            rows.extend(sorted([[d.name, d.type, d.selected] for d in devices]))

            line: str
            for line in _make_table(rows):
                click.echo(line)

            return 0

        if Result.is_err(result):
            error_vm: ErrorViewModel = result.value
            logger.error(error_vm)
            return 1

        assert_never(result)  # ty:ignore[type-assertion-failure]

    def command_usb(self) -> FrameworkResult:
        """Run the usb command."""
        result: Result[list[UsbDeviceViewModel], ErrorViewModel] = (
            self.app.usb_device_controller.handle_get_usb_devices()
        )

        if Result.is_ok(result):
            devices: list[UsbDeviceViewModel] = result.value

            rows: list[list[str]] = [["Vendor", "Product", "Version", "Serial Number"]]
            rows.extend(sorted([[d.vendor, d.product, d.version_number, d.serial_number] for d in devices]))

            line: str
            for line in _make_table(rows):
                click.echo(line)

            return FRAMEWORK_SUCCESS

        if Result.is_err(result):
            error_vm: ErrorViewModel = result.value
            logger.error(error_vm)
            return FRAMEWORK_FAILURE

        assert_never(result)  # ty:ignore[type-assertion-failure]

    # noinspection method-may-be-static
    def command_validate(self) -> FrameworkResult:
        """Run the validate command."""
        logger.warning("Not implemented.")
        return FRAMEWORK_FAILURE

    # noinspection method-may-be-static
    def command_listen(self) -> FrameworkResult:
        """Run the listen command."""
        logger.warning("Not implemented.")
        return FRAMEWORK_FAILURE

    # noinspection method-may-be-static
    def command_run(self) -> FrameworkResult:
        """Run the run command."""
        logger.warning("Not implemented.")
        return FRAMEWORK_FAILURE


def _make_table[T: Sequence](rows: list[T]) -> list[str]:
    """Make a table with a list if rows."""
    if len(rows) == 0:
        return []

    widths: list[int] = []
    for i in range(len(rows[0])):
        width: int = 0
        for row in rows:
            width = max(width, len(row[i]))
        widths.append(width)
    format: str = " | ".join(f"{{:>{w}}}" for w in widths)

    return [format.format(*r) for r in rows]


def create_framework() -> BaseFramework:
    """Create the framework."""
    # Create application with dependencies
    sound_device_provider: SoundDeviceProvider = SoundVolumeView()
    sound_device_presenter: SoundDevicePresenter = ConsoleSoundDevicePresenter()

    usb_device_provider: UsbDeviceProvider = PyWinUsb()
    usb_device_presenter: UsbDevicePresenter = ConsoleUsbDevicePresenter()

    app: HeadphoneAutoSwitcherApplication = HeadphoneAutoSwitcherApplication(
        sound_device_provider=sound_device_provider,
        sound_device_presenter=sound_device_presenter,
        usb_device_provider=usb_device_provider,
        usb_device_presenter=usb_device_presenter,
    )

    framework: CLIFramework = CLIFramework(app)
    return framework


def run(*args: Any) -> FrameworkResult:
    """Run the framework."""
    framework: BaseFramework = create_framework()
    return framework.run(*args)


def main() -> FrameworkResult:
    """Main entry point for the framework."""
    framework: BaseFramework = create_framework()
    framework.main()


if __name__ == "__main__":
    from multiprocessing import freeze_support

    freeze_support()
    main()
