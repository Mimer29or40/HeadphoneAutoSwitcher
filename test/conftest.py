"""Pytest fixtures and utilities."""

from __future__ import annotations

import itertools
import logging.config
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any
from typing import TypedDict
from typing import overload
from typing import override

import pytest

from _ca.domain import ErrorMsg
from application.dto import GetSoundDevicesRequest
from application.dto import GetUsbDevicesRequest
from application.dto import SoundDeviceResponse
from application.dto import UsbDeviceResponse
from application.use_case import GetSoundDevicesUseCase
from application.use_case import GetUsbDevicesUseCase
from domain.entity import SoundDevice
from domain.entity import UsbDevice
from domain.exception import SoundDeviceProviderError
from domain.exception import UsbDeviceProviderError
from domain.service import SoundDeviceProvider
from domain.service import UsbDeviceProvider
from domain.value import SoundDeviceType
from infrastructure.app import HeadphoneAutoSwitcherApplication
from infrastructure.console import ConsoleLogConfigProvider
from infrastructure.console import ConsoleSoundDevicePresenter
from infrastructure.console import ConsoleUsbDevicePresenter
from interface.controller import SoundDeviceController
from interface.controller import UsbDeviceController
from interface.presenter import SoundDevicePresenter
from interface.presenter import UsbDevicePresenter
from interface.view_model import SoundDeviceViewModel
from interface.view_model import UsbDeviceViewModel

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


# ---------- Domain Layer ---------- #


# ----- Entity ----- #


@pytest.fixture
def sound_device() -> SoundDevice:
    """SoundDevice fixture."""
    return SoundDevice(type=SoundDeviceType.INPUT, name="name", selected=False)


@pytest.fixture
def sound_devices() -> list[SoundDevice]:
    """SoundDevice list fixture."""
    devices: list[SoundDevice] = [
        SoundDevice(type=type, name=f"name{i}", selected=False)
        for type, i in itertools.product((SoundDeviceType.INPUT, SoundDeviceType.OUTPUT), range(5))
    ]

    for device_type in SoundDeviceType:
        device: SoundDevice | None = next((d for d in devices if d.type == device_type), None)
        if device is not None:
            device.selected = True

    return devices


@pytest.fixture
def usb_device() -> UsbDevice:
    """UsbDevice fixture."""
    return UsbDevice(
        serial_number="serial_number",
        vendor_name="vendor_name",
        vendor_id=0,
        product_name="product_name",
        product_id=1,
        version_number=3,
    )


@pytest.fixture
def usb_devices() -> list[UsbDevice]:
    """UsbDevice list fixture."""
    return [
        UsbDevice(
            serial_number="serial_number",
            vendor_name="vendor_name",
            vendor_id=0,
            product_name="product_name",
            product_id=1,
            version_number=3,
        )
    ]


# ----- Error ----- #


DUMMY_SOUND_DEVICE_PROVIDER_ERROR_MSG: ErrorMsg = ErrorMsg("Dummy SoundDeviceProvider error.")


@pytest.fixture
def dummy_sound_device_provider_error_msg() -> ErrorMsg:
    """Dummy SoundDeviceProvider ErrorMsg fixture."""
    return DUMMY_SOUND_DEVICE_PROVIDER_ERROR_MSG


DUMMY_USB_DEVICE_PROVIDER_ERROR_MSG: ErrorMsg = ErrorMsg("Dummy UsbDeviceProvider error.")


@pytest.fixture
def dummy_usb_device_provider_error_msg() -> ErrorMsg:
    """Dummy UsbDeviceProvider ErrorMsg fixture."""
    return DUMMY_USB_DEVICE_PROVIDER_ERROR_MSG


# ----- Service ----- #


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
            raise SoundDeviceProviderError(DUMMY_SOUND_DEVICE_PROVIDER_ERROR_MSG)


@pytest.fixture
def dummy_sound_device_provider_should_raise() -> bool:
    """Dummy SoundDeviceProvider should_raise fixture."""
    return False


@pytest.fixture
def dummy_sound_device_provider(
    sound_devices: list[SoundDevice],
    dummy_sound_device_provider_should_raise: bool,
) -> SoundDeviceProvider:
    """Dummy SoundDeviceProvider fixture."""
    return DummySoundDeviceProvider(
        devices=sound_devices,
        should_raise=dummy_sound_device_provider_should_raise,
    )


@dataclass(frozen=True, slots=True)
class DummyUsbDeviceProvider(UsbDeviceProvider):
    """Dummy UsbDeviceProvider."""

    devices: list[UsbDevice]
    should_raise: bool = False

    @override
    def find(self, device_id: UUID) -> UsbDevice | None:
        self._raise()
        device: UsbDevice
        for device in self.devices:
            if device.id == device_id:
                return device
        return None

    @override
    def find_all(self) -> list[UsbDevice]:
        self._raise()
        return self.devices

    def _raise(self) -> None:
        """Raise the UsbDeviceProviderError if configured to do so."""
        if self.should_raise:
            raise UsbDeviceProviderError(DUMMY_USB_DEVICE_PROVIDER_ERROR_MSG)


@pytest.fixture
def dummy_usb_device_provider_should_raise() -> bool:
    """Dummy UsbDeviceProvider should_raise fixture."""
    return False


@pytest.fixture
def dummy_usb_device_provider(
    usb_devices: list[UsbDevice],
    dummy_usb_device_provider_should_raise: bool,
) -> UsbDeviceProvider:
    """Dummy UsbDeviceProvider fixture."""
    return DummyUsbDeviceProvider(
        devices=usb_devices,
        should_raise=dummy_usb_device_provider_should_raise,
    )


# ----- Value ----- #


# ---------- Application Layer ---------- #


