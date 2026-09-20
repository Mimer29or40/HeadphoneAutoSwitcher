"""Tests for infrastructure.runner."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from test_application.conftest import DummyApplication

from application.base import BaseApplication
from test_infrastructure.conftest import DummyRunner

if TYPE_CHECKING:
    from infrastructure.runner import BaseRunner


@pytest.mark.unit
class TestBaseRunner:
    """Tests for BaseRunner."""

    @pytest.fixture
    def runner_obj(self) -> BaseRunner:
        """BaseRunner fixture."""
        application: DummyApplication = DummyApplication()

        return DummyRunner(
            application=application,
        )

    def test_application(self, runner_obj: BaseRunner) -> None:
        """Tests for BaseRunner.application."""
        assert isinstance(runner_obj.application, BaseApplication)

    def test_is_running(self, runner_obj: BaseRunner) -> None:
        """Tests for BaseRunner.is_running."""
        assert isinstance(runner_obj.is_running, bool)


# ---------- Project Specific ---------- #


if __name__ == "__main__":
    pytest.main()
