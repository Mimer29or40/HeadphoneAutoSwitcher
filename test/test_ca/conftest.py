"""Pytest fixtures and utilities."""

from __future__ import annotations

import logging.config
from typing import TYPE_CHECKING
from typing import Any
from uuid import UUID
from uuid import uuid4

import pytest

from ca.domain import ApplicationError
from ca.domain import ControllerError
from ca.domain import ErrorMsg
from ca.domain import UseCaseError
from ca.utils import TRACE
from test_ca._dummy import DummyApplication
from test_ca._dummy import DummyApplicationFactory
from test_ca._dummy import DummyController
from test_ca._dummy import DummyEntity
from test_ca._dummy import DummyEntityPresenter
from test_ca._dummy import DummyEntityResponse
from test_ca._dummy import DummyEntityViewModel
from test_ca._dummy import DummyFramework
from test_ca._dummy import DummyLogConfigProvider
from test_ca._dummy import DummyPort
from test_ca._dummy import DummyRepository
from test_ca._dummy import DummyRequest
from test_ca._dummy import DummyRequestDict
from test_ca._dummy import DummyService
from test_ca._dummy import DummyUseCase
from test_ca._dummy import DummyValue

if TYPE_CHECKING:
    from collections.abc import Generator

    from ca.domain import FrameworkError
    from ca.domain import RepositoryError
    from ca.domain import ServiceError


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
def call_log_level() -> int:
    """call_log level fixture."""
    return TRACE


@pytest.fixture
def call_log(monkeypatch: pytest.MonkeyPatch, call_log_level: int) -> int:
    """call_log fixture."""
    monkeypatch.setattr("ca.utils.LOG_CALL_DEFAULT_LEVEL", call_log_level)

    return call_log_level


@pytest.fixture
def dummy_uuid() -> UUID:
    """UUID fixture."""
    return uuid4()


# -------------------- Domain -------------------- #


# ---------- Value ---------- #


@pytest.fixture
def dummy_value_obj() -> Any:
    """DummyValue obj fixture."""
    return "dummy_value_obj"


@pytest.fixture
def dummy_value(dummy_value_obj: Any) -> DummyValue:
    """DummyValue fixture."""
    return DummyValue(obj=dummy_value_obj)


# ---------- Entity ---------- #


@pytest.fixture
def dummy_entity_value() -> DummyValue:
    """DummyEntity value fixture."""
    return DummyValue(obj="dummy_value_obj")


@pytest.fixture
def dummy_entity(dummy_entity_value: DummyValue) -> DummyEntity:
    """DummyEntity fixture."""
    return DummyEntity(value=dummy_entity_value)


# ---------- Error ---------- #


@pytest.fixture
def dummy_error_message() -> ErrorMsg:
    """ErrorMsg fixture."""
    return ErrorMsg("Dummy error message.")


# ---------- Service ---------- #


@pytest.fixture
def dummy_service_error_cls() -> type[ServiceError] | None:
    """DummyService error_cls fixture."""
    return None


@pytest.fixture
def dummy_service(dummy_service_error_cls: type[ServiceError] | None) -> DummyService:
    """DummyService fixture."""
    return DummyService(error_cls=dummy_service_error_cls)


# ---------- Repository ---------- #


@pytest.fixture
def dummy_repository_entities() -> list[DummyEntity]:
    """DummyRepository entities fixture."""
    return []


@pytest.fixture
def dummy_repository_error_cls() -> type[RepositoryError] | None:
    """DummyRepository error_cls fixture."""
    return None


@pytest.fixture
def dummy_repository(
    dummy_repository_entities: list[DummyEntity],
    dummy_repository_error_cls: type[RepositoryError] | None,
) -> DummyRepository:
    """DummyRepository fixture."""
    return DummyRepository(
        entities={e.id: e for e in dummy_repository_entities},
        error_cls=dummy_repository_error_cls,
    )


# -------------------- Application -------------------- #


# ---------- Application ---------- #


@pytest.fixture
def dummy_application(dummy_application_factory: DummyApplicationFactory) -> DummyApplication:
    """DummyApplication fixture."""
    return dummy_application_factory.create()


@pytest.fixture
def dummy_application_factory_service(dummy_service: DummyService) -> DummyService | None:
    """DummyApplicationFactory service fixture."""
    return dummy_service


@pytest.fixture
def dummy_application_factory_repository() -> DummyRepository | None:
    """DummyApplicationFactory repository fixture."""
    return None


@pytest.fixture
def dummy_application_factory_presenter(dummy_entity_presenter: DummyEntityPresenter) -> DummyEntityPresenter:
    """DummyApplicationFactory presenter fixture."""
    return dummy_entity_presenter


@pytest.fixture
def dummy_application_factory_error_cls() -> type[ApplicationError] | None:
    """DummyApplicationFactory error_cls fixture."""
    return None


@pytest.fixture
def dummy_application_factory(
    dummy_application_factory_service: DummyService | None,
    dummy_application_factory_repository: DummyRepository | None,
    dummy_application_factory_presenter: DummyEntityPresenter,
) -> DummyApplicationFactory:
    """DummyApplicationFactory fixture."""
    return DummyApplicationFactory(
        service=dummy_application_factory_service,
        repository=dummy_application_factory_repository,
        presenter=dummy_application_factory_presenter,
    )


