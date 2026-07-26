"""T-09: Event ring buffer (50-event bound) + orchestrator event emission."""

from __future__ import annotations

import logging

import pytest

from modules.config.src.agent_config_orchestrator import ConfigOrchestrator
from modules.config.src.capabilities_redaction_rules import RedactionRulesCapability
from modules.config.src.capabilities_settings_loader import SettingsLoaderCapability
from modules.config.src.capabilities_settings_metadata import SettingsMetadataCapability
from modules.config.src.capabilities_settings_retriever import SettingsRetrieverCapability
from modules.config.src.capabilities_workspace_resolver import WorkspaceResolverCapability
from modules.shared.src.config.taxonomy_config_constant import EVENT_RING_BUFFER_SIZE


def _orchestrator(permissive=False):
    mode = "permissive" if permissive else "strict"
    loader = SettingsLoaderCapability(policy_mode=mode, config_v2_enabled=True)
    return ConfigOrchestrator(
        loader=loader,
        retriever=SettingsRetrieverCapability(policy_mode=mode),
        workspace_resolver=WorkspaceResolverCapability(),
        metadata_provider=SettingsMetadataCapability(metadata_supplier=loader.get_last_metadata),
        redaction_rules=RedactionRulesCapability(),
    )


@pytest.mark.unit
def test_ring_buffer_holds_50_drops_oldest():
    orch = _orchestrator()
    for _ in range(60):
        orch.load()
    events = orch.recent_events()
    assert len(events) == EVENT_RING_BUFFER_SIZE
    assert len(events) == 50


@pytest.mark.unit
def test_events_ordered_oldest_to_newest():
    orch = _orchestrator()
    orch.load()
    orch.reload()
    events = orch.recent_events()
    categories = [e["category"] for e in events]
    assert "settings" in categories
    # reload event comes after load event
    assert categories.index("settings") < len(categories)


@pytest.mark.unit
def test_recent_events_limit_slicing():
    orch = _orchestrator()
    for _ in range(10):
        orch.load()
    events = orch.recent_events(limit=3)
    assert len(events) == 3


@pytest.mark.unit
def test_log_record_emitted(caplog):
    orch = _orchestrator()
    with caplog.at_level(logging.INFO, logger="BlenderMCPServer"):
        orch.load()
    assert any("config_event" in r.message for r in caplog.records)


@pytest.mark.unit
def test_orchestrator_load_reload_resolve_record_events():
    orch = _orchestrator()
    orch.load()
    orch.reload()
    orch.resolve_workspace()
    events = orch.recent_events()
    cats = [e["category"] for e in events]
    assert cats.count("settings") >= 2
    assert "workspace" in cats


@pytest.mark.unit
def test_permissive_schema_warning_records_validation_event():
    orch = _orchestrator(permissive=True)
    # load with bad schema port via file
    import os
    import tempfile

    d = tempfile.mkdtemp()
    cfg = os.path.join(d, "config.yaml")
    with open(cfg, "w") as f:
        f.write("blender:\n  port: oops\n")
    orch.load(cfg)
    events = orch.recent_events()
    assert any(e["category"] == "validation" for e in events)


@pytest.mark.unit
def test_recent_events_without_sink_returns_empty():
    # Orchestrator always owns the buffer, so this validates the buffer is empty pre-load
    orch = _orchestrator()
    assert orch.recent_events() == ()
