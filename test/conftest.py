"""Pytest fixtures and utilities."""

from __future__ import annotations

import logging.config
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import TypedDict
from typing import overload
from typing import override

import pytest

from _ca.domain import ErrorMsg
from application.dto import SoundDeviceResponse
from application.use_case import GetSoundDevicesUseCase
from domain.entity import SoundDevice
from domain.exception import SoundDeviceProviderError
from domain.service import SoundDeviceProvider
from infrastructure.app import HeadphoneAutoSwitcherApplication
from interface.controller import SoundDeviceController
from interface.presenter import SoundDevicePresenter
from interface.view_model import SoundDeviceViewModel

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Generator
    from collections.abc import Iterable
    from collections.abc import Sequence
    from pathlib import Path
    from uuid import UUID

    from _pytest.mark import ParameterSet
    from _pytest.mark import _HiddenParam


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
def project_src_path(project_root_path: Path) -> Path:
    """Project source path fixture."""
    return project_root_path / "src"


@pytest.fixture
def project_test_path(project_root_path: Path) -> Path:
    """Project test source path fixture."""
    return project_root_path / "test"


@pytest.fixture
def change_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Change working directory to tmp_path fixture."""
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def unfreeze_monkeypatch(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    """Unfreeze objects fixture."""
    # This is a hack to be able to set attributes on a frozen dataclass
    monkeypatch.setattr("builtins.setattr", object.__setattr__)
    return monkeypatch


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


# ---------- Project Domain ---------- #


DUMMY_SOUND_DEVICE_PROVIDER_ERROR: ErrorMsg = ErrorMsg("Dummy SoundDeviceProvider error.")


@dataclass(frozen=True, slots=True)
class DummySoundDeviceProvider(SoundDeviceProvider):
    """Dummy SoundDeviceProvider."""

    devices: list[SoundDevice]
    should_raise: bool = False

    @override
    def find(self, device_id: UUID) -> SoundDevice | None:
        self._raise()
        device: SoundDevice
        for device in self.devices:
            if device.id == device_id:
                return device
        return None

    @override
    def find_all(self) -> list[SoundDevice]:
        self._raise()
        return self.devices

    def _raise(self) -> None:
        """Raise the SoundDeviceProviderError if configured to do so."""
        if self.should_raise:
            raise SoundDeviceProviderError(DUMMY_SOUND_DEVICE_PROVIDER_ERROR)


@pytest.fixture
def sound_devices() -> list[SoundDevice]:
    """SoundDevices fixture."""
    return [SoundDevice(type="type", name=f"name{i}", default="default") for i in range(3)]


@pytest.fixture
def sound_device_provider_should_raise() -> bool:
    """SoundDeviceProvider should_raise fixture."""
    return False


@pytest.fixture
def sound_volume_view(
    sound_devices: list[SoundDevice],
    sound_device_provider_should_raise: bool,
) -> SoundDeviceProvider:
    """SoundDeviceProvider fixture."""
    return DummySoundDeviceProvider(
        devices=sound_devices,
        should_raise=sound_device_provider_should_raise,
    )


# ---------- Project Application ---------- #


@pytest.fixture
def sound_device_responses(sound_devices: list[SoundDevice]) -> list[SoundDeviceResponse]:
    """SoundDevices fixture."""
    return [SoundDeviceResponse.from_entity(entity) for entity in sound_devices]


@pytest.fixture
def get_sound_devices_use_case(sound_volume_view: SoundDeviceProvider) -> GetSoundDevicesUseCase:
    """GetSoundDevicesUseCase fixture."""
    return GetSoundDevicesUseCase(
        sound_device_provider=sound_volume_view,
    )


# ---------- Project Interface ---------- #


@dataclass(frozen=True, slots=True)
class DummySoundDevicePresenter(SoundDevicePresenter):
    """Dummy SoundDevicePresenter."""

    @override
    def present_sound_device(self, response: SoundDeviceResponse) -> SoundDeviceViewModel:
        return SoundDeviceViewModel(
            id=response.id,
            type=response.type,
            name=response.name,
            default=response.default,
        )


@pytest.fixture
def sound_device_presenter() -> SoundDevicePresenter:
    """SoundDeviceProvider fixture."""
    return DummySoundDevicePresenter()


@pytest.fixture
def sound_device_controller(
    get_sound_devices_use_case: GetSoundDevicesUseCase,
    sound_device_presenter: SoundDevicePresenter,
) -> SoundDeviceController:
    """SoundDeviceController fixture."""
    return SoundDeviceController(
        get_sound_devices_use_case=get_sound_devices_use_case,
        sound_device_presenter=sound_device_presenter,
    )


# ---------- Project Infrastructure ---------- #


@pytest.fixture
def app_name() -> str:
    """Application name fixture."""
    return "NAME"


@pytest.fixture
def app_description() -> str:
    """Application description fixture."""
    return "DESCRIPTION"


@pytest.fixture
def app_version() -> str:
    """Application version fixture."""
    return "0.0.0"


@pytest.fixture
def application(
    app_name: str,
    app_description: str,
    app_version: str,
    sound_volume_view: SoundDeviceProvider,
    sound_device_presenter: SoundDevicePresenter,
) -> HeadphoneAutoSwitcherApplication:
    """Application fixture."""
    return HeadphoneAutoSwitcherApplication(
        name=app_name,
        description=app_description,
        version=app_version,
        sound_device_provider=sound_volume_view,
        sound_device_presenter=sound_device_presenter,
    )
