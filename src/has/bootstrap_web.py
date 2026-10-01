"""Headphone Auto Switcher web bootstrap module."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from typing import Any
from typing import Never

if TYPE_CHECKING:
    from logging import Logger

    from ca.infrastructure import BaseFramework
    from ca.infrastructure import CommandFramework
    from ca.infrastructure import FrameworkResult

    from has.infrastructure.application import HASApplication

logger: Logger = logging.getLogger("has.bootstrap_web")


def web_framework() -> CommandFramework[HASApplication]:
    """Create the WEB Framework."""
    raise NotImplementedError


def web_framework_run(*args: Any) -> FrameworkResult:
    """Run the WEB Framework."""
    framework: BaseFramework = web_framework()
    return framework.run(*args)


def web_framework_main() -> Never:
    """Main entry point for the WEB Framework."""
    framework: BaseFramework = web_framework()
    framework.main()


if __name__ == "__main__":
    from multiprocessing import freeze_support

    freeze_support()
    web_framework_main()
