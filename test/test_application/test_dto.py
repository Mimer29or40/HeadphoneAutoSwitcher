"""Tests for application.dto."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

import pytest
from test_domain.conftest import DummyEntity

from test_application.conftest import DummyOutcome
from test_application.conftest import DummyRequest
from test_application.conftest import DummyResponse

if TYPE_CHECKING:
    from application.dto import BaseOutcome
    from application.dto import BaseRequest
    from application.dto import BaseResponse


@pytest.mark.unit
class TestBaseRequest:
    """Tests for BaseRequest."""

    @pytest.fixture
    def request_obj(self) -> BaseRequest:
        """BaseRequest fixture."""
        return DummyRequest("VALUE")

    def test_convert(self, request_obj: BaseRequest) -> None:
        """Tests for BaseRequest.convert()."""
        # Act
        result: dict[str, Any] = request_obj.convert()

        # Assert
        assert isinstance(result, dict)


@pytest.mark.unit
class TestBaseResponse:
    """Tests for BaseResponse."""

    def test_from_entity(self) -> None:
        """Tests for BaseRequest.from_entity()."""
        # Arrange
        entity: DummyEntity = DummyEntity("VALUE")

        # Act
        result: BaseResponse = DummyResponse.from_entity(entity)

        # Assert
        assert isinstance(result, DummyResponse)


@pytest.mark.unit
class TestBaseOutcome:
    """Tests for BaseOutcome."""

    def test_str(self) -> None:
        """Tests for BaseOutcome.__str__()."""
        # Arrange
        value: Any = "VALUE"
        outcome: BaseOutcome = DummyOutcome(value)

        # Act
        result: str = str(outcome)

        # Assert
        assert isinstance(result, str)


# ---------- Project Specific ---------- #


if __name__ == "__main__":
    pytest.main()
