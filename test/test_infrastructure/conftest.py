"""Pytest fixtures and utilities."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import override

from infrastructure.runner import BaseRunner

if TYPE_CHECKING:
    from test_application.conftest import DummyApplication


# ---------- General Fixtures ---------- #


# ---------- General Utilities ---------- #


@dataclass(frozen=True, slots=True)
class DummyRunner(BaseRunner):
    """Dummy runner class, implementing Clean Architecture patterns."""

    application: DummyApplication
    _is_running: list[bool] = field(default_factory=lambda: [False], init=False)

    @property
    @override
    def is_running(self) -> bool:
        return self._is_running[0]

    @override
    def start(self) -> None:
        self._is_running[0] = True

    @override
    def stop(self) -> None:
        self._is_running[0] = False


# ---------- Project Fixtures ---------- #


# ---------- Project Utilities ---------- #
