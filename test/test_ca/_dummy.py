"""Dummy module for testing Clean Architecture."""

from __future__ import annotations

import logging
from abc import ABC
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import Any
from typing import Self
from typing import TypedDict
from typing import assert_never
from typing import override

from ca.application import BaseApplication
from ca.application import BaseApplicationFactory
from ca.application import BasePort
from ca.application import BaseRequest
from ca.application import BaseRequestDict
from ca.application import BaseResponse
from ca.application import BaseUseCase
from ca.domain import ApplicationError
from ca.domain import BaseEntity
from ca.domain import BaseError
from ca.domain import BaseRepository
from ca.domain import BaseService
from ca.domain import BaseValue
from ca.domain import ControllerError
from ca.domain import ErrorMsg
from ca.domain import FrameworkError
from ca.domain import PresenterError
from ca.domain import RepositoryError
from ca.domain import ServiceError
from ca.domain import UseCaseError
from ca.infrastructure import RESULT_FAILURE
from ca.infrastructure import CommandFramework
from ca.infrastructure import FrameworkResult
from ca.infrastructure import LogConfigProvider
from ca.interface import BaseController
from ca.interface import BasePresenter
from ca.interface import BaseViewModel
from ca.interface import ErrorViewModel
from ca.utils import Result
from ca.utils import log_call

if TYPE_CHECKING:
    from logging import Logger
    from uuid import UUID


logger: Logger = logging.getLogger("test_ca._dummy")


class _BaseDummy(ABC):
    error_cls: type[BaseError] | None

    def should_raise(self, message: ErrorMsg) -> None:
        if self.error_cls is not None:
            raise self.error_cls(message)


# -------------------- Domain -------------------- #


# ---------- Value ---------- #


@dataclass(frozen=True, slots=True)
class DummyValue(BaseValue):
    obj: Any


# ---------- Entity ---------- #


@dataclass(eq=False, kw_only=True)
class DummyEntity(BaseEntity):
    value: DummyValue


# ---------- Error ---------- #


# ---------- Service ---------- #


DUMMY_SERVICE_ERROR: ErrorMsg = ErrorMsg("DummyService Error.")


@dataclass(frozen=True, slots=True)
class DummyService(BaseService, _BaseDummy):
    error_cls: type[ServiceError] | None = None

    @log_call(type="method")
    def create_value(self, obj: Any) -> DummyValue:
        self.should_raise(DUMMY_SERVICE_ERROR)
        return DummyValue(obj=obj)

    @log_call(type="method")
    def create_entity(self, value: DummyValue) -> DummyEntity:
        self.should_raise(DUMMY_SERVICE_ERROR)
        return DummyEntity(value=value)


# ---------- Repository ---------- #


DUMMY_REPOSITORY_ERROR: ErrorMsg = ErrorMsg("DummyRepository Error.")


@dataclass(frozen=True, slots=True)
class DummyRepository(BaseRepository, _BaseDummy):
    entities: dict[UUID, DummyEntity]

    error_cls: type[RepositoryError] | None = None

    @log_call(type="method")
    def get(self, entity_id: UUID) -> DummyEntity | None:
        self.should_raise(DUMMY_REPOSITORY_ERROR)
        return self.entities.get(entity_id)

    @log_call(type="method")
    def set(self, entity: DummyEntity) -> None:
        self.should_raise(DUMMY_REPOSITORY_ERROR)
        self.entities[entity.id] = entity

    @log_call(type="method")
    def remove(self, entity_id: UUID) -> None:
        self.should_raise(DUMMY_REPOSITORY_ERROR)
        self.entities.pop(entity_id)


# -------------------- Application -------------------- #


# ---------- Application ---------- #


DUMMY_APPLICATION_ERROR: ErrorMsg = ErrorMsg("DummyApplication Error.")


