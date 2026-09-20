"""Pytest fixtures and utilities."""

from __future__ import annotations

import logging.config
from typing import TYPE_CHECKING
from typing import Any
from typing import TypedDict
from typing import overload

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Generator
    from collections.abc import Iterable
    from collections.abc import Sequence
    from pathlib import Path

    from _pytest.mark import ParameterSet
    from _pytest.mark import _HiddenParam


# ---------- General Fixtures ---------- #


@pytest.fixture
def setup_logging() -> Generator[None]:
    """Setup log Handler for console output."""
    logging_config: dict[str, Any] = {
        "version": 1,
        "formatters": {"CONSOLE": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}},
        "handlers": {
            "CONSOLE": {
                "class": "logging.StreamHandler",
                "formatter": "CONSOLE",
                "level": "DEBUG",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {"level": "DEBUG", "handlers": ["CONSOLE"]},
    }

    logging.config.dictConfig(logging_config)

    yield

    logging.config.dictConfig({"version": 1, "root": {}})


@pytest.fixture
def project_root_path(pytestconfig: pytest.Config) -> Path:
    """Project root path fixture."""
    return pytestconfig.rootpath


@pytest.fixture
def change_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Change working directory to tmp_path fixture."""
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def unfreeze_objects(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unfreeze objects fixture."""
    # This is a hack to be able to set attributes on a frozen dataclass
    monkeypatch.setattr("builtins.setattr", object.__setattr__)


# ---------- General Utilities ---------- #


class MakeFixtureResult(TypedDict):
    """Result of make_fixture()."""

    # Copied directly from pytest.fixture()
    params: Iterable[object] | None
    ids: Sequence[object | None] | Callable[[Any], object | None] | None


def make_fixture[T](arg_name: str, /, *values: T, ids: Iterable | None = None) -> MakeFixtureResult:
    """Make pytest.fixture() parameters with pretty ids."""
    return {"params": values, "ids": [f"{arg_name}={v!r}" for v in (values if ids is None else ids)]}


class MakeParametrizeResult(TypedDict):
    """Result of make_parametrize()."""

    # Copied directly from pytest.mark.parametrize()
    argnames: str | Sequence[str]
    argvalues: Iterable[ParameterSet | Sequence[object] | object]
    ids: Iterable[None | str | float | int | bool | _HiddenParam] | Callable[[Any], object | None] | None


@overload
def make_parametrize(
    arg_names: str,
    /,
    *values: Any,
    ids: Iterable | None = None,
) -> MakeParametrizeResult: ...


@overload
def make_parametrize(
    arg_names: tuple[str],
    /,
    *values: tuple[Any],
    ids: Iterable | None = None,
) -> MakeParametrizeResult: ...


@overload
def make_parametrize(
    arg_names: tuple[str, str],
    /,
    *values: tuple[Any, Any],
    ids: Iterable | None = None,
) -> MakeParametrizeResult: ...


@overload
def make_parametrize(
    arg_names: tuple[str, str, str],
    /,
    *values: tuple[Any, Any, Any],
    ids: Iterable | None = None,
) -> MakeParametrizeResult: ...


@overload
def make_parametrize(
    arg_names: tuple[str, str, str, str],
    /,
    *values: tuple[Any, Any, Any, Any],
    ids: Iterable | None = None,
) -> MakeParametrizeResult: ...


@overload
def make_parametrize(
    arg_names: tuple[str, ...],
    /,
    *values: tuple[Any, ...],
    ids: Iterable | None = None,
) -> MakeParametrizeResult: ...


def make_parametrize(
    arg_names: str | tuple[str, ...],
    /,
    *values: Any | tuple,
    ids: Iterable | None = None,
) -> MakeParametrizeResult:
    """Make pytest.mark.parametrize() parameters with pretty ids."""
    id_list: list[str]
    if isinstance(values[0], tuple):
        id_list = [
            "-".join(f"{n}={v!r}" for n, v in zip(arg_names, v_tuple, strict=True))
            for v_tuple in (values if ids is None else ids)
        ]
    else:
        id_list = [f"{arg_names}={v!r}" for v in (values if ids is None else ids)]
    return {"argnames": arg_names, "argvalues": values, "ids": id_list}


# ---------- Project Fixtures ---------- #


# ---------- Project Utilities ---------- #
