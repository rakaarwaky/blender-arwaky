"""T-11: ConfigContainer — zero-arg build, flag resolution, supplier wiring."""

from __future__ import annotations

import os
import tempfile

import pytest

from modules.config.src.root_config_container import ConfigContainer
from modules.shared.src.common.taxonomy_core_vo import ConfigPath
from modules.shared.src.config.taxonomy_config_error import ConfigValidationError


@pytest.mark.unit
def test_zero_arg_build_loads_defaults(monkeypatch):
    # chdir to a temp dir with no config.yaml
    d = tempfile.mkdtemp()
    monkeypatch.chdir(d)
    agg = ConfigContainer().build()
    snap = agg.load()
    assert snap.get("blender.port") == 9876
    assert snap.get("server.transport") == "stdio"


@pytest.mark.unit
def test_metadata_populated_after_load(monkeypatch):
    d = tempfile.mkdtemp()
    monkeypatch.chdir(d)
    agg = ConfigContainer().build()
    agg.load()
    md = agg.get_metadata()
    assert md is not None
    assert md.source is not None


@pytest.mark.unit
def test_recent_events_populated_after_load(monkeypatch):
    d = tempfile.mkdtemp()
    monkeypatch.chdir(d)
    agg = ConfigContainer().build()
    agg.load()
    assert len(agg.recent_events()) >= 1


@pytest.mark.unit
def test_metadata_source_ends_with_config_yaml(monkeypatch):
    d = tempfile.mkdtemp()
    monkeypatch.chdir(d)
    agg = ConfigContainer().build()
    agg.load()
    assert str(agg.get_metadata().source).endswith("config.yaml")


@pytest.mark.unit
def test_schema_validation_is_always_enabled():
    d = tempfile.mkdtemp()
    cfg = os.path.join(d, "config.yaml")
    with open(cfg, "w") as f:
        f.write("blender:\n  port: oops\n")
    agg = ConfigContainer().build()
    with pytest.raises(ConfigValidationError):
        agg.load(ConfigPath(cfg))


@pytest.mark.unit
def test_strict_enforcement_cannot_be_disabled():
    agg = ConfigContainer().build()
    d = tempfile.mkdtemp()
    cfg = os.path.join(d, "config.yaml")
    with open(cfg, "w") as f:
        f.write("blender:\n  port: oops\n")
    with pytest.raises(ConfigValidationError):
        agg.load(ConfigPath(cfg))
