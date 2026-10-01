"""Pytest fixtures and utilities."""

from __future__ import annotations

import logging.config
from typing import TYPE_CHECKING
from typing import Any
from typing import TypedDict
from typing import overload
from uuid import UUID
from uuid import uuid4

import pytest
from _dummy import DummyApplication
from _dummy import DummyApplicationFactory
from _dummy import DummyClickFramework
from _dummy import DummyFramework
from _dummy import DummyPyWinUsbListener
from _dummy import DummyPyWinUsbProvider

from ca.infrastructure import RESULT_SUCCESS
from ca.utils import TRACE

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Generator
    from collections.abc import Iterable
    from collections.abc import Sequence
    from pathlib import Path

    from _pytest.mark import ParameterSet
    from _pytest.mark import _HiddenParam

    from ca.application import BaseApplication
    from ca.application import BaseApplicationFactory
    from ca.infrastructure import FrameworkResult


# ------------------------------ Generic Fixtures ------------------------------ #


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


# ------------------------------ Project Fixtures ------------------------------ #


@pytest.fixture
def call_log_level() -> int:
    """call_log level fixture."""
    return TRACE


@pytest.fixture
def call_log(monkeypatch: pytest.MonkeyPatch, call_log_level: int) -> int:
    """call_log fixture."""
    monkeypatch.setattr("ca.utils.LOG_CALL_DEFAULT_LEVEL", call_log_level)

    return call_log_level


@pytest.fixture
def dummy_id() -> UUID:
    """Dummy UUID fixture."""
    return uuid4()


# -------------------- Domain -------------------- #


# ---------- Value ---------- #


# @pytest.fixture
# def dummy_value_obj() -> Any:
#     """DummyValue obj fixture."""
#     return "dummy_value_obj"
#
#
# @pytest.fixture
# def dummy_value(dummy_value_obj: Any) -> DummyValue:
#     """DummyValue fixture."""
#     return DummyValue(obj=dummy_value_obj)
#
#
# @pytest.fixture
# def dummy_values() -> list[DummyValue]:
#     """DummyValue list fixture."""
#     return [DummyValue(obj=f"dummy_value_obj{i}") for i in range(10)]


# ---------- Entity ---------- #


# @pytest.fixture
# def dummy_entity_value() -> DummyValue:
#     """DummyEntity value fixture."""
#     return DummyValue(obj="dummy_entity_obj")
#
#
# @pytest.fixture
# def dummy_entity(dummy_entity_value: DummyValue) -> DummyEntity:
#     """DummyEntity fixture."""
#     return DummyEntity(value=dummy_entity_value)
#
#
# @pytest.fixture
# def dummy_entities() -> list[DummyEntity]:
#     """DummyEntity list fixture."""
#     return [DummyEntity(value=DummyValue(obj=f"dummy_entity_obj{i}")) for i in range(10)]


# ---------- Error ---------- #


# @pytest.fixture
# def dummy_error_message() -> ErrorMsg:
#     """ErrorMsg fixture."""
#     return ErrorMsg("Dummy error message.")


# ---------- Service ---------- #

# UsbDeviceProvider


# @pytest.fixture
# def dummy_service_error_cls() -> type[ServiceError] | None:
#     """DummyService error_cls fixture."""
#     return None
#
#
# @pytest.fixture
# def dummy_service(dummy_service_error_cls: type[ServiceError] | None) -> DummyService:
#     """DummyService fixture."""
#     return DummyService(error_cls=dummy_service_error_cls)


@pytest.fixture
def dummy_usb_device_provider_exception() -> type[BaseException] | None:
    """DummyUsbDeviceProvider exception fixture."""
    return None


# TODO(Ryan): usb_device_providers fixture


# @pytest.fixture
# def dummy_usb_device_provider(
#     dummy_usb_device_provider_exception: Callable[[], BaseException] | None,
# ) -> DummyUsbDeviceProvider:
#     """DummyUsbDeviceProvider fixture."""
#     return DummyUsbDeviceProvider(
#         exception=dummy_usb_device_provider_exception,
#     )


@pytest.fixture
def dummy_pywinusb_provider_exception() -> type[BaseException] | None:
    """DummyPyWinUsbProvider exception fixture."""
    return None


@pytest.fixture
def dummy_pywinusb_provider(
    dummy_pywinusb_provider_exception: Callable[[], BaseException] | None,
) -> DummyPyWinUsbProvider:
    """DummyPyWinUsbProvider fixture."""
    return DummyPyWinUsbProvider(
        exception=dummy_pywinusb_provider_exception,
    )


