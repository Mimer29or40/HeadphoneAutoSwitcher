"""Tests for _ca.domain."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

import pytest

from _ca.application import BaseApplication
from _ca.infrastructure import DefaultLogConfigProvider
from _ca.infrastructure import LogConfigProvider
from _ca.infrastructure import configure_logging

if TYPE_CHECKING:
    from _ca.infrastructure import BaseFramework
    from test__ca.conftest import DummyFramework


@pytest.mark.unit
class TestLogConfigProvider:
    """Tests for LogConfigProvider."""

    @pytest.fixture
    def log_config_provider(self) -> LogConfigProvider:
        """LogConfigProvider fixture."""
        return DefaultLogConfigProvider()

    def test_get(self, log_config_provider: LogConfigProvider) -> None:
        """Tests for LogConfigProvider.get()."""
        # Act
        result: dict[str, Any] = log_config_provider.get()

        # Assert
        assert isinstance(result, dict)

    def test_configure_logging(self, monkeypatch: pytest.MonkeyPatch, log_config_provider: LogConfigProvider) -> None:
        """Tests for configure_logging()."""
        # Arrange
        actual: dict[str, Any] | None = None

        def dictConfig(config: dict[str, Any]) -> None:  # noqa: N802
            nonlocal actual
            actual = config

        monkeypatch.setattr("logging.config.dictConfig", dictConfig)

        # Act
        expected: dict[str, Any] = log_config_provider.get()
        configure_logging(log_config_provider)

        # Assert
        assert actual == expected


@pytest.mark.unit
class TestBaseFramework:
    """Tests for BaseFramework."""

    def test_application(self, dummy_framework: DummyFramework) -> None:
        """Tests for BaseFramework.application."""
        # Arrange
        framework: BaseFramework = dummy_framework

        # Assert
        assert isinstance(framework.application, BaseApplication)


if __name__ == "__main__":
    pytest.main()