# ---------- Data Transfer Object (DTO) ---------- #


@pytest.fixture
def dummy_request_dict() -> DummyRequestDict:
    """DummyRequestDict fixture."""
    return DummyRequestDict()


@pytest.fixture
def dummy_request_obj() -> Any:
    """DummyRequest obj fixture."""
    return "obj"


@pytest.fixture
def dummy_request(dummy_request_obj: Any) -> DummyRequest:
    """DummyRequest fixture."""
    return DummyRequest(obj=dummy_request_obj)


@pytest.fixture
def dummy_entity_response_value() -> str:
    """DummyEntityResponse value fixture."""
    return "obj"


@pytest.fixture
def dummy_entity_response(dummy_entity_response_value: str) -> DummyEntityResponse:
    """DummyEntityResponse fixture."""
    return DummyEntityResponse(value=dummy_entity_response_value)


# ---------- Port ---------- #


@pytest.fixture
def dummy_port() -> DummyPort:
    """DummyPort fixture."""
    return DummyPort()


# ---------- Use Case ---------- #


@pytest.fixture
def dummy_use_case_error_cls() -> type[UseCaseError] | None:
    """DummyUseCase error_cls fixture."""
    return None


@pytest.fixture
def dummy_use_case(dummy_use_case_error_cls: type[UseCaseError] | None = None) -> DummyUseCase:
    """DummyUseCase fixture."""
    return DummyUseCase(
        error_cls=dummy_use_case_error_cls,
    )


# -------------------- Interface -------------------- #


# ---------- ViewModel ---------- #


@pytest.fixture
def dummy_entity_view_model_value() -> str:
    """DummyEntityViewModel value fixture."""
    return "obj"


@pytest.fixture
def dummy_entity_view_model(dummy_entity_view_model_value: str) -> DummyEntityViewModel:
    """DummyEntityViewModel fixture."""
    return DummyEntityViewModel(
        value=dummy_entity_view_model_value,
    )


# ---------- Presenter ---------- #


@pytest.fixture
def dummy_entity_presenter_error_cls() -> type[UseCaseError] | None:
    """DummyEntityPresenter error_cls fixture."""
    return None


@pytest.fixture
def dummy_entity_presenter(dummy_entity_presenter_error_cls: type[UseCaseError] | None = None) -> DummyEntityPresenter:
    """DummyEntityPresenter fixture."""
    return DummyEntityPresenter(
        error_cls=dummy_entity_presenter_error_cls,
    )


# ---------- Controller ---------- #


@pytest.fixture
def dummy_controller_use_case(dummy_use_case: DummyUseCase) -> DummyUseCase:
    """DummyFramework use_case fixture."""
    return dummy_use_case


@pytest.fixture
def dummy_controller_presenter(dummy_entity_presenter: DummyEntityPresenter) -> DummyEntityPresenter:
    """DummyFramework presenter fixture."""
    return dummy_entity_presenter


@pytest.fixture
def dummy_controller_error_cls() -> type[ControllerError] | None:
    """DummyController error_cls fixture."""
    return None


@pytest.fixture
def dummy_controller(
    dummy_controller_use_case: DummyUseCase,
    dummy_controller_presenter: DummyEntityPresenter,
    dummy_controller_error_cls: type[ControllerError] | None,
) -> DummyController:
    """DummyController fixture."""
    return DummyController(
        use_case=dummy_controller_use_case,
        presenter=dummy_controller_presenter,
        error_cls=dummy_controller_error_cls,
    )


# -------------------- Infrastructure -------------------- #


# ---------- Framework ---------- #


@pytest.fixture
def dummy_framework_app_factory(dummy_application_factory: DummyApplicationFactory) -> DummyApplicationFactory:
    """DummyFramework app_factory fixture."""
    return dummy_application_factory


@pytest.fixture
def dummy_framework_obj() -> Any:
    """DummyFramework obj fixture."""
    return "obj"


@pytest.fixture
def dummy_framework_error_cls() -> type[FrameworkError] | None:
    """DummyFramework error_cls fixture."""
    return None


@pytest.fixture
def dummy_framework(
    dummy_framework_app_factory: DummyApplicationFactory,
    dummy_framework_obj: Any,
    dummy_framework_error_cls: type[FrameworkError] | None,
) -> DummyFramework:
    """DummyFramework fixture."""
    return DummyFramework(
        app_factory=dummy_framework_app_factory,
        obj=dummy_framework_obj,
        error_cls=dummy_framework_error_cls,
    )


# ---------- Logging ---------- #


@pytest.fixture
def dummy_log_config_provider_config() -> dict[str, Any]:
    """DummyLogConfigProvider config fixture."""
    return {"version": 1}


@pytest.fixture
def dummy_log_config_provider(dummy_log_config_provider_config: dict[str, Any]) -> DummyLogConfigProvider:
    """DummyLogConfigProvider fixture."""
    return DummyLogConfigProvider(
        config=dummy_log_config_provider_config,
    )
