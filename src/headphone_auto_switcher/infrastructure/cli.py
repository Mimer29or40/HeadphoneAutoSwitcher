"""Headphone Auto Switcher command line interface infrastructure module."""

from __future__ import annotations

import inspect
import logging.config
from abc import ABC
from abc import abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import Never
from typing import assert_never
from typing import override

import click
from click import Abort
from click import Choice
from click import ClickException
from click import Context
from click import Group
from click.exceptions import Exit

from ca.application import BaseApplication
from ca.application import BaseApplicationFactory
from ca.infrastructure import FRAMEWORK_FAILURE
from ca.infrastructure import FRAMEWORK_SUCCESS
from ca.infrastructure import BaseFramework
from ca.infrastructure import FrameworkResult
from ca.infrastructure import LogConfigProvider
from ca.infrastructure import configure_logging
from ca.utils import Result

if TYPE_CHECKING:
    from collections.abc import Collection
    from collections.abc import Iterable
    from logging import Logger
    from types import MethodType

    from ca.presentation import ErrorViewModel
    from headphone_auto_switcher.domain.value import UsbDevicePacket
    from headphone_auto_switcher.presentation.view_model import SoundDeviceViewModel
    from headphone_auto_switcher.presentation.view_model import UsbDeviceViewModel
    from headphone_auto_switcher.presentation.view_model import ValidationResultViewModel

logger: Logger = logging.getLogger("has.infrastructure.cli")


DEFAULT_CONSOLE_LOG_FORMAT: dict[str, Any] = {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}


@dataclass(frozen=True, slots=True)
class CLILogConfigProvider(LogConfigProvider):
    """Console logging configuration."""

    level: str = "WARNING"
    format: dict[str, Any] | None = None

    @override
    def get(self) -> dict[str, Any]:
        """Get the logging configuration."""
        format: dict[str, Any] | None = self.format
        if format is None:
            format = DEFAULT_CONSOLE_LOG_FORMAT

        return {
            "version": 1,
            "incremental": False,
            "disable_existing_loggers": False,
            "formatters": {"standard": format},
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": self.level,
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {"level": self.level, "handlers": ["console"]},
        }


class BaseClickFramework[A: BaseApplication](BaseFramework[A], ABC):
    """Base click framework."""

    @override
    def run(self, *args: Any) -> FrameworkResult:
        result: FrameworkResult
        try:
            # Create and run appropriate CLI implementation
            cli: Group = self._create_commands()
            result = cli.main(args, standalone_mode=False)
        except ClickException as e:
            logger.critical("Click Exception: %s", type(e).__name__, exc_info=False)
            result = e.message
        except KeyboardInterrupt:
            logger.critical("User interrupted")
            result = "USER_INTERRUPT"
        except Abort:
            logger.critical("click.Abort")
            result = "click.Abort"
        except Exit as e:
            logger.critical("click.Exit")
            result = e.exit_code
        except Exception as e:
            logger.exception("Unhandled exception:", exc_info=e)
            result = FRAMEWORK_FAILURE
        return result

    def _create_commands(self) -> Group:
        @click.group(help=self.app_factory.description, invoke_without_command=True)
        @click.version_option(version=self.app_factory.version, prog_name=self.app_factory.name)
        @click.option(
            "--log-level",
            type=Choice(["DEBUG", "INFO", "WARNING", "ERROR", "SEVERE"], case_sensitive=False),
            default="WARNING",
            help="Set the console log level [default: WARNING]",
        )
        @click.pass_context
        def cli(ctx: Context, log_level: str) -> FrameworkResult:
            """Main CLI entry point."""
            # from infrastructure.console import ConsoleLogConfigProvider

            # Configure logging
            log_config_provider: LogConfigProvider = CLILogConfigProvider(level=log_level)
            configure_logging(log_config_provider)

            logger.debug("Application run with args: %s", ctx.args)

            # Create application container
            ctx.ensure_object(dict)
            ctx.obj["container"] = self.app_factory.create()

            if ctx.invoked_subcommand is None:
                container: BaseApplication = ctx.obj["container"]
                return self.command_default(container)
            return None

        methods: list[tuple[str, MethodType]] = inspect.getmembers(self, predicate=inspect.ismethod)
        method_name: str
        method: MethodType
        for method_name, method in methods:
            if method_name.startswith("command_") and method_name != "command_default":
                command_name: str = method_name.removeprefix("command_")

                def command_wrapper(
                    ctx: Context,
                    *args: Any,
                    __command__: MethodType = method,
                    **kwargs: Any,
                ) -> FrameworkResult:
                    app: A = ctx.obj["container"]
                    return __command__(app, *args, **kwargs)

                command_wrapper.__doc__ = method.__doc__

                cli.command(name=command_name)(click.pass_context(command_wrapper))

        return cli

    @abstractmethod
    def command_default(self, app: A) -> FrameworkResult:
        """Command to run when user supplied no command."""


