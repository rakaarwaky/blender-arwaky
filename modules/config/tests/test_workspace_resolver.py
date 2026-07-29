"""T-10: WorkspaceResolverCapability — strategy order, caching, legacy regression."""

from __future__ import annotations

import os
import tempfile

import pytest

from modules.config.src.capabilities_workspace_resolver import WorkspaceResolverCapability


@pytest.mark.unit
def test_explicit_override_strategy(monkeypatch):
    d = tempfile.mkdtemp()
    monkeypatch.delenv("BLENDERMCP_ROOT", raising=False)
    r = WorkspaceResolverCapability(explicit_override=d)
    ws = r.resolve()
    assert ws.strategy == "explicit_override"
    assert ws.path == d


@pytest.mark.unit
def test_explicit_invalid_falls_through(monkeypatch):
    monkeypatch.delenv("BLENDERMCP_ROOT", raising=False)
    r = WorkspaceResolverCapability(explicit_override="/nonexistent_dir_xyz")
    ws = r.resolve()
    assert ws.strategy != "explicit_override"


@pytest.mark.unit
def test_env_signal_strategy(monkeypatch):
    d = tempfile.mkdtemp()
    monkeypatch.setenv("BLENDERMCP_ROOT", d)
    r = WorkspaceResolverCapability()
    ws = r.resolve()
    assert ws.strategy == "env_signal"
    assert ws.path == d


@pytest.mark.unit
def test_blender_mcp_root_legacy_ignored(monkeypatch):
    # Q8 regression: legacy BLENDER_MCP_ROOT must NOT be honored
    d = tempfile.mkdtemp()
    monkeypatch.setenv("BLENDER_MCP_ROOT", d)
    monkeypatch.delenv("BLENDERMCP_ROOT", raising=False)
    r = WorkspaceResolverCapability()
    ws = r.resolve()
    assert ws.strategy != "env_signal"


@pytest.mark.unit
def test_settings_file_location_strategy(monkeypatch):
    monkeypatch.delenv("BLENDERMCP_ROOT", raising=False)
    d = tempfile.mkdtemp()
    cfg = os.path.join(d, "config.yaml")
    open(cfg, "w").close()
    r = WorkspaceResolverCapability(config_path=cfg)
    ws = r.resolve()
    assert ws.strategy == "settings_file_location"
    assert ws.path == d


@pytest.mark.unit
def test_marker_search_strategy(monkeypatch):
    monkeypatch.delenv("BLENDERMCP_ROOT", raising=False)
    # chdir into a temp dir that contains pyproject.toml
    d = tempfile.mkdtemp()
    open(os.path.join(d, "pyproject.toml"), "w").close()
    monkeypatch.chdir(d)
    r = WorkspaceResolverCapability()
    ws = r.resolve()
    assert ws.strategy == "marker_search"


@pytest.mark.unit
def test_caching_only_one_filesystem_probe(monkeypatch):
    monkeypatch.delenv("BLENDERMCP_ROOT", raising=False)
    d = tempfile.mkdtemp()
    calls = {"n": 0}

    orig = WorkspaceResolverCapability._resolve_uncached

    def counting(self):
        calls["n"] += 1
        return orig(self)

    monkeypatch.setattr(WorkspaceResolverCapability, "_resolve_uncached", counting)
    r = WorkspaceResolverCapability(explicit_override=d)
    r.resolve()
    r.resolve()
    assert calls["n"] == 1


@pytest.mark.unit
def test_symlinked_dir_resolves():
    base = tempfile.mkdtemp()
    real = os.path.join(base, "real")
    os.makedirs(real)
    link = os.path.join(base, "link")
    os.symlink(real, link)
    r = WorkspaceResolverCapability(explicit_override=link)
    ws = r.resolve()
    # resolves without error; .resolve() normalizes the symlink to its real target
    assert ws.strategy == "explicit_override"
    assert os.path.isdir(ws.path)
