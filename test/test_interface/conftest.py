"""Pytest fixtures and utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

from test_application.conftest import DummyOutcome
from test_application.conftest import DummyRequest
from test_application.conftest import DummyResponse

from domain.base import Result
from interface.controller import BaseController
from interface.presenter import BasePresenter
from interface.view_model import BaseViewModel
from interface.view_model import ErrorViewModel

if TYPE_CHECKING:
    from test_application.conftest import DummyUseCase

    from domain.exception import ErrorMsg


# ---------- General Fixtures ---------- #


# ---------- General Utilities ---------- #


@dataclass(frozen=True, slots=True)
class DummyController(BaseController):
    """Dummy controller."""

    dummy_use_case: DummyUseCase
    dummy_presenter: DummyPresenter

    def handle_use_case(self, value: Any) -> Result[DummyViewModel, ErrorViewModel]:
        """Handle Dummy UseCase."""
        try:
            request: DummyRequest = DummyRequest(value=value)
            result: Result[DummyResponse | DummyOutcome, ErrorMsg] = self.dummy_use_case.execute(request)  # ty:ignore[unresolved-reference]
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


# ---------- Project Fixtures ---------- #


# ---------- Project Utilities ---------- #
