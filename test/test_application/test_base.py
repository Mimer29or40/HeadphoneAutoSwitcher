"""Tests for application.base."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from test_application.conftest import DummyApplication

if TYPE_CHECKING:
    pass


@pytest.mark.unit
class TestBaseApplication:
    """Tests for BaseApplication."""

    @pytest.fixture
    def application_obj(self) -> DummyApplication:
        """Application fixture."""
        return DummyApplication()

    def test_name(self, application_obj: DummyApplication) -> None:
        """Verify that the Application has a name."""
        assert hasattr(application_obj, "name")
        assert isinstance(application_obj.name, str)

    def test_description(self, application_obj: DummyApplication) -> None:
        """Verify that the Application has a description."""
        assert hasattr(application_obj, "description")
        assert isinstance(application_obj.description, str)

    def test_version(self, application_obj: DummyApplication) -> None:
        """Verify that the Application has a version."""
        assert hasattr(application_obj, "version")
        assert isinstance(application_obj.version, str)


# ---------- Project Specific ---------- #


if __name__ == "__main__":
    pytest.main()
