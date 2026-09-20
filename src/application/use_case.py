"""Use cases used by the application, as described by Clean Architecture."""

from __future__ import annotations

import logging
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import Any

from application.dto import BaseOutcome
from application.dto import BaseRequest
from application.dto import BaseResponse

if TYPE_CHECKING:
    from logging import Logger

    from domain.base import Result
    from domain.exception import ErrorMsg


logger: Logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class BaseUseCase[REQ: BaseRequest, RES: BaseResponse | BaseOutcome](ABC):
    """Base use case class, implementing Clean Architecture patterns."""

    _optional_services: dict[str, Any] = field(default_factory=dict, init=False)

    def register_service(self, name: str, service: Any) -> None:
        """Register an optional service with the use cases at runtime."""
        self._optional_services[name] = service

    def unregister_service(self, name: str) -> None:
        """Unregister an optional service with the use cases at runtime."""
        self._optional_services.pop(name)

    @abstractmethod
    def execute(self, request: REQ) -> Result[RES, ErrorMsg]:
        """Execute the use case with the provided request."""


# ---------- Project Specific ---------- #
