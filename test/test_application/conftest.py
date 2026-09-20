"""Pytest fixtures and utilities."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from typing import Self
from typing import override

from test_domain.conftest import DummyEntity
from test_domain.conftest import DummyService

from application.base import BaseApplication
from application.dto import BaseOutcome
from application.dto import BaseRequest
from application.dto import BaseResponse
from application.port import BasePort
from application.repository import BaseRepository
from application.use_case import BaseUseCase
from domain.base import Result

if TYPE_CHECKING:
    from domain.exception import ErrorMsg


# ---------- General Fixtures ---------- #


# ---------- General Utilities ---------- #


@dataclass(frozen=True, slots=True)
class DummyApplication(BaseApplication):
    """Dummy application."""

    name: str = "Dummy Application"
    description: str = "Application used for testing."
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
class DummyResponse(BaseResponse[DummyEntity]):
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


# ---------- Project Fixtures ---------- #


# ---------- Project Utilities ---------- #