@dataclass(frozen=True, kw_only=True, slots=True)
class DummyApplication(BaseApplication, _BaseDummy):
    # Service
    service: DummyService | None
    repository: DummyRepository | None

    # Presenter
    presenter: DummyEntityPresenter

    # Controller
    controller: DummyController = field(init=False, repr=False)

    error_cls: type[ApplicationError] | None = None

    @override
    @log_call(type="method")
    def __post_init__(self) -> None:
        self.should_raise(DUMMY_APPLICATION_ERROR)

        # Create UseCases
        use_case: DummyUseCase = DummyUseCase()
        use_case.register(DUMMY_USE_CASE_SERVICE, self.service)
        use_case.register(DUMMY_USE_CASE_REPOSITORY, self.repository)

        # Wire Controllers
        controller: DummyController = DummyController(
            use_case=use_case,
            presenter=self.presenter,
        )
        object.__setattr__(self, "controller", controller)


@dataclass(frozen=True, kw_only=True, slots=True)
class DummyApplicationFactory(BaseApplicationFactory[DummyApplication]):
    name: str = "Dummy Application"
    description: str = "Does nothing!"
    version: str = "0.0.0"

    # Service
    service: DummyService | None
    repository: DummyRepository | None

    # Presenter
    presenter: DummyEntityPresenter

    @override
    @log_call(type="method")
    def create(self) -> DummyApplication:
        app: DummyApplication = DummyApplication(
            service=self.service,
            repository=self.repository,
            presenter=self.presenter,
        )
        return app


# ---------- Data Transfer Object (DTO) ---------- #


class DummyRequestDict(BaseRequestDict, TypedDict):
    obj: Any


@dataclass(frozen=True, slots=True)
class DummyRequest(BaseRequest[DummyRequestDict]):
    obj: Any

    @override
    @log_call(type="method")
    def __post_init__(self) -> None:
        if self.obj is None:
            raise ValueError("obj cannot be None")

    @override
    @log_call(type="method")
    def convert(self) -> DummyRequestDict:
        return DummyRequestDict(obj=self.obj)


@dataclass(frozen=True, slots=True)
class DummyEntityResponse(BaseResponse[DummyEntity]):
    value: str

    @classmethod
    @override
    @log_call(type="class")
    def from_entity(cls, entity: DummyEntity) -> Self:
        return cls(value=str(entity.value.obj))


# ---------- Port ---------- #


class DummyPort(BasePort):  # TODO(Ryan): Implement
    pass


# ---------- Use Case ---------- #


DUMMY_USE_CASE_ERROR: ErrorMsg = ErrorMsg("DummyUseCase Error.")

DUMMY_USE_CASE_SERVICE: str = "SERVICE"
DUMMY_USE_CASE_REPOSITORY: str = "REPOSITORY"


@dataclass(frozen=True, slots=True)
class DummyUseCase(BaseUseCase[DummyRequest, DummyEntityResponse], _BaseDummy):
    error_cls: type[UseCaseError] | None = None

    @override
    @log_call(type="method")
    def execute(self, request: DummyRequest) -> Result[list[DummyEntityResponse], ErrorMsg]:
        self.should_raise(DUMMY_USE_CASE_ERROR)

        try:
            request_dict: DummyRequestDict = request.convert()

            service: DummyService | None = self.optional.get(DUMMY_USE_CASE_SERVICE)
            repository: DummyRepository | None = self.optional.get(DUMMY_USE_CASE_REPOSITORY)

            entities: list[DummyEntity] = []
            match service, repository:
                case DummyService(), None:
                    entities = self._handle_service(service, request_dict)
                case None, DummyRepository():
                    entities = self._handle_repository(repository, request_dict)

            success_value: list[DummyEntityResponse] = DummyEntityResponse.from_entities(entities)
            return Result.ok(success_value)
        except (ServiceError, RepositoryError) as e:
            error_value: ErrorMsg = e.message
            logger.critical("%s raised an error: %s", type(e).__name__, error_value, exc_info=False)
            return Result.err(error_value)

    def _handle_service(self, service: DummyService, request_dict: DummyRequestDict) -> list[DummyEntity]:
        obj: Any = request_dict["obj"]
        value: DummyValue = service.create_value(obj)
        entity: DummyEntity = service.create_entity(value)
        return [entity]

    def _handle_repository(self, repository: DummyRepository, request_dict: DummyRequestDict) -> list[DummyEntity]:  # noqa: ARG002
        return []  # TODO(Ryan): Implement