@pytest.fixture
def dummy_pywinusb_listener_max_queue() -> int:
    """DummyPyWinUsbListener max_queue fixture."""
    return 100


@pytest.fixture
def dummy_pywinusb_listener_exception() -> type[BaseException] | None:
    """DummyPyWinUsbListener exception fixture."""
    return None


@pytest.fixture
def dummy_pywinusb_listener(
    dummy_pywinusb_listener_max_queue: int,
    dummy_pywinusb_listener_exception: Callable[[], BaseException] | None,
) -> DummyPyWinUsbListener:
    """DummyPyWinUsbListener fixture."""
    return DummyPyWinUsbListener(
        max_queue=dummy_pywinusb_listener_max_queue,
        exception=dummy_pywinusb_listener_exception,
    )


# ---------- Repository ---------- #


# @pytest.fixture
# def dummy_repository_entities() -> list[DummyEntity]:
#     """DummyRepository entities fixture."""
#     return []
#
#
# @pytest.fixture
# def dummy_repository_error_cls() -> type[RepositoryError] | None:
#     """DummyRepository error_cls fixture."""
#     return None
#
#
# @pytest.fixture
# def dummy_repository(
#     dummy_repository_entities: list[DummyEntity],
#     dummy_repository_error_cls: type[RepositoryError] | None,
# ) -> DummyRepository:
#     """DummyRepository fixture."""
#     return DummyRepository(
#         entities={e.id: e for e in dummy_repository_entities},
#         error_cls=dummy_repository_error_cls,
#     )


# -------------------- Application -------------------- #


# ---------- Application ---------- #


@pytest.fixture
def dummy_application_exception() -> type[BaseException] | None:
    """DummyApplication exception fixture."""
    return None


@pytest.fixture
def dummy_application(dummy_application_exception: Callable[[], BaseException] | None) -> DummyApplication:
    """DummyApplication fixture."""
    return DummyApplication(
        exception=dummy_application_exception,
    )


@pytest.fixture
def dummy_application_factory_app_cls() -> type[BaseApplication]:
    """DummyApplicationFactory app_cls fixture."""
    return DummyApplication


@pytest.fixture
def dummy_application_factory_exception() -> type[BaseException] | None:
    """DummyApplicationFactory exception fixture."""
    return None


@pytest.fixture
def dummy_application_factory(
    dummy_application_factory_app_cls: type[BaseApplication],
    dummy_application_factory_exception: type[BaseException] | None,
) -> DummyApplicationFactory:
    """DummyApplicationFactory fixture."""
    return DummyApplicationFactory(
        app_cls=dummy_application_factory_app_cls,
        exception=dummy_application_factory_exception,
    )


# ---------- Data Transfer Object (DTO) ---------- #


# @pytest.fixture
# def dummy_request_dict_obj() -> Any:
#     """DummyRequestDict obj fixture."""
#     return "dummy_request_dict_obj"
#
#
# @pytest.fixture
# def dummy_request_dict(dummy_request_dict_obj: Any) -> DummyRequestDict:
#     """DummyRequestDict fixture."""
#     return DummyRequestDict(obj=dummy_request_dict_obj)
#
#
# @pytest.fixture
# def dummy_request_obj() -> Any:
#     """DummyRequest obj fixture."""
#     return "dummy_request_obj"
#
#
# @pytest.fixture
# def dummy_request(dummy_request_obj: Any) -> DummyRequest:
#     """DummyRequest fixture."""
#     return DummyRequest(obj=dummy_request_obj)
#
#
# @pytest.fixture
# def dummy_entity_response_value() -> str:
#     """DummyEntityResponse value fixture."""
#     return "dummy_entity_response_value"
#
#
# @pytest.fixture
# def dummy_entity_response(dummy_entity_response_value: str) -> DummyEntityResponse:
#     """DummyEntityResponse fixture."""
#     return DummyEntityResponse(value=dummy_entity_response_value)
#
#
# @pytest.fixture
# def dummy_entity_responses() -> list[DummyEntity]:
#     """DummyEntityResponse list fixture."""
#     return [DummyEntity(value=DummyValue(obj=f"dummy_entity_responses{i}")) for i in range(10)]


# ---------- Port ---------- #


# @pytest.fixture
# def dummy_port() -> DummyPort:
#     """DummyPort fixture."""
#     return DummyPort()


# ---------- Use Case ---------- #


