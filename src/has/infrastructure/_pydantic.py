"""Headphone Auto Switcher pydantic implementation."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Annotated
from typing import override

from ca.application import BaseConfig
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import StringConstraints

from has.application.config import Config
from has.application.config import ConfigValidator

if TYPE_CHECKING:
    from logging import Logger

logger: Logger = logging.getLogger("has.infrastructure._pydantic")


class ConfigModel(BaseModel):
    """HeadphoneAutoSwitcher config data structure."""

    model_config = ConfigDict(from_attributes=True)

    vendor_id: Annotated[str, StringConstraints(pattern=r"^(?i)(?:0x)?[0-9a-f]+$")]
    product_id: Annotated[str, StringConstraints(pattern=r"^(?i)(?:0x)?[0-9a-f]+$")]
    capture_device: str
    render_device: str


@dataclass(frozen=True, slots=True)
class PydanticValidator[C: BaseConfig](ConfigValidator):
    """HeadphoneAutoSwitcher config data structure."""

    @override
    def validate(self, config: Config) -> None:
        ConfigModel.model_validate(config)