class HASApplication(BaseApplication):
    """Headphone Auto Switcher application container."""

    sound_device_controller: Any
    usb_device_controller: Any
    run_controller: Any

    @override
    def __post_init__(self) -> None:
        pass


@dataclass(frozen=True, slots=True)
class HASApplicationFactory(BaseApplicationFactory):
    """Headphone Auto Switcher application information."""

    name: str = "Headphone Auto Switcher"
    description: str = "Automatically switches the sound device to/from configured Headphones when powered on/off."
    version: str = "3.0.0a1"

    @override
    def create(self) -> HASApplication:
        # # Create application with dependencies
        # from infrastructure.console import ConsoleSoundDevicePresenter
        # from infrastructure.console import ConsoleUsbDevicePresenter
        # from infrastructure.service import PyWinUsbListener
        # from infrastructure.service import PyWinUsbProvider
        # from infrastructure.service import SoundVolumeViewProvider
        #
        # # Create application with dependencies
        # sound_device_provider: SoundDeviceProvider = SoundVolumeViewProvider()
        # sound_device_presenter: SoundDevicePresenter = ConsoleSoundDevicePresenter()
        #
        # usb_device_provider: UsbDeviceProvider = PyWinUsbProvider()
        # usb_device_listener: UsbDeviceListener = PyWinUsbListener()
        # usb_device_presenter: UsbDevicePresenter = ConsoleUsbDevicePresenter()
        #
        # app: HASApplication = HASApplication(
        #     sound_device_provider=sound_device_provider,
        #     sound_device_presenter=sound_device_presenter,
        #     usb_device_provider=usb_device_provider,
        #     usb_device_listener=usb_device_listener,
        #     usb_device_presenter=usb_device_presenter,
        # )
        return HASApplication()