# @pytest.fixture
# def dummy_use_case_error_cls() -> type[UseCaseError] | None:
#     """DummyUseCase error_cls fixture."""
#     return None
#
#
# @pytest.fixture
# def dummy_use_case(dummy_use_case_error_cls: type[UseCaseError] | None = None) -> DummyUseCase:
#     """DummyUseCase fixture."""
#     return DummyUseCase(
#         error_cls=dummy_use_case_error_cls,
#     )


# -------------------- Interface -------------------- #


# ---------- ViewModel ---------- #


# @pytest.fixture
# def dummy_entity_view_model_value() -> str:
#     """DummyEntityViewModel value fixture."""
#     return "obj"
#
#
# @pytest.fixture
# def dummy_entity_view_model(dummy_entity_view_model_value: str) -> DummyEntityViewModel:
#     """DummyEntityViewModel fixture."""
#     return DummyEntityViewModel(
#         value=dummy_entity_view_model_value,
#     )


# ---------- Presenter ---------- #


# @pytest.fixture
# def dummy_entity_presenter_error_cls() -> type[PresenterError] | None:
#     """DummyEntityPresenter error_cls fixture."""
#     return None
#
#
# @pytest.fixture
# def dummy_entity_presenter(
#     dummy_entity_presenter_error_cls: type[PresenterError] | None = None,
# ) -> DummyEntityPresenter:
#     """DummyEntityPresenter fixture."""
#     return DummyEntityPresenter(
#         error_cls=dummy_entity_presenter_error_cls,
#     )


# ---------- Controller ---------- #


# @pytest.fixture
# def dummy_controller_use_case(dummy_use_case: DummyUseCase) -> DummyUseCase:
#     """DummyFramework use_case fixture."""
#     return dummy_use_case
#
#
# @pytest.fixture
# def dummy_controller_presenter(dummy_entity_presenter: DummyEntityPresenter) -> DummyEntityPresenter:
#     """DummyFramework presenter fixture."""
#     return dummy_entity_presenter
#
#
# @pytest.fixture
# def dummy_controller_error_cls() -> type[ControllerError] | None:
#     """DummyController error_cls fixture."""
#     return None
#
#
# @pytest.fixture
# def dummy_controller(
#     dummy_controller_use_case: DummyUseCase,
#     dummy_controller_presenter: DummyEntityPresenter,
#     dummy_controller_error_cls: type[ControllerError] | None,
# ) -> DummyController:
#     """DummyController fixture."""
#     return DummyController(
#         use_case=dummy_controller_use_case,
#         presenter=dummy_controller_presenter,
#         error_cls=dummy_controller_error_cls,
#     )


# -------------------- Infrastructure -------------------- #


# ---------- Framework ---------- #


@pytest.fixture
def dummy_framework_exception() -> type[BaseException] | None:
    """Dummy Framework.exception fixture."""
    return None


@pytest.fixture
def dummy_framework(
    dummy_framework_exception: type[BaseException] | None,
) -> DummyFramework:
    """Dummy Framework fixture."""
    return DummyFramework(
        exception=dummy_framework_exception,
    )


@pytest.fixture
def dummy_click_framework_app_factory(dummy_application_factory: DummyApplicationFactory) -> BaseApplicationFactory:
    """Dummy ClickFramework.app_factory fixture."""
    return dummy_application_factory


@pytest.fixture
def dummy_click_framework_exception() -> type[BaseException] | None:
    """Dummy ClickFramework.exception fixture."""
    return None


@pytest.fixture
def dummy_click_framework(
    dummy_click_framework_app_factory: BaseApplicationFactory,
    dummy_click_framework_exception: type[BaseException] | None,
) -> DummyClickFramework:
    """DummyClickFramework fixture."""
    return DummyClickFramework(
        app_factory=dummy_click_framework_app_factory,
        exception=dummy_click_framework_exception,
    )


@pytest.fixture
def dummy_click_framework_with_commands(dummy_click_framework: DummyClickFramework) -> DummyClickFramework:
    """Dummy ClickFramework with commands fixture."""

    def command(app: DummyApplication) -> FrameworkResult:
        _: BaseApplication = app
        return RESULT_SUCCESS

    dummy_click_framework.register_default(command)

    return dummy_click_framework


# ---------- Logging ---------- #


# @pytest.fixture
# def dummy_log_config_provider_config() -> dict[str, Any]:
#     """DummyLogConfigProvider config fixture."""
#     return {"version": 1}
#
#
# @pytest.fixture
# def dummy_log_config_provider(dummy_log_config_provider_config: dict[str, Any]) -> DummyLogConfigProvider:
#     """DummyLogConfigProvider fixture."""
#     return DummyLogConfigProvider(
#         config=dummy_log_config_provider_config,
#     )
