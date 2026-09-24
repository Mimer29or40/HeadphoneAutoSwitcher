"""Infrastructure config, as described by Clean Architecture."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import override

from pydantic import BaseModel

from _ca.application import BaseAdapter
from _ca.application import BaseConfig
from _ca.application import BaseConfigProvider
from infrastructure.app import HeadphoneAutoSwitcherConfig

if TYPE_CHECKING:
    from logging import Logger
    from pathlib import Path

logger: Logger = logging.getLogger("infrastructure.config")


class HeadphoneAutoSwitcherConfigModel(BaseModel):
    """HeadphoneAutoSwitcher configuration model."""

    vendor_id: str
    product_id: str
    capture_device: str
    render_device: str


class ModelAdapter(BaseAdapter[HeadphoneAutoSwitcherConfigModel, HeadphoneAutoSwitcherConfig]):
    """Adapter for converting HeadphoneAutoSwitcher configuration and models."""

    @override
    def convert(self, value: HeadphoneAutoSwitcherConfigModel) -> HeadphoneAutoSwitcherConfig:
        return HeadphoneAutoSwitcherConfig(
            vendor_id=value.vendor_id,
            product_id=value.product_id,
            capture_device=value.capture_device,
            render_device=value.render_device,
        )


@dataclass(frozen=True, slots=True)
class JsonModelConfigProvider[C: BaseConfig, M: BaseModel](BaseConfigProvider[C]):
    """ConfigProvider with pydantic models validation from a JSON file."""

    file: Path
    model_cls: type[M]
    adapter: BaseAdapter[M, C]

    @override
    def get(self) -> C:
        json_data: str = self.file.read_text()
        model: M = self.model_cls.model_validate_json(json_data)
        config: C = self.adapter.convert(model)
        return config