# -------------------- Interface -------------------- #


# ---------- ViewModel ---------- #


@dataclass(frozen=True, slots=True)
class DummyEntityViewModel(BaseViewModel):
    value: str


# ---------- Presenter ---------- #


@dataclass(repr=False, frozen=True, slots=True)
class DummyEntityPresenter(BasePresenter[DummyEntityResponse, DummyEntityViewModel]):
    error_cls: type[PresenterError] | None = None

    @classmethod
    @override
    @log_call(type="class")
    def present(cls, response: DummyEntityResponse) -> DummyEntityViewModel:
        return DummyEntityViewModel(value=response.value)


# ---------- Controller ---------- #


DUMMY_CONTROLLER_ERROR_MESSAGE: ErrorMsg = ErrorMsg("DummyController error.")


@dataclass(frozen=True, slots=True)
class DummyController(BaseController, _BaseDummy):
    use_case: DummyUseCase
    presenter: DummyEntityPresenter

    error_cls: type[ControllerError] | None = None

    @log_call(type="method")
    def handle_use_case(self, obj: Any) -> Result[list[DummyEntityViewModel], ErrorViewModel]:
        self.should_raise(DUMMY_CONTROLLER_ERROR_MESSAGE)

        try:
            request: DummyRequest = DummyRequest(obj=obj)
            result: Result[list[DummyEntityResponse], ErrorMsg] = self.use_case.execute(request)
        except ValueError as e:
            error_value: ErrorViewModel = self.presenter.present_validation_error(e)
            return Result.err(error_value)

        if Result.is_ok(result):
            logger.info("Success: self.dummy_use_case.execute", extra={"context": {"ok": result.value}})

            responses: list[DummyEntityResponse] = result.value
            success_value: list[DummyEntityViewModel] = self.presenter.present_many(responses)
            return Result.ok(success_value)

        if Result.is_err(result):
            logger.info("Failure: self.dummy_use_case.execute", extra={"context": {"err": result.value}})

            message: ErrorMsg = result.value
            error_value: ErrorViewModel = self.presenter.present_error(message)
            return Result.err(error_value)

        assert_never(result)  # ty:ignore[type-assertion-failure]


# -------------------- Infrastructure -------------------- #


# ---------- Framework ---------- #


DUMMY_FRAMEWORK_ERROR_MESSAGE: ErrorMsg = ErrorMsg("DummyFramework error.")


@dataclass(frozen=True, slots=True)
class DummyFramework(CommandFramework[DummyApplication], _BaseDummy):
    app_factory: DummyApplicationFactory
    obj: Any

    error_cls: type[FrameworkError] | None = None

    @override
    @log_call(type="method")
    def run_impl(self, *args: Any) -> FrameworkResult:
        """Run the Framework."""
        self.should_raise(DUMMY_FRAMEWORK_ERROR_MESSAGE)

        app: DummyApplication = self.app_factory.create()

        obj: Any = self.obj
        result: Result[list[DummyEntityViewModel], ErrorViewModel] = app.controller.handle_use_case(obj)

        if Result.is_ok(result):
            logger.info("Success: app.dummy_controller.handle_use_case", extra={"context": {"ok": result.value}})

            entities: list[DummyEntityViewModel] = result.value
            string: str = ", ".join([entity.value for entity in entities])
            return string

        if Result.is_err(result):
            logger.info("Failure: app.dummy_controller.handle_use_case", extra={"context": {"err": result.value}})

            logger.error(result.value)
            return RESULT_FAILURE

        assert_never(result)  # ty:ignore[type-assertion-failure]


# ---------- Logging ---------- #


@dataclass(frozen=True, slots=True)
class DummyLogConfigProvider(LogConfigProvider):
    config: dict[str, Any]

    @override
    @log_call(type="method")
    def get(self) -> dict[str, Any]:
        return self.config
