"""Pytest fixtures and utilities."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from typing import Self
from typing import assert_never
from typing import override

import pytest

from _ca.application import BaseApplication
from _ca.application import BaseOutcome
from _ca.application import BasePort
from _ca.application import BaseRepository
from _ca.application import BaseRequest
from _ca.application import BaseResponse
from _ca.application import BaseUseCase
from _ca.domain import BaseEntity
from _ca.domain import BaseError
from _ca.domain import BaseService
from _ca.domain import BaseValue
from _ca.domain import ErrorMsg
from _ca.infrastructure import BaseFramework
from _ca.interface import BaseController
from _ca.interface import BasePresenter
from _ca.interface import BaseViewModel
from _ca.interface import ErrorViewModel
from _ca.utils import Result

if TYPE_CHECKING:
    pass


# ---------- Domain Layer ---------- #


# ----- Entity ----- #


@dataclass(eq=False)
class DummyEntity(BaseEntity):
    """Dummy value."""

    value: Any


@pytest.fixture
def dummy_entity_value() -> Any:
    """DummyEntity value fixture."""
    return "entity"


@pytest.fixture
def dummy_entity(dummy_entity_value: Any) -> DummyEntity:
    """DummyEntity fixture."""
    return DummyEntity(dummy_entity_value)


@pytest.fixture
def dummy_entities(dummy_entity: DummyEntity) -> list[DummyEntity]:
    """DummyEntities fixture."""
    return [dummy_entity] + [DummyEntity(value=f"entity{i}") for i in range(3)]


# ----- Exception ----- #


class DummyError(BaseError):
    """Dummy Error."""


@pytest.fixture
def dummy_error(dummy_error_msg: ErrorMsg) -> DummyError:
    """DummyError fixture."""
    return DummyError(dummy_error_msg)


DUMMY_ERROR_MSG: ErrorMsg = ErrorMsg("Dummy error.")


@pytest.fixture
def dummy_error_msg() -> ErrorMsg:
    """DummyRepository fixture."""
    return DUMMY_ERROR_MSG


# ----- Service ----- #


@dataclass(frozen=True, slots=True)
class DummyService(BaseService):
    """Dummy Service."""

    should_raise: bool = False

    def convert_entity_to_value(self, entity: DummyEntity) -> DummyValue:
        """Convert entity to value."""
        if self.should_raise:
            raise DummyError(DUMMY_ERROR_MSG)
        return DummyValue(entity.value)

    def convert_value_to_entity(self, value: DummyValue) -> DummyEntity:
        """Convert value to entity."""
        if self.should_raise:
            raise DummyError(DUMMY_ERROR_MSG)
        return DummyEntity(value.value)


@pytest.fixture
def dummy_service_should_raise() -> bool:
    """DummyService should_raise fixture."""
    return False


@pytest.fixture
def dummy_service(dummy_service_should_raise: bool) -> BaseService:
    """Service fixture."""
    return DummyService(
        should_raise=dummy_service_should_raise,
    )


# ----- Value ----- #


@dataclass(frozen=True, slots=True)
class DummyValue(BaseValue):
    """Dummy Value."""

    value: Any


@pytest.fixture
def dummy_value_value() -> Any:
    """DummyValue value fixture."""
    return "value"


@pytest.fixture
def dummy_value(dummy_value_value: Any) -> DummyValue:
    """DummyValue fixture."""
    return DummyValue(dummy_value_value)


@pytest.fixture
def dummy_values(dummy_value: DummyValue) -> list[DummyValue]:
    """DummyValues fixture."""
    return [dummy_value] + [DummyValue(value=f"value{i}") for i in range(3)]


# ---------- Application Layer ---------- #


# ----- Application ----- #


@dataclass(frozen=True, slots=True)
class DummyApplication(BaseApplication):
    """Dummy application."""

    name: str = "Dummy Application"
    description: str = "Dummy Application."
    version: str = "0.0.0"


@pytest.fixture
def dummy_application() -> DummyApplication:
    """DummyApplication values fixture."""
    return DummyApplication()


# ----- Data Transfer Object ----- #


@dataclass(frozen=True, slots=True)
class DummyRequest(BaseRequest):
    """Dummy request."""

    value: Any

    @override
    def __post_init__(self) -> None:
        if self.value is None:
            raise ValueError("Data must not be None.")

    @override
    def convert(self) -> dict[str, Any]:
        return {"data": str(self.value)}


@pytest.fixture
def dummy_request_value() -> Any:
    """DummyRequest value fixture."""
    return "request"


@pytest.fixture
def dummy_request(dummy_request_value: Any) -> DummyRequest:
    """DummyRequest fixture."""
    return DummyRequest(dummy_request_value)


@dataclass(frozen=True, slots=True)
class DummyResponse(BaseResponse):
    """Dummy response."""

    value: str

    @classmethod
    def from_entity(cls, entity: DummyEntity) -> Self:
        """Create a Response from an Entity."""
        return cls(value=str(entity.value))


@pytest.fixture
def dummy_response_value() -> Any:
    """DummyResponse value fixture."""
    return "response"


@pytest.fixture
def dummy_response(dummy_response_value: Any) -> DummyResponse:
    """DummyResponse fixture."""
    return DummyResponse(dummy_response_value)


@dataclass(frozen=True, slots=True)
class DummyOutcome(BaseOutcome):
    """Dummy outcome."""

    value: Any

    def __str__(self) -> str:
        """Convert the outcome into a human-readable string."""
        return str(self.value)


@pytest.fixture
def dummy_outcome_value() -> Any:
    """DummyOutcome value fixture."""
    return "outcome"


@pytest.fixture
def dummy_outcome(dummy_outcome_value: Any) -> DummyOutcome:
    """DummyOutcome fixture."""
    return DummyOutcome(dummy_outcome_value)


# ----- Port ----- #


@dataclass(frozen=True, slots=True)
class DummyPort(BasePort):
    """Dummy rort."""

    notifications: list[Any] = field(default_factory=list, init=False)

    def notify(self, value: Any) -> None:
        """Notify something."""
        self.notifications.append(value)


@pytest.fixture
def dummy_port() -> DummyPort:
    """DummyPort fixture."""
    return DummyPort()


# ----- Repository ----- #


@dataclass(frozen=True, slots=True)
class DummyRepository(BaseRepository):
    """Dummy repository."""

    values: list[Any]

    def get(self, index: int) -> Any:
        """Get something from a repository."""
        return self.values[index]


@pytest.fixture
def dummy_repository_values() -> list[Any]:
    """DummyRepository values fixture."""
    return [0, True, "two", 3.0]


@pytest.fixture
def dummy_repository(dummy_repository_values: list[Any]) -> DummyRepository:
    """DummyRepository fixture."""
    return DummyRepository(dummy_repository_values)


# ----- Use Case ----- #


@dataclass(frozen=True, slots=True)
class DummyUseCase(BaseUseCase):
    """Dummy use case."""

    optional_service_name: ClassVar[str] = "optional_service"
    optional_service: ClassVar[object] = object()

    service: DummyService
    port: DummyPort
    repository: DummyRepository

    response: DummyResponse | DummyOutcome
    error_msg: ErrorMsg

    @override
    def execute(self, request: DummyRequest) -> Result[DummyResponse | DummyOutcome, ErrorMsg]:
        should_succeed: bool = request.value

        optional_service: object | None = self._optional_services.get(DummyUseCase.optional_service_name)
        if optional_service is not None:
            should_succeed = not should_succeed

        if should_succeed:
            return Result.ok(self.response)
        return Result.err(self.error_msg)


@pytest.fixture
def dummy_use_case(
    dummy_service: DummyService,
    dummy_port: DummyPort,
    dummy_repository: DummyRepository,
    dummy_response: DummyResponse | DummyOutcome,
    dummy_error_msg: ErrorMsg,
) -> DummyUseCase:
    """DummyUseCase fixture."""
    return DummyUseCase(
        service=dummy_service,
        port=dummy_port,
        repository=dummy_repository,
        response=dummy_response,
        error_msg=dummy_error_msg,
    )


# ---------- Interface Layer ---------- #


# ----- Controller ----- #


@dataclass(frozen=True, slots=True)
class DummyController(BaseController):
    """Dummy controller."""

    dummy_use_case: DummyUseCase
    dummy_presenter: DummyPresenter

    def handle_use_case(self, value: Any) -> Result[DummyViewModel, ErrorViewModel]:
        """Handle Dummy UseCase."""
        try:
            request: DummyRequest = DummyRequest(value=value)
            result: Result[DummyResponse | DummyOutcome, ErrorMsg] = self.dummy_use_case.execute(request)
        except ValueError as e:
            validation_error_vm: ErrorViewModel = self.dummy_presenter.present_validation_error(e)
            return Result.err(validation_error_vm)

        if Result.is_ok(result):
            view_model: DummyViewModel = self.dummy_presenter.present_value(result.value)
            return Result.ok(view_model)

        if Result.is_err(result):
            error_vm: ErrorViewModel = self.dummy_presenter.present_error(result.value)
            return Result.err(error_vm)

        assert_never(result)  # ty:ignore[type-assertion-failure]


@pytest.fixture
def dummy_controller(dummy_use_case: DummyUseCase, dummy_presenter: DummyPresenter) -> DummyController:
    """DummyController fixture."""
    return DummyController(
        dummy_use_case=dummy_use_case,
        dummy_presenter=dummy_presenter,
    )


# ----- Presenter ----- #


@dataclass(frozen=True, slots=True)
class DummyPresenter(BasePresenter):
    """Dummy Presenter."""

    @staticmethod
    def present_value(value: Any) -> DummyViewModel:
        """Present a value."""
        return DummyViewModel(value=str(value))


@pytest.fixture
def dummy_presenter() -> DummyPresenter:
    """DummyPresenter fixture."""
    return DummyPresenter()


# ----- View Model ----- #


@dataclass(frozen=True, slots=True)
class DummyViewModel(BaseViewModel):
    """Dummy ViewModel."""

    value: str


@pytest.fixture
def dummy_view_model_value() -> str:
    """DummyViewModel fixture."""
    return "view_model"


@pytest.fixture
def dummy_view_model(dummy_view_model_value: str) -> DummyViewModel:
    """DummyViewModel fixture."""
    return DummyViewModel(dummy_view_model_value)


# ---------- Infrastructure Layer ---------- #


# ----- Framework ----- #


@dataclass(frozen=True, slots=True)
class DummyFramework(BaseFramework):
    """Dummy Framework."""

    application: BaseApplication
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


@pytest.fixture
def dummy_framework(dummy_application: DummyApplication) -> DummyFramework:
    """DummyFramework fixture."""
    return DummyFramework(
        application=dummy_application,
    )
