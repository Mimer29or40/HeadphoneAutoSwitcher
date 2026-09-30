"""Headphone Auto Switcher click implementation."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import override

import click
from click import Choice
from click import Context
from click import Group
from click.exceptions import Abort
from click.exceptions import ClickException
from click.exceptions import Exit

from ca.application import BaseApplication
from ca.infrastructure import COMMAND_FRAMEWORK_DEFAULT_CMD
from ca.infrastructure import CommandFramework
from ca.infrastructure import CommandFrameworkCommand
from ca.infrastructure import FrameworkResult
from ca.infrastructure import LogConfigProvider
from ca.infrastructure import configure_logging

if TYPE_CHECKING:
    from logging import Logger

type RawUsbDevice = dict[str, Any]

logger: Logger = logging.getLogger("has.infrastructure.click")


CLICK_APPLICATION: str = "APPLICATION"


@dataclass(frozen=True, slots=True)
class ClickFramework[A: BaseApplication](CommandFramework[A]):
    """Framework using click."""

    @override
    def run_impl(self, *args: Any) -> FrameworkResult:
        result: FrameworkResult
        try:
            group: Group = self._create_group()
            self._add_commands(group)
            result = group.main(args, standalone_mode=False)
        except ClickException as e:
            logger.critical("Click Exception: %s", type(e).__name__, exc_info=False)
            result = e.message
        except Abort:
            logger.critical("click.Abort")
            result = "click.Abort"
        except Exit as e:
            logger.critical("click.Exit")
            result = e.exit_code
        return result

    def _create_group(self) -> Group:
        invoke_without_command: bool = COMMAND_FRAMEWORK_DEFAULT_CMD in self.commands

        @click.group(help=self.app_factory.description, invoke_without_command=invoke_without_command)
        @click.version_option(version=self.app_factory.version, prog_name=self.app_factory.name)
        @click.option(
            "--log-level",
            type=Choice(["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "SEVERE"], case_sensitive=False),
            default="WARNING",
            help="Set the console log level [default: WARNING]",
        )
        @click.pass_context
        def group(ctx: Context, log_level: str) -> FrameworkResult:
            """Main entry point."""
            from has.infrastructure.cli import CLILogConfigProvider

            # Configure logging immediately
            log_config_provider: LogConfigProvider = CLILogConfigProvider(level=log_level)
            configure_logging(log_config_provider)

            logger.debug("Application launched with args: %s", ctx.args)

            # Create application container
            ctx.ensure_object(dict)
            ctx.obj[CLICK_APPLICATION] = self.app_factory.create()

            if ctx.invoked_subcommand is None:
                app: BaseApplication = ctx.obj[CLICK_APPLICATION]
                command: CommandFrameworkCommand | None = self.commands.get(COMMAND_FRAMEWORK_DEFAULT_CMD)
                if command is None:  # pragma: no cover
                    # This should never happen because this function should not be run if no default
                    #  command is provided, invoke_without_command would be False in that case.
                    return "NO_DEFAULT_COMMAND"
                return command(app)
            return None

        return group

    def _add_commands(self, group: Group) -> None:
        command_name: str
        command: CommandFrameworkCommand
        for command_name, command in self.commands.items():

            @click.pass_context
            def wrapper(
                ctx: Context, *args: Any, __command__: CommandFrameworkCommand = command, **kwargs: Any
            ) -> FrameworkResult:
                return __command__(ctx.obj[CLICK_APPLICATION], *args, **kwargs)

            wrapper.__doc__ = command.__doc__
            group.command(name=command_name)(wrapper)
