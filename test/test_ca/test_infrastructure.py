"""Tests for ca.infrastructure."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from typing import Any

import pytest
from conftest import make_parametrize

from ca.domain import FrameworkError
from ca.infrastructure import COMMAND_ALREADY_REGISTERED
from ca.infrastructure import COMMAND_FRAMEWORK_DEFAULT_CMD
from ca.infrastructure import COMMAND_NOT_REGISTERED
from ca.infrastructure import RESULT_EXCEPTION
from ca.infrastructure import RESULT_FAILURE
from ca.infrastructure import RESULT_USER_INTERRUPT
from ca.infrastructure import CommandFramework
from ca.infrastructure import configure_logging

if TYPE_CHECKING:
    from ca.infrastructure import FrameworkResult
    from ca.infrastructure import LogConfigProvider
    from test_ca._dummy import DummyFramework
    from test_ca._dummy import DummyLogConfigProvider


# ---------- Framework ---------- #


class TestBaseFramework:
    """Tests for BaseFramework."""

    class TestRun:
        """Tests for BaseFramework.run()."""

        @pytest.mark.unit
        def test_success(self, dummy_framework: DummyFramework) -> None:
            """Test for BaseFramework.run() when the implementation is successful."""
            # Arrange
            expected: str = dummy_framework.obj
            args: tuple[Any] = (expected,)

            # Act
            result: FrameworkResult = dummy_framework.run(*args)

            # Assert
            assert result == expected

        @pytest.mark.unit
        @pytest.mark.parametrize(**make_parametrize("dummy_framework_error_cls", FrameworkError))
        def test_base_error(self, dummy_framework: DummyFramework) -> None:
            """Test for BaseFramework.run() when the implementation raises a BaseError."""
            # Arrange
            args: tuple[Any] = ("obj",)

            # Act
            result: FrameworkResult = dummy_framework.run(*args)

            # Assert
            assert result == RESULT_FAILURE

        @pytest.mark.unit
        def test_keyboard_interrupt(self, dummy_framework: DummyFramework) -> None:
            """Test for BaseFramework.run() when the implementation raises a KeyboardInterrupt."""
            # Arrange
            args: tuple[Any] = ("obj",)

            # Act
            result: FrameworkResult = dummy_framework.run(*args)

            # Assert
            assert result == RESULT_USER_INTERRUPT

        @pytest.mark.unit
        def test_exception(self, dummy_framework: DummyFramework) -> None:
            """Test for BaseFramework.run() when the implementation raises an unhandled Exception."""
            # Arrange
            args: tuple[Any] = ("obj",)

            # Act
            result: FrameworkResult = dummy_framework.run(*args)

            # Assert
            assert result == RESULT_EXCEPTION

    @pytest.mark.unit
    def test_main(self, monkeypatch: pytest.MonkeyPatch, dummy_framework: DummyFramework) -> None:
        """Test for BaseFramework.main()."""
        # Arrange
        expected: str = "obj"
        argv: list[str] = [sys.argv[0], expected]
        monkeypatch.setattr("sys.argv", argv)

        # Act
        with pytest.raises(SystemExit) as exc_info:
            dummy_framework.main()

        result: FrameworkResult = exc_info.value.code

        # Assert
        assert result == expected


class TestCommandFramework:
    """Tests for CommandFramework."""

    @staticmethod
    def dummy_command(obj: Any) -> Any:
        """Dummy command."""
        return obj

    class TestRegister:
        """Tests for CommandFramework.register()."""

        @pytest.mark.unit
        def test_success(self, dummy_framework: DummyFramework) -> None:
            """Test for CommandFramework.register() when successful."""
            # Arrange
            command_framework: CommandFramework = dummy_framework

            command_name: str = "command"
            command: Any = TestCommandFramework.dummy_command

            # Act
            command_framework.register(command_name, command)

            # Assert
            assert command_name in dummy_framework.commands
            assert dummy_framework.commands.get(command_name) is command

        @pytest.mark.unit
        def test_command_already_registered(self, dummy_framework: DummyFramework) -> None:
            """Test for CommandFramework.register() when a command is already registered."""
            # Arrange
            command_framework: CommandFramework = dummy_framework

            command_name: str = "command"
            command: Any = TestCommandFramework.dummy_command
            command_framework.commands[command_name] = command

            # Act
            with pytest.raises(FrameworkError) as exc_info:
                command_framework.register(command_name, command)
            error: FrameworkError = exc_info.value

            # Assert
            assert error.message == COMMAND_ALREADY_REGISTERED

    @pytest.mark.unit
    def test_register_default(self, dummy_framework: DummyFramework) -> None:
        """Test for CommandFramework.register_default()."""
        # Arrange
        command_framework: CommandFramework = dummy_framework

        command: Any = TestCommandFramework.dummy_command

        # Act
        command_framework.register_default(command)

        # Assert
        assert COMMAND_FRAMEWORK_DEFAULT_CMD in dummy_framework.commands
        assert dummy_framework.commands.get(COMMAND_FRAMEWORK_DEFAULT_CMD) is command

    class TestUnregister:
        """Tests for CommandFramework.unregister()."""

        @pytest.mark.unit
        def test_success(self, dummy_framework: DummyFramework) -> None:
            """Test for CommandFramework.unregister() when successful."""
            # Arrange
            command_framework: CommandFramework = dummy_framework

            command_name: str = "command"
            command: Any = TestCommandFramework.dummy_command
            command_framework.commands[command_name] = command

            # Act
            command_framework.unregister(command_name)

            # Assert
            assert command_name not in dummy_framework.commands

        @pytest.mark.unit
        def test_command_not_registered(self, dummy_framework: DummyFramework) -> None:
            """Test for CommandFramework.register() when a command is not registered."""
            # Arrange
            command_framework: CommandFramework = dummy_framework

            command_name: str = "command"

            # Act
            with pytest.raises(FrameworkError) as exc_info:
                command_framework.unregister(command_name)
            error: FrameworkError = exc_info.value

            # Assert
            assert error.message == COMMAND_NOT_REGISTERED


# ---------- Logging ---------- #


class TestLogConfigProvider:
    """Tests for LogConfigProvider."""

    @pytest.mark.unit
    def test_get(self, dummy_log_config_provider: DummyLogConfigProvider) -> None:
        """Test for LogConfigProvider.get()."""
        # Arrange
        log_config_provider: LogConfigProvider = dummy_log_config_provider

        # Act
        result: dict[str, Any] = log_config_provider.get()

        # Assert
        assert isinstance(result, dict)


@pytest.mark.unit
def test_configure_logging(
    monkeypatch: pytest.MonkeyPatch,
    dummy_log_config_provider_config: dict[str, Any],
    dummy_log_config_provider: DummyLogConfigProvider,
) -> None:
    """Test for configure_logging()."""
    # Arrange
    result: dict[str, Any] | None = None

    def dictConfig(config: dict[str, Any]) -> None:  # noqa: N802
        nonlocal result
        result = config

    monkeypatch.setattr("logging.config.dictConfig", dictConfig)

    # Act
    configure_logging(dummy_log_config_provider)

    # Assert
    assert result == dummy_log_config_provider_config


if __name__ == "__main__":
    pytest.main()