# ----- Application ----- #


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
    dummy_sound_device_provider: SoundDeviceProvider,
    dummy_sound_device_presenter: SoundDevicePresenter,
    dummy_usb_device_provider: UsbDeviceProvider,
    dummy_usb_device_presenter: UsbDevicePresenter,
) -> HeadphoneAutoSwitcherApplication:
    """Application fixture."""
    return HeadphoneAutoSwitcherApplication(
        name=app_name,
        description=app_description,
        version=app_version,
        sound_device_provider=dummy_sound_device_provider,
        sound_device_presenter=dummy_sound_device_presenter,
        usb_device_provider=dummy_usb_device_provider,
        usb_device_presenter=dummy_usb_device_presenter,
    )


# ----- Data Transfer Object ----- #


@pytest.fixture
def get_sound_devices_request() -> GetSoundDevicesRequest:
    """GetSoundDevicesRequest fixture."""
    return GetSoundDevicesRequest()


@pytest.fixture
def get_usb_devices_request() -> GetUsbDevicesRequest:
    """GetUsbDevicesRequest fixture."""
    return GetUsbDevicesRequest()


@pytest.fixture
def sound_device_responses(sound_devices: list[SoundDevice]) -> list[SoundDeviceResponse]:
    """SoundDevices fixture."""
    return [SoundDeviceResponse.from_entity(entity) for entity in sound_devices]


@pytest.fixture
def usb_device_responses(usb_devices: list[UsbDevice]) -> list[UsbDeviceResponse]:
    """UsbDevices fixture."""
    return [UsbDeviceResponse.from_entity(entity) for entity in usb_devices]


# ----- Port ----- #


# ----- Repository ----- #


# ----- Use Case ----- #


@pytest.fixture
def get_sound_devices_use_case(dummy_sound_device_provider: SoundDeviceProvider) -> GetSoundDevicesUseCase:
    """GetSoundDevicesUseCase fixture."""
    return GetSoundDevicesUseCase(
        sound_device_provider=dummy_sound_device_provider,
    )


@pytest.fixture
def get_usb_devices_use_case(dummy_usb_device_provider: UsbDeviceProvider) -> GetUsbDevicesUseCase:
    """GetUsbDevicesUseCase fixture."""
    return GetUsbDevicesUseCase(
        usb_device_provider=dummy_usb_device_provider,
    )


# ---------- Interface Layer ---------- #


# ----- Controller ----- #


@dataclass(frozen=True, slots=True)
class DummySoundDevicePresenter(SoundDevicePresenter):
    """Dummy SoundDevicePresenter."""

    @override
    def present_sound_device(self, response: SoundDeviceResponse) -> SoundDeviceViewModel:
        return SoundDeviceViewModel(
            id=response.id,
            type=response.type,
            name=response.name,
            selected=str(response.selected),
        )


@pytest.fixture
def dummy_sound_device_presenter() -> SoundDevicePresenter:
    """Dummy SoundDeviceProvider fixture."""
    return DummySoundDevicePresenter()


@dataclass(frozen=True, slots=True)
class DummyUsbDevicePresenter(UsbDevicePresenter):
    """Dummy UsbDevicePresenter."""

    @override
    def present_usb_device(self, response: UsbDeviceResponse) -> UsbDeviceViewModel:
        return UsbDeviceViewModel(
            id=response.id,
            serial_number=response.serial_number,
            vendor=f"{response.vendor_name} (0x{response.vendor_id:04X})",
            product=f"{response.product_name} (0x{response.product_id:04X})",
            version_number=str(response.version_number),
        )


@pytest.fixture
def dummy_usb_device_presenter() -> UsbDevicePresenter:
    """Dummy UsbDeviceProvider fixture."""
    return DummyUsbDevicePresenter()


@pytest.fixture
def sound_device_controller(
    get_sound_devices_use_case: GetSoundDevicesUseCase,
    dummy_sound_device_presenter: SoundDevicePresenter,
) -> SoundDeviceController:
    """SoundDeviceController fixture."""
    return SoundDeviceController(
        get_sound_devices_use_case=get_sound_devices_use_case,
        sound_device_presenter=dummy_sound_device_presenter,
    )


@pytest.fixture
def usb_device_controller(
    get_usb_devices_use_case: GetUsbDevicesUseCase,
    dummy_usb_device_presenter: UsbDevicePresenter,
) -> UsbDeviceController:
    """UsbDeviceController fixture."""
    return UsbDeviceController(
        get_usb_devices_use_case=get_usb_devices_use_case,
        usb_device_presenter=dummy_usb_device_presenter,
    )


# ----- Presenter ----- #


# ----- View Model ----- #


# ---------- Infrastructure Layer ---------- #


# ----- Console ----- #


@pytest.fixture
def console_log_config_provider_level() -> str:
    """ConsoleLogConfigProvider level fixture."""
    return "DEBUG"


@pytest.fixture
def console_log_config_provider_format() -> dict[str, Any] | None:
    """ConsoleLogConfigProvider format fixture."""
    return None


@pytest.fixture
def console_log_config_provider(
    console_log_config_provider_level: str,
    console_log_config_provider_format: dict[str, Any] | None,
) -> ConsoleLogConfigProvider:
    """ConsoleLogConfigProvider fixture."""
    return ConsoleLogConfigProvider(
        level=console_log_config_provider_level,
        format=console_log_config_provider_format,
    )


@pytest.fixture
def console_sound_device_presenter() -> ConsoleSoundDevicePresenter:
    """ConsoleSoundDevicePresenter fixture."""
    return ConsoleSoundDevicePresenter()


@pytest.fixture
def console_usb_device_presenter() -> ConsoleUsbDevicePresenter:
    """ConsoleUsbDevicePresenter fixture."""
    return ConsoleUsbDevicePresenter()


# ----- Framework ----- #
