"""Infrastructure for command line based interactions."""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING
from typing import Any
from typing import assert_never

import click
from click import ClickException

from _ca.infrastructure import configure_logging
from _ca.utils import Result
from infrastructure.app import HeadphoneAutoSwitcherApplication
from infrastructure.console import ConsoleLogConfigProvider
from infrastructure.console import ConsoleSoundDevicePresenter
from infrastructure.service import SoundVolumeView

if TYPE_CHECKING:
    from collections.abc import Sequence
    from logging import Logger

    from _ca.infrastructure import LogConfigProvider
    from _ca.interface import ErrorViewModel
    from domain.service import SoundDeviceProvider
    from interface.presenter import SoundDevicePresenter
    from interface.view_model import SoundDeviceViewModel


logger: Logger = logging.getLogger("infrastructure.console")


type ConsoleResult = str | int | None


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


def create_cli(app: HeadphoneAutoSwitcherApplication) -> click.Group:  # TODO(Ryan): Make this a class
    """Create the CLI."""

    @click.group(help=app.description, invoke_without_command=True)
    @click.version_option(version=app.version)
    @click.option(
        "--log-level",
        type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "SEVERE"], case_sensitive=False),
        default="WARNING",
        help="Set the console log level [default: WARNING]",
    )
    @click.pass_context
    def cli(ctx: click.Context, log_level: str) -> ConsoleResult:
        """Main CLI entry point."""
        # Configure logging
        log_config_provider: LogConfigProvider = ConsoleLogConfigProvider(level=log_level)
        configure_logging(log_config_provider)
        if ctx.invoked_subcommand is None:
            logger.warning("Not implemented.")  # TODO(Ryan): Interactive shell
            return -1
        return None

    @cli.command()
    def sound() -> ConsoleResult:
        """Command 'sound'."""
        result: Result[list[SoundDeviceViewModel], ErrorViewModel] = (
            app.sound_device_controller.handle_get_sound_devices()
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

    return cli


def run(*args: Any) -> ConsoleResult:
    """Run the CLI framework."""
    result: ConsoleResult
    try:
        # Create application with dependencies
        sound_device_provider: SoundDeviceProvider = SoundVolumeView()
        sound_device_presenter: SoundDevicePresenter = ConsoleSoundDevicePresenter()

        app: HeadphoneAutoSwitcherApplication = HeadphoneAutoSwitcherApplication(
            sound_device_provider=sound_device_provider,
            sound_device_presenter=sound_device_presenter,
        )

        # Create and run appropriate CLI implementation
        cli: click.Group = create_cli(app)

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
        result = -1
    return result


def main() -> ConsoleResult:
    """Main entry point for the console application."""
    args: list[str] = sys.argv[1:]
    result: ConsoleResult = run(*args)
    sys.exit(result)


if __name__ == "__main__":
    from multiprocessing import freeze_support

    freeze_support()
    main()