@dataclass(frozen=True, slots=True)
class HASClickFramework(BaseClickFramework[HASApplication]):
    """Headphone Auto Switcher click framework."""

    app_factory: HASApplicationFactory

    # TODO(Ryan): Command to track time between heartbeats

    @override
    def command_default(self, app: HASApplication) -> FrameworkResult:
        return self.command_shell(app)

    # noinspection method-may-be-static
    def command_shell(self, app: HASApplication) -> FrameworkResult:  # noqa: ARG002
        """Drop into an interactive shell."""
        logger.warning("Not implemented.")
        return FRAMEWORK_FAILURE

    def command_sound(self, app: HASApplication) -> FrameworkResult:
        """Run the sound command."""
        result: Result[list[SoundDeviceViewModel], ErrorViewModel] = (
            app.sound_device_controller.handle_get_sound_devices()
        )

        if Result.is_ok(result):
            devices: list[SoundDeviceViewModel] = result.value

            table: list[list[str]] = [["Name", "Type", "Selected"]]
            table.extend(sorted([[d.name, d.type, d.selected] for d in devices]))

            self._output_table(table)

            return FRAMEWORK_SUCCESS

        if Result.is_err(result):
            return self._handle_error(result.value)

        assert_never(result)  # ty:ignore[type-assertion-failure]

    def command_usb(self, app: HASApplication) -> FrameworkResult:
        """Run the usb command."""
        result: Result[list[UsbDeviceViewModel], ErrorViewModel] = app.usb_device_controller.handle_get_usb_devices()

        if Result.is_ok(result):
            devices: list[UsbDeviceViewModel] = result.value

            table: list[list[str]] = [["Vendor", "Product", "Version", "Serial Number"]]
            table.extend(sorted([[d.vendor, d.product, d.version_number, d.serial_number] for d in devices]))

            self._output_table(table)

            return FRAMEWORK_SUCCESS

        if Result.is_err(result):
            return self._handle_error(result.value)

        assert_never(result)  # ty:ignore[type-assertion-failure]

    def command_validate(self, app: HASApplication) -> FrameworkResult:
        """Run the validate command."""
        result: Result[ValidationResultViewModel, ErrorViewModel] = app.run_controller.handle_validate()

        if Result.is_ok(result):
            validation_result: ValidationResultViewModel = result.value

            if validation_result.is_valid:
                click.echo("Configuration is valid!")
                return FRAMEWORK_SUCCESS

            click.echo("Configuration is invalid!")
            reason: str
            for reason in validation_result.reasons:
                click.echo(f" - {reason}")
            return "VALIDATION_FAILURE"

        if Result.is_err(result):
            return self._handle_error(result.value)

        assert_never(result)  # ty:ignore[type-assertion-failure]

    def command_listen(self, app: HASApplication) -> FrameworkResult:
        """Run the listen command."""

        def receive(packet: UsbDevicePacket) -> None:
            click.echo(f"Packet received: {packet}")

        result: Result[None, ErrorViewModel] = app.run_controller.handle_listen(receive)

        if Result.is_ok(result):
            return FRAMEWORK_SUCCESS

        if Result.is_err(result):
            return self._handle_error(result.value)

        assert_never(result)  # ty:ignore[type-assertion-failure]

    def command_run(self, app: HASApplication) -> FrameworkResult:
        """Run the run command."""
        result: Result[None, ErrorViewModel] = app.run_controller.handle_run()

        if Result.is_ok(result):
            return FRAMEWORK_SUCCESS

        if Result.is_err(result):
            return self._handle_error(result.value)

        assert_never(result)  # ty:ignore[type-assertion-failure]

    @staticmethod
    def _handle_error(error_vm: ErrorViewModel) -> FrameworkResult:
        logger.error(error_vm)
        return FRAMEWORK_FAILURE

    @staticmethod
    def _output_table(table: Collection[Collection[str]]) -> None:
        if len(table) == 0:
            return

        width_dict: dict[int, int] = defaultdict(int)
        row: Iterable[str]
        for row in table:
            col_index: int
            value: str
            for col_index, value in enumerate(row):
                width_dict[col_index] = max(width_dict[col_index], len(value))

        column_widths: list[int] = [width_dict[col_index] for col_index in sorted(width_dict.keys())]

        row_format: str = " | ".join(f"{{:>{w}}}" for w in column_widths)
        row: Iterable[str]
        for row in table:
            message: str = row_format.format(*row)
            click.echo(message)


def create_framework() -> BaseClickFramework:
    """Create the framework."""
    # Create application factory
    app_info: HASApplicationFactory = HASApplicationFactory()

    framework: BaseClickFramework = HASClickFramework(app_info)
    return framework


def run(*args: Any) -> FrameworkResult:
    """Run the framework."""
    framework: BaseFramework = create_framework()
    return framework.run(*args)


def main() -> Never:
    """Main entry point for the framework."""
    framework: BaseFramework = create_framework()
    framework.main()


if __name__ == "__main__":
    from multiprocessing import freeze_support

    freeze_support()
    main()
