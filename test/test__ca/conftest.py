"""Pytest fixtures and utilities."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from typing import Self
from typing import override

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
from _ca.infrastructure import BaseRunner
from _ca.interface import BaseController
from _ca.interface import BasePresenter
from _ca.interface import BaseViewModel
from _ca.interface import ErrorViewModel
from _ca.utils import Result

if TYPE_CHECKING:
    pass


# ---------- Domain Layer ---------- #


@dataclass(eq=False)
class DummyEntity(BaseEntity):
    """Dummy value."""

    value: Any


DUMMY_ERROR_MSG: ErrorMsg = ErrorMsg("FAILURE", "12345")


class DummyError(BaseError):
    """Dummy error."""


@dataclass(frozen=True, slots=True)
class DummyService(BaseService):
    """Dummy service."""

    @staticmethod
    def convert_entity_to_value(entity: DummyEntity) -> DummyValue:
        """Convert entity to value."""
        return DummyValue(entity.value)

    @staticmethod
    def convert_value_to_entity(value: DummyValue) -> DummyEntity:
        """Convert value to entity."""
        return DummyEntity(value.value)


@dataclass(frozen=True, slots=True)
class DummyValue(BaseValue):
    """Dummy value."""

    value: Any


# ---------- Application Layer ---------- #


@dataclass(frozen=True, slots=True)
class DummyApplication(BaseApplication):
    """Dummy application."""

    name: str = "Dummy Application"
    description: str = "Dummy Application."
    version: str = "0.0.0"


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


@dataclass(frozen=True, slots=True)
class DummyResponse(BaseResponse):
    """Dummy response."""

    value: str

    @classmethod
    def from_entity(cls, entity: DummyEntity) -> Self:
        """Create a Response from an Entity."""
        return cls(value=str(entity.value))


@dataclass(frozen=True, slots=True)
class DummyOutcome(BaseOutcome):
    """Dummy outcome."""

    value: Any

    def __str__(self) -> str:
        """Convert the outcome into a human-readable string."""
        return str(self.value)


@dataclass(frozen=True, slots=True)
class DummyPort(BasePort):
    """Dummy rort."""

    value: Any
    notifications: list[Any] = field(default_factory=list, init=False)

    def notify(self) -> None:
        """Notify something."""
        self.notifications.append(self.value)


@dataclass(frozen=True, slots=True)
class DummyRepository(BaseRepository):
    """Dummy repository."""

    values: list[Any]

    def get(self, index: int) -> Any:
        """Get something from a repository."""
        return self.values[index]


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


# ---------- Interface Layer ---------- #


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

        raise RuntimeError  # This will never happen


@dataclass(frozen=True, slots=True)
class DummyPresenter(BasePresenter):
    """Dummy presenter."""

    @staticmethod
    def present_value(value: Any) -> DummyViewModel:
        """Present a value."""
        return DummyViewModel(value=str(value))


@dataclass(frozen=True, slots=True)
class DummyViewModel(BaseViewModel):
    """Dummy view model."""

    value: str


# ---------- Infrastructure Layer ---------- #


@dataclass(frozen=True, slots=True)
class DummyRunner(BaseRunner):
    """Dummy runner class, implementing Clean Architecture patterns."""

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
