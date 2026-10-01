"""Tests for ca.infrastructure._click."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING
from typing import Any

import click
import pytest
from click import ClickException
from conftest import make_parametrize

from ca.infrastructure import RESULT_SUCCESS

if TYPE_CHECKING:
    from _dummy import DummyClickFramework

    from ca.infrastructure import FrameworkResult
    from has.infrastructure._click import ClickFramework


CLICK_EXCEPTION_MESSAGE: str = "ClickException message."
CLICK_EXIT_CODE: int = 1001


class TestClickFramework:
    """Tests for ClickFramework."""

    # TODO(Ryan): Test for _create_group(). This could be covered by testing subclasses of CommandFramework
    # TODO(Ryan): Test for _add_commands(). This could be covered by testing subclasses of CommandFramework

    class TestRunImpl:
        """Tests for ClickFramework.run_impl()."""

        @pytest.mark.unit
        def test_success(self, dummy_click_framework_with_commands: DummyClickFramework) -> None:
            """Test for ClickFramework.run_impl() when the command is successful."""
            # Arrange
            framework: ClickFramework = dummy_click_framework_with_commands

            args: tuple[Any, ...] = ()

            # Act
            result: FrameworkResult = framework.run_impl(*args)

            # Assert
            assert result == RESULT_SUCCESS

        @pytest.mark.unit
        @pytest.mark.parametrize(
            **make_parametrize(
                "dummy_click_framework_exception",
                partial(ClickException, CLICK_EXCEPTION_MESSAGE),
            )
        )
        def test_click_exception(self, dummy_click_framework_with_commands: DummyClickFramework) -> None:
            """Test for ClickFramework.run_impl() when the implementation raises a ClickException."""
            # Arrange
            framework: ClickFramework = dummy_click_framework_with_commands

            args: tuple[Any, ...] = ()

            # Act
            result: FrameworkResult = framework.run_impl(*args)

            # Assert
            assert result == CLICK_EXCEPTION_MESSAGE

        @pytest.mark.unit
        @pytest.mark.parametrize(
            **make_parametrize(
                "dummy_click_framework_exception",
                click.Abort,
            )
        )
        def test_abort(self, dummy_click_framework_with_commands: DummyClickFramework) -> None:
            """Test for ClickFramework.run_impl() when the implementation raises an Abort."""
            # Arrange
            framework: ClickFramework = dummy_click_framework_with_commands

            args: tuple[Any, ...] = ()

            # Act
            result: FrameworkResult = framework.run_impl(*args)

            # Assert
            assert result == "click.Abort"

        @pytest.mark.unit
        @pytest.mark.parametrize(
            **make_parametrize(
                "dummy_click_framework_exception",
                partial(click.exceptions.Exit, CLICK_EXIT_CODE),
            )
        )
        def test_exit(self, dummy_click_framework_with_commands: DummyClickFramework) -> None:
            """Test for ClickFramework.run_impl() when the implementation raises an Exit."""
            # Arrange
            framework: ClickFramework = dummy_click_framework_with_commands

            args: tuple[Any, ...] = ()

            # Act
            result: FrameworkResult = framework.run_impl(*args)

            # Assert
            assert result == CLICK_EXIT_CODE


if __name__ == "__main__":
    pytest.main()
