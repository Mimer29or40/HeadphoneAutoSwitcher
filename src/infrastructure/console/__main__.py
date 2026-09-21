"""Module entry point."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from infrastructure.console import main

if TYPE_CHECKING:
    from infrastructure.console import ConsoleResult


if __name__ == "__main__":
    args: list[str] = sys.argv[1:]
    result: ConsoleResult = main(*args)
    sys.exit(result)
