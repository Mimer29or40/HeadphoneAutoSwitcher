"""Module entry point."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from typing import Never

from infrastructure.console import main as main_func

if TYPE_CHECKING:
    from infrastructure.console import ConsoleResult


def main() -> Never:
    """Function entry point."""
    args: list[str] = sys.argv[1:]
    result: ConsoleResult = main_func(*args)
    sys.exit(result)


if __name__ == "__main__":
    main()
