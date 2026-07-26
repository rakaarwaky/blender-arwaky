"""T-13: import hygiene — capabilities must not import other capability modules;
the agent orchestrator must not import capability modules (AES §8/§9)."""

from __future__ import annotations

import ast
import pathlib

import pytest

_CONFIG_SRC = pathlib.Path(__file__).resolve().parents[1] / "src"
_CAPABILITIES = list(_CONFIG_SRC.glob("capabilities_*.py"))
_AGENT = _CONFIG_SRC / "agent_config_orchestrator.py"


def _imported_module_names(tree: ast.Module) -> set[str]:
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
    return names


@pytest.mark.unit
def test_capabilities_do_not_import_other_capabilities():
    for cap_file in _CAPABILITIES:
        tree = ast.parse(cap_file.read_text())
        for mod in _imported_module_names(tree):
            assert "capabilities_" not in mod, (
                f"{cap_file.name} imports capability module {mod}"
            )


@pytest.mark.unit
def test_agent_does_not_import_capability_modules():
    tree = ast.parse(_AGENT.read_text())
    for mod in _imported_module_names(tree):
        assert "capabilities_" not in mod, (
            f"agent orchestrator imports capability module {mod}"
        )


@pytest.mark.unit
def test_config_v1_capabilities_exist():
    # sanity: the 5 FR-mapped capabilities are present
    names = {f.name for f in _CAPABILITIES}
    for expected in (
        "capabilities_settings_loader.py",
        "capabilities_settings_retriever.py",
        "capabilities_settings_metadata.py",
        "capabilities_workspace_resolver.py",
        "capabilities_redaction_rules.py",
    ):
        assert expected in names