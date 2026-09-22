"""Test module for the architecture of the project."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator
    from collections.abc import Sequence

    from pytest_check import CheckType

    type Layer = str
    type Level = int

_LAYERS: Sequence[Layer] = [
    "domain",
    "application",
    "interface",
    "infrastructure",
]


def _get_level_from_layer(layer: Layer) -> Level:
    return _LAYERS.index(layer)


def _get_layer_from_level(level: Level) -> Layer:
    return _LAYERS[level]


def _get_python_files(path: Path) -> Generator[tuple[Path, Path]]:
    file: Path
    for file in path.rglob("*.py"):
        file_rel: Path = file.relative_to(path.parent)
        yield file, file_rel


def _get_test_file_from_rel(file_rel: Path) -> Path:
    parts: list[str]
    if file_rel.stem == "__init__":
        parts = [f"test_{p}" for p in file_rel.parts[:-1]]
        parts.append("__init__.py")
    else:
        parts = [f"test_{p}" for p in file_rel.parts]
    return Path("/".join(parts))


def _get_module_node(file: Path) -> ast.Module:
    source: str = file.read_text()
    return ast.parse(source)


@pytest.fixture(params=tuple(_LAYERS))
def layer(request: pytest.FixtureRequest) -> Layer:
    """Project Layer fixture."""
    return request.param


@pytest.fixture
def level(layer: Layer) -> Level:
    """Project Level fixture."""
    return _get_level_from_layer(layer)


@pytest.fixture
def layer_path(project_src_path: Path, layer: Layer) -> Path:
    """Project Layer path fixture."""
    return project_src_path / layer


@pytest.fixture
def layer_test_path(project_test_path: Path, layer: Layer) -> Path:
    """Project Layer test path fixture."""
    return project_test_path / f"test_{layer}"


@pytest.mark.architectural
def test_module_present(layer_path: Path) -> None:
    """Verify that each Layer's associated module is present."""
    # Assert
    assert layer_path.exists()


def test_file_logger(check: CheckType, layer_path: Path) -> None:
    """Verify all files have a correctly named Logger."""
    # Arrange
    file: Path
    file_rel: Path
    for file, file_rel in _get_python_files(layer_path):
        module_node: ast.Module = _get_module_node(file)

        # Act
        module_name: str = ".".join(file_rel.with_suffix("").parts)

        if module_name.endswith(("__init__", "__main__")):
            continue  # Skip dunder files

        # Assert
        found_logger: bool = False
        with check:
            node: ast.AST
            for node in ast.walk(module_node):
                try:
                    if node.target.id != "logger":  # ty:ignore[unresolved-attribute]
                        continue
                    found_logger = True
                    assert node.value.args[0].value == module_name  # ty:ignore[unresolved-attribute]
                except AttributeError:
                    continue

            if not found_logger:
                pytest.fail(f"File does not have a logger: '{file_rel}'")


def test_layer_dependencies(check: CheckType, layer: Layer, level: Level, layer_path: Path) -> None:
    """Verify that each Layer only import from lower Layers."""
    # Arrange
    layer_pattern: re.Pattern[str] = re.compile(rf"^({'|'.join(_LAYERS)})")

    def get_layer(module_name: str, layer_pattern: re.Pattern[str] = layer_pattern) -> Layer | None:
        file_layer_match: re.Match[str] | None = layer_pattern.match(module_name)
        if file_layer_match is None:
            return None
        layer: Layer = file_layer_match.group(1)
        return layer

    file: Path
    file_rel: Path
    for file, file_rel in _get_python_files(layer_path):
        module_node: ast.Module = _get_module_node(file)

        node: ast.AST
        for node in ast.walk(module_node):
            module_name: str
            if isinstance(node, ast.Import):
                module_name: str = node.names[0].name
            elif isinstance(node, ast.ImportFrom):
                module_name: str = str(node.module)
            else:
                continue

            module_layer: Layer | None = get_layer(module_name)
            if module_layer is None:
                continue
            module_level: Level = _get_level_from_layer(module_layer)

            # Act
            result: bool = module_level > level

            # Assert
            with check:
                if result:
                    pytest.fail(f"Layer '{module_layer}' cannot be imported from file in Layer '{layer}': '{file_rel}'")


def test_has_test_file(check: CheckType, layer_path: Path, layer_test_path: Path) -> None:
    """Verify that each Python file has a test file."""
    # Arrange
    layer_test_files: dict[Path, Path] = {r: f for f, r in _get_python_files(layer_test_path)}

    file_rel: Path
    for _, file_rel in _get_python_files(layer_path):
        test_file: Path = _get_test_file_from_rel(file_rel)

        if file_rel.stem.endswith(("__init__", "__main__")):
            continue  # Skip dunder files

        # Act
        result: bool = test_file in layer_test_files

        # Assert
        with check:
            if not result:
                pytest.fail(f"File must have a test file: '{file_rel}'")


def test_has_test_class(check: CheckType, layer_path: Path, project_test_path: Path) -> None:
    """Verify that each defined class has a test class."""
    # Arrange
    file: Path
    file_rel: Path
    for file, file_rel in _get_python_files(layer_path):
        if file_rel.stem.endswith(("__init__", "__main__")):
            continue  # Skip dunder files

        test_file: Path = project_test_path / _get_test_file_from_rel(file_rel)

        file_node: ast.Module = _get_module_node(file)
        file_classes: list[str] = sorted([n.name for n in ast.walk(file_node) if isinstance(n, ast.ClassDef)])

        test_file_node: ast.Module = _get_module_node(test_file)
        test_file_classes: list[str] = sorted([n.name for n in ast.walk(test_file_node) if isinstance(n, ast.ClassDef)])

        file_cls: str
        for file_cls in file_classes:
            test_cls_name: str = "Test" + file_cls

            # Act
            result: bool = test_cls_name in test_file_classes

            # Assert
            with check:
                if not result:
                    pytest.fail(f"Class must have a test class: '{file_cls}'")


if __name__ == "__main__":
    pytest.main()
