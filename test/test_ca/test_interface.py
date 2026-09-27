"""Tests for ca.interface."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from ca.interface import BaseController
    from ca.interface import BasePresenter
    from ca.interface import BaseViewModel
    from ca.interface import ErrorViewModel
    from test_ca._dummy import DummyController
    from test_ca._dummy import DummyEntityPresenter
    from test_ca._dummy import DummyEntityViewModel


# ---------- ViewModel ---------- #


class TestBaseViewModel:
    """Tests for BaseViewModel."""

    @pytest.mark.unit
    def test_dummy(self, dummy_entity_view_model: DummyEntityViewModel) -> None:
        """Dummy test."""
        # Arrange
        _: BaseViewModel = dummy_entity_view_model


class TestErrorViewModel:
    """Tests for ErrorViewModel."""

    @pytest.mark.unit
    def test_message(self, dummy_entity_view_model: ErrorViewModel) -> None:
        """Test for ErrorViewModel.message."""  # TODO(Ryan): Implement
        # Arrange
        _: ErrorViewModel = dummy_entity_view_model

    @pytest.mark.unit
    def test_code(self, dummy_entity_view_model: ErrorViewModel) -> None:
        """Test for ErrorViewModel.code."""  # TODO(Ryan): Implement
        # Arrange
        _: ErrorViewModel = dummy_entity_view_model


# ---------- Presenter ---------- #


class TestBasePresenter:
    """Tests for BasePresenter."""

    @pytest.mark.unit
    def test_repr(self, dummy_entity_presenter: DummyEntityPresenter) -> None:
        """Test for BasePresenter.__repr__()."""  # TODO(Ryan): Implement
        # Arrange
        _: BasePresenter = dummy_entity_presenter

    @pytest.mark.unit
    def test_present(self, dummy_entity_presenter: DummyEntityPresenter) -> None:
        """Test for BasePresenter.present()."""  # TODO(Ryan): Implement
        # Arrange
        _: BasePresenter = dummy_entity_presenter

    @pytest.mark.unit
    def test_present_many(self, dummy_entity_presenter: DummyEntityPresenter) -> None:
        """Test for BasePresenter.present_many()."""  # TODO(Ryan): Implement
        # Arrange
        _: BasePresenter = dummy_entity_presenter

    @pytest.mark.unit
    def test_present_error(self, dummy_entity_presenter: DummyEntityPresenter) -> None:
        """Test for BasePresenter.present_error()."""  # TODO(Ryan): Implement
        # Arrange
        _: BasePresenter = dummy_entity_presenter

    @pytest.mark.unit
    def test_present_validation_error(self, dummy_entity_presenter: DummyEntityPresenter) -> None:
        """Test for BasePresenter.present_validation_error()."""  # TODO(Ryan): Implement
        # Arrange
        _: BasePresenter = dummy_entity_presenter


# ---------- Controller ---------- #


class TestBaseController:
    """Tests for BaseController."""

    @pytest.mark.unit
    def test_dummy(self, dummy_controller: DummyController) -> None:
        """Dummy test."""
        # Arrange
        _: BaseController = dummy_controller


if __name__ == "__main__":
    pytest.main()
