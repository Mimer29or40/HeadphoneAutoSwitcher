"""Headphone Auto Switcher command line interface presentation module."""

from __future__ import annotations

import inspect
import logging.config
import sys
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

from ca.application import BaseApplicationContainer
from ca.application import BaseApplicationFactory
from ca.presentation import FRAMEWORK_FAILURE
from ca.presentation import FRAMEWORK_SUCCESS
from ca.presentation import BaseFramework
from ca.presentation import FrameworkResult
from ca.presentation import LogConfigProvider
from ca.presentation import configure_logging
from ca.utils import Result

if TYPE_CHECKING:
    from collections.abc import Collection
    from collections.abc import Iterable
    from logging import Logger
    from types import MethodType

logger: Logger = logging.getLogger(__name__)


DEFAULT_CONSOLE_LOG_FORMAT: dict[str, Any] = {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}


@dataclass(frozen=True, slots=True)
class ConsoleLogConfigProvider(LogConfigProvider):
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


class BaseClickFramework[A: BaseApplicationContainer](BaseFramework[A], ABC):
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
        # TODO(Ryan): Command to track time between heartbeats
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
            log_config_provider: LogConfigProvider = ConsoleLogConfigProvider(level=log_level)
            configure_logging(log_config_provider)

            logger.debug("Application run with args: %s", ctx.args)

            # Create application container
            ctx.ensure_object(dict)
            ctx.obj["container"] = self.app_factory.create()

            if ctx.invoked_subcommand is None:
                container: BaseApplicationContainer = ctx.obj["container"]
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


class HASApplicationContainer(BaseApplicationContainer):
    """Headphone Auto Switcher application container."""


@dataclass(frozen=True, slots=True)
class HASApplicationFactory(BaseApplicationFactory):
    """Headphone Auto Switcher application information."""

    name: str = "Headphone Auto Switcher"
    description: str = "Automatically switches the sound device to/from configured Headphones when powered on/off."
    version: str = "3.0.0a1"

    @override
    def create(self) -> HASApplicationContainer:
        return HASApplicationContainer()


@dataclass(frozen=True, slots=True)
class HASClickFramework(BaseClickFramework[HASApplicationContainer]):
    """Headphone Auto Switcher click framework."""

    app_factory: HASApplicationFactory

    @override
    def command_default(self, app: HASApplicationContainer) -> FrameworkResult:
        return self.command_shell(app)

    # noinspection method-may-be-static
    def command_shell(self, app: HASApplicationContainer) -> FrameworkResult:  # noqa: ARG002
        """Drop into an interactive shell."""
        logger.warning("Not implemented.")
        return FRAMEWORK_FAILURE

    # noinspection method-may-be-static
    def command_sound(self, app: HASApplicationContainer) -> FrameworkResult:  # noqa: ARG002
        """Run the sound command."""
        result: Result[list[SoundDeviceViewModel], ErrorViewModel] = (
            app.sound_device_controller.handle_get_sound_devices()
        )

        if Result.is_ok(result):
            devices: list[SoundDeviceViewModel] = result.value

            table: list[list[str]] = [["Name", "Type", "Selected"]]
            table.extend(sorted([[d.name, d.type, d.selected] for d in devices]))

            self._output_table(table)

            return 0

        if Result.is_err(result):
            error_vm: ErrorViewModel = result.value
            logger.error(error_vm)
            return 1

        assert_never(result)  # ty:ignore[type-assertion-failure]

        logger.warning("Not implemented.")
        return FRAMEWORK_FAILURE

    # noinspection method-may-be-static
    def command_usb(self, app: HASApplicationContainer) -> FrameworkResult:  # noqa: ARG002
        """Run the usb command."""
        result: Result[list[UsbDeviceViewModel], ErrorViewModel] = app.usb_device_controller.handle_get_usb_devices()

        if Result.is_ok(result):
            devices: list[UsbDeviceViewModel] = result.value

            table: list[list[str]] = [["Vendor", "Product", "Version", "Serial Number"]]
            table.extend(sorted([[d.vendor, d.product, d.version_number, d.serial_number] for d in devices]))

            self._output_table(table)

            return FRAMEWORK_SUCCESS

        if Result.is_err(result):
            error_vm: ErrorViewModel = result.value
            logger.error(error_vm)
            return FRAMEWORK_FAILURE

        assert_never(result)  # ty:ignore[type-assertion-failure]

    # noinspection method-may-be-static
    def command_validate(self, app: HASApplicationContainer) -> FrameworkResult:  # noqa: ARG002
        """Run the validate command."""
        # try:
        #     app.validate_configuration.execute()
        # except ConfigurationError as e:
        #     raise click.ClickException(f"Configuration errors: {e}") from e
        # except UnsupportedHeadphonesError as e:
        #     raise click.ClickException(f"Unsupported headphones: {e}") from e
        # except NoDevicesFoundError as e:
        #     raise click.ClickException(str(e)) from e
        # click.echo("Configuration valid")

        logger.warning("Not implemented.")
        return FRAMEWORK_FAILURE

    # noinspection method-may-be-static
    def command_listen(self, app: HASApplicationContainer) -> FrameworkResult:  # noqa: ARG002
        """Run the listen command."""
        # try:
        #     app.listen_to_device.execute(lambda d: click.echo(f"{d.received_at}: {d.packet}"))
        # except KeyboardInterrupt:
        #     click.echo("Stopped.", err=True)

        logger.warning("Not implemented.")
        return FRAMEWORK_FAILURE

    # noinspection method-may-be-static
    def command_run(self, app: HASApplicationContainer) -> FrameworkResult:  # noqa: ARG002
        """Run the run command."""
        # switcher = app.auto_switchers.create()
        # try:
        #     switcher.execute()
        # except KeyboardInterrupt:
        #     switcher.stop()

        logger.warning("Not implemented.")
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
    # app: HeadphoneAutoSwitcherApplication = HeadphoneAutoSwitcherApplication(
    #     sound_device_provider=sound_device_provider,
    #     sound_device_presenter=sound_device_presenter,
    #     usb_device_provider=usb_device_provider,
    #     usb_device_listener=usb_device_listener,
    #     usb_device_presenter=usb_device_presenter,
    # )
    #
    # framework: ClickFramework = ClickFramework(app)

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
