"""T-11: ConfigContainer — zero-arg build, flag resolution, supplier wiring."""

from __future__ import annotations

import os
import tempfile

import pytest

from modules.config.src.root_config_container import ConfigContainer
from modules.shared.src.config.taxonomy_config_constant import CONFIG_V2_FLAG_ENV


@pytest.mark.unit
def test_zero_arg_build_loads_defaults(monkeypatch):
    monkeypatch.delenv(CONFIG_V2_FLAG_ENV, raising=False)
    # chdir to a temp dir with no config.yaml
    d = tempfile.mkdtemp()
    monkeypatch.chdir(d)
    agg = ConfigContainer().build()
    snap = agg.load()
    assert snap.get("blender.port") == 9876
    assert snap.get("server.transport") == "stdio"


@pytest.mark.unit
def test_metadata_populated_after_load(monkeypatch):
    monkeypatch.delenv(CONFIG_V2_FLAG_ENV, raising=False)
    d = tempfile.mkdtemp()
    monkeypatch.chdir(d)
    agg = ConfigContainer().build()
    agg.load()
    md = agg.get_metadata()
    assert md is not None
    assert md.source is not None


@pytest.mark.unit
def test_recent_events_populated_after_load(monkeypatch):
    monkeypatch.delenv(CONFIG_V2_FLAG_ENV, raising=False)
    d = tempfile.mkdtemp()
    monkeypatch.chdir(d)
    agg = ConfigContainer().build()
    agg.load()
    assert len(agg.recent_events()) >= 1


@pytest.mark.unit
def test_metadata_source_ends_with_config_yaml(monkeypatch):
    monkeypatch.delenv(CONFIG_V2_FLAG_ENV, raising=False)
    d = tempfile.mkdtemp()
    monkeypatch.chdir(d)
    agg = ConfigContainer().build()
    agg.load()
    assert str(agg.get_metadata().source).endswith("config.yaml")


@pytest.mark.unit
def test_flag_from_env_enables_schema_errors(monkeypatch):
    monkeypatch.setenv(CONFIG_V2_FLAG_ENV, "true")
    d = tempfile.mkdtemp()
    cfg = os.path.join(d, "config.yaml")
    with open(cfg, "w") as f:
        f.write("blender:\n  port: oops\n")
    from modules.shared.src.common.taxonomy_core_vo import ConfigPath
    from modules.shared.src.config.taxonomy_config_error import ConfigValidationError

    agg = ConfigContainer().build()
    with pytest.raises(ConfigValidationError):
        agg.load(ConfigPath(cfg))


@pytest.mark.unit
def test_explicit_false_beats_env_true(monkeypatch):
    monkeypatch.setenv(CONFIG_V2_FLAG_ENV, "true")
    agg = ConfigContainer(config_v2_enabled=False).build()
    # flag OFF → no schema validation; bad port does not raise
    d = tempfile.mkdtemp()
    cfg = os.path.join(d, "config.yaml")
    with open(cfg, "w") as f:
        f.write("blender:\n  port: oops\n")
    from modules.shared.src.common.taxonomy_core_vo import ConfigPath

    snap = agg.load(ConfigPath(cfg))
    assert snap.get("blender.port") == "oops"  # no validation, value accepted