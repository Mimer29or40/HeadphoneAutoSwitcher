"""Pytest fixtures and utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

from domain.entity import BaseEntity
from domain.exception import BaseError
from domain.exception import ErrorMsg
from domain.service import BaseService
from domain.value import BaseValue

if TYPE_CHECKING:
    pass


# ---------- General Fixtures ---------- #


# ---------- Project Fixtures ---------- #


# ---------- General Utilities ---------- #


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


# ---------- Project Utilities ---------- #
