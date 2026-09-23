"""Application layer base classes, as described by Clean Architecture."""

from __future__ import annotations

import json
import logging
from abc import ABC
from abc import abstractmethod
from dataclasses import Field
from dataclasses import dataclass
from dataclasses import field
from dataclasses import fields
from typing import TYPE_CHECKING
from typing import Any
from typing import Self

from _ca.domain import BaseEntity
from _ca.domain import ErrorMsg

if TYPE_CHECKING:
    from logging import Logger
    from pathlib import Path

    from _ca.utils import Result


logger: Logger = logging.getLogger("application")


class BaseConfig(ABC):
    """Base config class, implementing Clean Architecture patterns."""


class BaseConfigProvider[C: BaseConfig](ABC):
    """Base config provider class, implementing Clean Architecture patterns."""

    config_cls: type[C]

    @abstractmethod
    def get(self, errors: list[str]) -> C:
        """Get the configuration."""

    def create_config(self, data: dict[str, Any], errors: list[str]) -> C:
        """Create the Config object."""
        values: dict[str, str] = {}
        f: Field
        for f in fields(self.config_cls):
            if f.name not in data:
                errors.append(f"{f.name} is required.")
                continue
            if data[f.name] == "":
                errors.append(f"{f.name} is blank.")
                continue
            values[f.name] = data[f.name]

        return self.config_cls(**values)


@dataclass(frozen=True, slots=True)
class MemoryConfigProvider[C: BaseConfig](BaseConfigProvider[C]):  # TODO(Ryan): Move ConfigProviders to infrastructure
    """ConfigProvider that loads a config from memory."""

    data: dict[str, Any]
    config_cls: type[C]

    def get(self, errors: list[str]) -> C:
        """Get the configuration."""
        return self.create_config(self.data, errors)


@dataclass(frozen=True, slots=True)
class JsonConfigProvider[C: BaseConfig](BaseConfigProvider[C]):
    """ConfigProvider that loads a config from a JSON file."""

    file: Path
    config_cls: type[C]

    def get(self, errors: list[str]) -> C:
        """Get the configuration."""
        data: dict[str, Any]
        try:
            data = json.loads(self.file.read_text())
        except OSError:
            errors.append(f"File not found: '{self.file}'")
            data = {}
        except json.decoder.JSONDecodeError:
            errors.append(f"Unable to parse JSON file: '{self.file}'")
            data = {}
        return self.create_config(data, errors)


class BaseApplication(ABC):
    """Base application class, implementing Clean Architecture patterns."""

    name: str
    description: str
    version: str

    config: BaseConfig

    def __post_init__(self) -> None:
        """Wire up use cases and controllers."""


# ----- Data Transfer Object ----- #


class BaseRequest(ABC):
    """Base request class, implementing Clean Architecture patterns."""

    @abstractmethod
    def __post_init__(self) -> None:
        """Validate request data."""

    @abstractmethod
    def convert(self) -> dict[str, Any]:
        """Convert the requested data to a standardized form."""


class BaseResponse[T: BaseEntity](ABC):
    """Base response class, implementing Clean Architecture patterns."""

    @classmethod
    @abstractmethod
    def from_entity(cls, entity: T) -> Self:
        """Create a Response from an Entity."""


class BaseOutcome(ABC):
    """Base outcome class, implementing Clean Architecture patterns."""

    @abstractmethod
    def __str__(self) -> str:
        """Convert the outcome into a human-readable string."""


# ----- Port ----- #


class BasePort(ABC):
    """Base port class, implementing Clean Architecture patterns."""


# ----- Repository ----- #


class BaseRepository(ABC):
    """Base repository class, implementing Clean Architecture patterns."""


# ----- Use Case ----- #


type UseCaseRequestType = BaseRequest
type UseCaseResponseType = BaseResponse | BaseOutcome | list[BaseResponse | BaseOutcome]


@dataclass(frozen=True, slots=True)
class BaseUseCase[REQ: UseCaseRequestType, RES: UseCaseResponseType](ABC):
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
